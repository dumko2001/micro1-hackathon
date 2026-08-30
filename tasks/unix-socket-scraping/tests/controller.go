package main

import (
	"context"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"math/big"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync/atomic"
	"syscall"
	"time"
)

const candidateUID = 65532

type apiResponse struct {
	Status string `json:"status"`
	Data   struct {
		Result []struct {
			Metric map[string]string `json:"metric"`
			Value  []any             `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

type endpoint struct {
	server   *http.Server
	listener net.Listener
	hits     atomic.Int64
	accepts  atomic.Int64
	closes   atomic.Int64
	badHost  atomic.Bool
}

type countingListener struct {
	net.Listener
	accepts *atomic.Int64
}

func (l *countingListener) Accept() (net.Conn, error) {
	conn, err := l.Listener.Accept()
	if err == nil {
		l.accepts.Add(1)
	}
	return conn, err
}

func token() string {
	b := make([]byte, 12)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return hex.EncodeToString(b)
}

func serve(listener net.Listener, host, metric, origin string, tlsConfig *tls.Config) *endpoint {
	e := &endpoint{listener: listener}
	e.server = &http.Server{Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		e.hits.Add(1)
		if r.Host != host {
			e.badHost.Store(true)
			http.Error(w, "wrong authority", http.StatusMisdirectedRequest)
			return
		}
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		fmt.Fprintf(w, "%s{origin=%q} 1\n", metric, origin)
	}), ConnState: func(_ net.Conn, state http.ConnState) {
		if state == http.StateClosed || state == http.StateHijacked {
			e.closes.Add(1)
		}
	}}
	listener = &countingListener{Listener: listener, accepts: &e.accepts}
	if tlsConfig != nil {
		listener = tls.NewListener(listener, tlsConfig)
	}
	go func() { _ = e.server.Serve(listener) }()
	return e
}

func unixEndpoint(dir, name, host, metric, origin string, tlsConfig *tls.Config) (*endpoint, string, error) {
	path := filepath.Join(dir, name)
	listener, err := net.Listen("unix", path)
	if err != nil {
		return nil, "", err
	}
	if err := os.Chmod(path, 0o777); err != nil {
		_ = listener.Close()
		return nil, "", err
	}
	return serve(listener, host, metric, origin, tlsConfig), path, nil
}

func certificate(dir string) (*tls.Config, string, error) {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return nil, "", err
	}
	now := time.Now()
	template := &x509.Certificate{
		SerialNumber:          big.NewInt(now.UnixNano()),
		Subject:               pkix.Name{CommonName: "localhost"},
		DNSNames:              []string{"localhost"},
		NotBefore:             now.Add(-time.Minute),
		NotAfter:              now.Add(time.Hour),
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageKeyEncipherment | x509.KeyUsageCertSign,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		IsCA:                  true,
		BasicConstraintsValid: true,
	}
	der, err := x509.CreateCertificate(rand.Reader, template, template, &key.PublicKey, key)
	if err != nil {
		return nil, "", err
	}
	certPath := filepath.Join(dir, "ca.pem")
	keyPath := filepath.Join(dir, "server-key.pem")
	if err := os.WriteFile(certPath, pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der}), 0o644); err != nil {
		return nil, "", err
	}
	if err := os.WriteFile(keyPath, pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)}), 0o600); err != nil {
		return nil, "", err
	}
	pair, err := tls.LoadX509KeyPair(certPath, keyPath)
	if err != nil {
		return nil, "", err
	}
	return &tls.Config{Certificates: []tls.Certificate{pair}, MinVersion: tls.VersionTLS12}, certPath, nil
}

func reservePort() (int, error) {
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return 0, err
	}
	port := l.Addr().(*net.TCPAddr).Port
	return port, l.Close()
}

func writeConfig(path, authority, fallbackAuthority, caPath, socketA, socketB, socketTLS, socketEmpty, reloadSocket, tcpAuthority string) error {
	config := fmt.Sprintf(`global:
  scrape_interval: 200ms
  scrape_timeout: 150ms
scrape_configs:
- job_name: uds_http
  static_configs:
  - targets: [%q]
    labels: {__unix_socket__: %q, target_slot: "a"}
  - targets: [%q]
    labels: {__unix_socket__: %q, target_slot: "b"}
- job_name: uds_tls
  scheme: https
  tls_config:
    ca_file: %q
  static_configs:
  - targets: [%q]
    labels: {__unix_socket__: %q, target_slot: "tls"}
- job_name: uds_missing
  static_configs:
  - targets: [%q]
    labels: {__unix_socket__: %q, target_slot: "missing"}
- job_name: uds_empty_address
  static_configs:
  - targets: ["discard.invalid:80"]
    labels: {__unix_socket__: %q, target_slot: "empty"}
  relabel_configs:
  - target_label: __address__
    replacement: ""
- job_name: uds_reload
  static_configs:
  - targets: [%q]
    labels: {__unix_socket__: %q, target_slot: "reload"}
- job_name: tcp_control
  static_configs:
  - targets: [%q]
`, authority, socketA, authority, socketB, caPath, authority, socketTLS,
		fallbackAuthority, filepath.Join(filepath.Dir(socketA), "absent.sock"), socketEmpty, authority, reloadSocket, tcpAuthority)
	return os.WriteFile(path, []byte(config), 0o644)
}

func waitHTTP(endpoint string, deadline time.Time) error {
	for time.Now().Before(deadline) {
		resp, err := http.Get(endpoint)
		if err == nil {
			_, _ = io.Copy(io.Discard, resp.Body)
			_ = resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				return nil
			}
		}
		time.Sleep(50 * time.Millisecond)
	}
	return fmt.Errorf("endpoint did not become ready: %s", endpoint)
}

func query(base, expression string) (apiResponse, error) {
	var decoded apiResponse
	endpoint := base + "/api/v1/query?query=" + url.QueryEscape(expression)
	resp, err := http.Get(endpoint)
	if err != nil {
		return decoded, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
		return decoded, fmt.Errorf("query status %d: %s", resp.StatusCode, body)
	}
	if err := json.NewDecoder(resp.Body).Decode(&decoded); err != nil {
		return decoded, err
	}
	if decoded.Status != "success" {
		return decoded, errors.New("query failed")
	}
	return decoded, nil
}

func waitSeries(base, expression string, want map[string]string, deadline time.Time) error {
	for time.Now().Before(deadline) {
		response, err := query(base, expression)
		if err == nil {
			for _, result := range response.Data.Result {
				matches := true
				for key, value := range want {
					if result.Metric[key] != value {
						matches = false
					}
				}
				if matches {
					return nil
				}
			}
		}
		time.Sleep(100 * time.Millisecond)
	}
	return fmt.Errorf("series not observed for %s with %v", expression, want)
}

func observeFailClosed(base, expression string, duration time.Duration) error {
	deadline := time.Now().Add(duration)
	for time.Now().Before(deadline) {
		response, err := query(base, expression)
		if err != nil {
			return err
		}
		switch len(response.Data.Result) {
		case 0:
		case 1:
			if len(response.Data.Result[0].Value) != 2 {
				return fmt.Errorf("unexpected scalar result for %s", expression)
			}
			text, ok := response.Data.Result[0].Value[1].(string)
			if !ok {
				return fmt.Errorf("unexpected value encoding for %s", expression)
			}
			value, err := strconv.ParseFloat(text, 64)
			if err != nil {
				return err
			}
			if value != 0 {
				return fmt.Errorf("unexpected nonzero value for %s: %v", expression, value)
			}
		default:
			return fmt.Errorf("unexpected result count for %s: %d", expression, len(response.Data.Result))
		}
		time.Sleep(100 * time.Millisecond)
	}
	return nil
}

func waitConnectionsClosed(endpoint *endpoint, deadline time.Time) error {
	for time.Now().Before(deadline) {
		if endpoint.accepts.Load() > 0 && endpoint.closes.Load() >= endpoint.accepts.Load() {
			return nil
		}
		time.Sleep(50 * time.Millisecond)
	}
	return fmt.Errorf("retired scrape transport left %d of %d connections open", endpoint.accepts.Load()-endpoint.closes.Load(), endpoint.accepts.Load())
}

func main() {
	if len(os.Args) != 3 {
		panic("usage: controller PROMETHEUS RUNTIME")
	}
	candidate, runtime := os.Args[1], os.Args[2]
	launcher := os.Getenv("MICRO1_CANDIDATE_LAUNCHER")
	if launcher == "" {
		panic("candidate launcher is unavailable")
	}
	controllerDir, err := os.MkdirTemp("", "micro1-uds-controller-")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(controllerDir)
	if err := os.Chmod(controllerDir, 0o755); err != nil {
		panic(err)
	}
	if err := os.MkdirAll(runtime, 0o755); err != nil {
		panic(err)
	}
	if err := os.Chown(runtime, candidateUID, candidateUID); err != nil {
		panic(err)
	}

	fallbackListener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}
	fallbackAuthority := "localhost:" + strconv.Itoa(fallbackListener.Addr().(*net.TCPAddr).Port)
	fallbackOrigin := token()
	fallback := serve(fallbackListener, fallbackAuthority, "micro1_fallback_probe", fallbackOrigin, nil)
	defer fallback.server.Close()

	tcpListener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}
	tcpAuthority := "localhost:" + strconv.Itoa(tcpListener.Addr().(*net.TCPAddr).Port)
	tcpOrigin := token()
	tcp := serve(tcpListener, tcpAuthority, "micro1_tcp_control", tcpOrigin, nil)
	defer tcp.server.Close()

	origins := []string{token(), token(), token(), token(), token(), token()}
	httpA, socketA, err := unixEndpoint(controllerDir, "a.sock", tcpAuthority, "micro1_uds_probe", origins[0], nil)
	if err != nil {
		panic(err)
	}
	httpB, socketB, err := unixEndpoint(controllerDir, "b.sock", tcpAuthority, "micro1_uds_probe", origins[1], nil)
	if err != nil {
		panic(err)
	}
	tlsConfig, caPath, err := certificate(controllerDir)
	if err != nil {
		panic(err)
	}
	httpsEndpoint, socketTLS, err := unixEndpoint(controllerDir, "tls.sock", tcpAuthority, "micro1_tls_probe", origins[2], tlsConfig)
	if err != nil {
		panic(err)
	}
	emptyAddress, socketEmpty, err := unixEndpoint(controllerDir, "empty.sock", "localhost", "micro1_empty_address_probe", origins[3], nil)
	if err != nil {
		panic(err)
	}
	reloadA, reloadSocketA, err := unixEndpoint(controllerDir, "reload-a.sock", tcpAuthority, "micro1_reload_probe", origins[4], nil)
	if err != nil {
		panic(err)
	}
	reloadB, reloadSocketB, err := unixEndpoint(controllerDir, "reload-b.sock", tcpAuthority, "micro1_reload_probe", origins[5], nil)
	if err != nil {
		panic(err)
	}
	for _, e := range []*endpoint{httpA, httpB, httpsEndpoint, emptyAddress, reloadA, reloadB} {
		defer e.server.Close()
	}

	configPath := filepath.Join(controllerDir, "prometheus.yml")
	if err := writeConfig(configPath, tcpAuthority, fallbackAuthority, caPath, socketA, socketB, socketTLS, socketEmpty, reloadSocketA, tcpAuthority); err != nil {
		panic(err)
	}
	port, err := reservePort()
	if err != nil {
		panic(err)
	}
	base := fmt.Sprintf("http://127.0.0.1:%d", port)
	cmd := exec.Command(launcher, candidate, runtime,
		"--config.file="+configPath,
		"--storage.tsdb.path="+filepath.Join(runtime, "data"),
		"--web.listen-address=127.0.0.1:"+strconv.Itoa(port),
		"--web.enable-lifecycle", "--log.level=error")
	cmd.Stdout, cmd.Stderr = os.Stderr, os.Stderr
	if err := cmd.Start(); err != nil {
		panic(err)
	}
	defer func() {
		_ = cmd.Process.Signal(syscall.SIGTERM)
		done := make(chan struct{})
		go func() { _ = cmd.Wait(); close(done) }()
		select {
		case <-done:
		case <-time.After(2 * time.Second):
			_ = cmd.Process.Kill()
		}
	}()

	deadline := time.Now().Add(20 * time.Second)
	if err := waitHTTP(base+"/-/ready", deadline); err != nil {
		panic(err)
	}
	checks := []struct {
		expression string
		want       map[string]string
	}{
		{`micro1_uds_probe{target_slot="a"}`, map[string]string{"origin": origins[0], "target_slot": "a"}},
		{`micro1_uds_probe{target_slot="b"}`, map[string]string{"origin": origins[1], "target_slot": "b"}},
		{`micro1_tls_probe{target_slot="tls"}`, map[string]string{"origin": origins[2], "target_slot": "tls"}},
		{`micro1_empty_address_probe{target_slot="empty"}`, map[string]string{"origin": origins[3], "target_slot": "empty"}},
		{`micro1_tcp_control`, map[string]string{"origin": tcpOrigin, "job": "tcp_control"}},
	}
	for _, check := range checks {
		if err := waitSeries(base, check.expression, check.want, deadline); err != nil {
			panic(err)
		}
	}
	if err := observeFailClosed(base, `up{job="uds_missing"}`, 2*time.Second); err != nil {
		panic(fmt.Sprintf("missing socket did not fail closed: %v", err))
	}
	if fallback.hits.Load() != 0 {
		panic(fmt.Sprintf("Unix socket failure fell back to TCP (%d requests)", fallback.hits.Load()))
	}
	for name, endpoint := range map[string]*endpoint{
		"http-a": httpA,
		"http-b": httpB,
		"https":  httpsEndpoint,
		"empty":  emptyAddress,
		"reload": reloadA,
	} {
		if endpoint.hits.Load() < 3 {
			panic(fmt.Sprintf("%s did not complete enough repeated scrapes to prove pooling", name))
		}
		if endpoint.accepts.Load() >= endpoint.hits.Load() {
			panic(fmt.Sprintf("%s opened a fresh connection for every scrape instead of reusing its pool", name))
		}
	}
	if httpA.badHost.Load() || httpB.badHost.Load() || httpsEndpoint.badHost.Load() || emptyAddress.badHost.Load() || reloadA.badHost.Load() {
		panic("Unix-socket scrape used the wrong HTTP authority")
	}

	if err := writeConfig(configPath, tcpAuthority, fallbackAuthority, caPath, socketA, socketB, socketTLS, socketEmpty, reloadSocketB, tcpAuthority); err != nil {
		panic(err)
	}
	reloadRequest, _ := http.NewRequestWithContext(context.Background(), http.MethodPost, base+"/-/reload", strings.NewReader(""))
	reloadResponse, err := http.DefaultClient.Do(reloadRequest)
	if err != nil {
		panic(err)
	}
	_, _ = io.Copy(io.Discard, reloadResponse.Body)
	_ = reloadResponse.Body.Close()
	if reloadResponse.StatusCode != http.StatusOK {
		panic("configuration reload failed")
	}
	if err := waitSeries(base, `micro1_reload_probe{target_slot="reload"}`, map[string]string{"origin": origins[5]}, time.Now().Add(10*time.Second)); err != nil {
		panic(err)
	}
	if err := waitConnectionsClosed(reloadA, time.Now().Add(5*time.Second)); err != nil {
		panic(err)
	}
	if reloadB.badHost.Load() || fallback.hits.Load() != 0 {
		panic("reload broke authority isolation or used TCP fallback")
	}
}
