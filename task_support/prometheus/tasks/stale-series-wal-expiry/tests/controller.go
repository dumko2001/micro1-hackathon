package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

func token() string {
	b := make([]byte, 12)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return hex.EncodeToString(b)
}

type readResult struct {
	Checkpoint map[string]bool `json:"checkpoint"`
	Queryable  map[string]bool `json:"queryable"`
}

func run(candidate, reader, selected, active string, maxt, target int64) readResult {
	root, err := os.MkdirTemp("/tmp/micro1-verifier-tmp", "wal-state-")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(root)
	if err := os.Chown(root, 65532, 65532); err != nil {
		panic(err)
	}
	launcher := os.Getenv("MICRO1_CANDIDATE_LAUNCHER")
	cmd := exec.Command(launcher, candidate, "/tmp/micro1-verifier-tmp", root, selected, active, fmt.Sprint(maxt), fmt.Sprint(target))
	if output, err := cmd.CombinedOutput(); err != nil {
		panic(fmt.Sprintf("candidate failed: %v: %s", err, output))
	}
	cmd = exec.Command(reader, root, selected, active)
	output, err := cmd.Output()
	if err != nil {
		panic(err)
	}
	result := readResult{}
	if err := json.Unmarshal(output, &result); err != nil {
		panic(err)
	}
	return result
}

func main() {
	if len(os.Args) != 3 {
		panic("invalid arguments")
	}
	candidate, err := filepath.Abs(os.Args[1])
	if err != nil {
		panic(err)
	}
	reader, err := filepath.Abs(os.Args[2])
	if err != nil {
		panic(err)
	}
	selected := "selected_" + token()
	active := "active_" + token()
	maxt := int64(10000 + int(token()[0]))

	atBoundary := run(candidate, reader, selected, active, maxt, maxt)
	if !atBoundary.Checkpoint[selected] || !atBoundary.Checkpoint[active] {
		panic("inclusive checkpoint boundary violated")
	}
	if !atBoundary.Queryable[selected] || !atBoundary.Queryable[active] {
		panic("clean-parent replay lost compacted or active data at the inclusive boundary")
	}
	afterBoundary := run(candidate, reader, selected, active, maxt, maxt+1)
	if afterBoundary.Checkpoint[selected] || !afterBoundary.Checkpoint[active] {
		panic("checkpoint expiry or active control violated")
	}
	if !afterBoundary.Queryable[selected] || !afterBoundary.Queryable[active] {
		panic("expiry removed compacted user data or the active control")
	}
}
