package main

import (
	"context"
	"crypto/rand"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/prometheus/prometheus/model/histogram"
	"github.com/prometheus/prometheus/model/labels"
	"github.com/prometheus/prometheus/storage"
	"github.com/prometheus/prometheus/tsdb"
	"github.com/prometheus/prometheus/tsdb/tsdbutil"
)

const candidateUID = 65532

type queryResponse struct {
	Status    string          `json:"status"`
	Data      json.RawMessage `json:"data"`
	ErrorType string          `json:"errorType"`
	Error     string          `json:"error"`
	Warnings  []string        `json:"warnings"`
}

func randomScale() int64 {
	var value uint64
	if err := binary.Read(rand.Reader, binary.LittleEndian, &value); err != nil {
		panic(err)
	}
	return int64(value%5) + 1
}

func reservePort() (int, error) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return 0, err
	}
	port := listener.Addr().(*net.TCPAddr).Port
	return port, listener.Close()
}

func chownTree(root string) error {
	return filepath.Walk(root, func(path string, _ os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		return os.Chown(path, candidateUID, candidateUID)
	})
}

func waitReady(endpoint string, deadline time.Time) error {
	for time.Now().Before(deadline) {
		response, err := http.Get(endpoint)
		if err == nil {
			_, _ = io.Copy(io.Discard, response.Body)
			_ = response.Body.Close()
			if response.StatusCode == http.StatusOK {
				return nil
			}
		}
		time.Sleep(50 * time.Millisecond)
	}
	return fmt.Errorf("Prometheus did not become ready")
}

func query(base, expression, at string) (queryResponse, error) {
	var decoded queryResponse
	parameters := url.Values{"query": {expression}, "time": {at}}
	response, err := http.Get(base + "/api/v1/query?" + parameters.Encode())
	if err != nil {
		return decoded, err
	}
	defer response.Body.Close()
	body, err := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	if err != nil {
		return decoded, err
	}
	if err := json.Unmarshal(body, &decoded); err != nil {
		return decoded, fmt.Errorf("invalid API response: %w", err)
	}
	if response.StatusCode != http.StatusOK || decoded.Status != "success" {
		return decoded, fmt.Errorf("query failed (%s): %s", decoded.ErrorType, decoded.Error)
	}
	return decoded, nil
}

func queryRange(base, expression, start, end, step string) (queryResponse, error) {
	var decoded queryResponse
	parameters := url.Values{
		"query": {expression}, "start": {start}, "end": {end}, "step": {step},
	}
	response, err := http.Get(base + "/api/v1/query_range?" + parameters.Encode())
	if err != nil {
		return decoded, err
	}
	defer response.Body.Close()
	body, err := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	if err != nil {
		return decoded, err
	}
	if err := json.Unmarshal(body, &decoded); err != nil {
		return decoded, err
	}
	if response.StatusCode != http.StatusOK || decoded.Status != "success" {
		return decoded, fmt.Errorf("query failed (%s): %s", decoded.ErrorType, decoded.Error)
	}
	return decoded, nil
}

func canonical(raw json.RawMessage) (any, error) {
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return nil, err
	}
	return value, nil
}

func equivalent(left, right any) bool {
	switch left := left.(type) {
	case map[string]any:
		right, ok := right.(map[string]any)
		if !ok || len(left) != len(right) {
			return false
		}
		for key, value := range left {
			other, ok := right[key]
			if !ok || !equivalent(value, other) {
				return false
			}
		}
		return true
	case []any:
		right, ok := right.([]any)
		if !ok || len(left) != len(right) {
			return false
		}
		for index := range left {
			if !equivalent(left[index], right[index]) {
				return false
			}
		}
		return true
	case string:
		right, ok := right.(string)
		if !ok {
			return false
		}
		if left == right {
			return true
		}
		leftNumber, leftErr := strconv.ParseFloat(left, 64)
		rightNumber, rightErr := strconv.ParseFloat(right, 64)
		if leftErr != nil || rightErr != nil {
			return false
		}
		if math.IsNaN(leftNumber) || math.IsNaN(rightNumber) {
			return math.IsNaN(leftNumber) && math.IsNaN(rightNumber)
		}
		if math.IsInf(leftNumber, 0) || math.IsInf(rightNumber, 0) {
			return leftNumber == rightNumber
		}
		tolerance := 1e-12 * math.Max(1, math.Max(math.Abs(leftNumber), math.Abs(rightNumber)))
		return math.Abs(leftNumber-rightNumber) <= tolerance
	default:
		return reflect.DeepEqual(left, right)
	}
}

func requireSame(name string, histogramResult, floatResult queryResponse) error {
	histogramData, err := canonical(histogramResult.Data)
	if err != nil {
		return err
	}
	floatData, err := canonical(floatResult.Data)
	if err != nil {
		return err
	}
	if !equivalent(histogramData, floatData) {
		return fmt.Errorf("%s diverged from the float control\nhistogram: %s\nfloat: %s", name, histogramResult.Data, floatResult.Data)
	}
	var decoded struct {
		Result []any `json:"result"`
	}
	if err := json.Unmarshal(histogramResult.Data, &decoded); err != nil {
		return err
	}
	if len(decoded.Result) == 0 {
		return fmt.Errorf("%s returned no series", name)
	}
	return nil
}

func requireWarning(name string, response queryResponse, fragment string) error {
	var decoded struct {
		Result []any `json:"result"`
	}
	if err := json.Unmarshal(response.Data, &decoded); err != nil {
		return err
	}
	if len(decoded.Result) != 0 {
		return fmt.Errorf("%s retained an invalid mixed series", name)
	}
	for _, warning := range response.Warnings {
		if strings.Contains(warning, fragment) {
			return nil
		}
	}
	return fmt.Errorf("%s omitted the expected warning: %v", name, response.Warnings)
}

func appendPair(app storage.Appender, histogramName, floatName, sumName, caseName string, timestamp int64, h *histogram.Histogram) error {
	caseLabels := []string{"case", caseName}
	if _, err := app.AppendHistogram(0, labels.FromStrings(append([]string{labels.MetricName, histogramName}, caseLabels...)...), timestamp, h, nil); err != nil {
		return err
	}
	if _, err := app.Append(0, labels.FromStrings(append([]string{labels.MetricName, floatName}, caseLabels...)...), timestamp, float64(h.Count)); err != nil {
		return err
	}
	if sumName != "" {
		if _, err := app.Append(0, labels.FromStrings(append([]string{labels.MetricName, sumName}, caseLabels...)...), timestamp, h.Sum); err != nil {
			return err
		}
	}
	return nil
}

func populate(path string, base int64, scale int64) error {
	options := tsdb.DefaultOptions()
	options.MinBlockDuration = int64(24 * time.Hour / time.Millisecond)
	options.MaxBlockDuration = options.MinBlockDuration
	options.RetentionDuration = int64(30 * 24 * time.Hour / time.Millisecond)
	database, err := tsdb.Open(path, nil, nil, options, tsdb.NewDBStats())
	if err != nil {
		return err
	}
	app := database.Appender(context.Background())
	for i := int64(0); i < 8; i++ {
		h := tsdbutil.GenerateTestHistogram((i + 2) * scale)
		if i > 0 {
			h.CounterResetHint = histogram.NotCounterReset
		}
		if err := appendPair(app, "hist_counter", "float_counter", "float_counter_sum", "monotonic", base+i*15_000, h); err != nil {
			return err
		}

		custom := tsdbutil.GenerateTestCustomBucketsHistogram((i + 1) * scale)
		if i > 0 {
			custom.CounterResetHint = histogram.NotCounterReset
		}
		if err := appendPair(app, "custom_counter", "custom_float_counter", "custom_float_sum", "custom", base+i*15_000, custom); err != nil {
			return err
		}
	}
	resetValues := []int64{5, 10, 3, 7}
	for i, value := range resetValues {
		h := tsdbutil.GenerateTestHistogram(value * scale)
		if i == 2 {
			h.CounterResetHint = histogram.CounterReset
		} else if i > 0 {
			h.CounterResetHint = histogram.NotCounterReset
		}
		if err := appendPair(app, "reset_counter", "reset_float_counter", "", "reset", base+int64(i)*30_000, h); err != nil {
			return err
		}
	}
	for i, value := range []int64{10, 4} {
		h := tsdbutil.GenerateTestGaugeHistogram(value * scale)
		if err := appendPair(app, "gauge_hist", "gauge_float", "", "gauge", base+int64(i)*30_000, h); err != nil {
			return err
		}
	}
	compatibleA := tsdbutil.GenerateTestHistogram(2 * scale)
	compatibleB := tsdbutil.GenerateTestHistogram(5 * scale)
	compatibleB.CounterResetHint = histogram.NotCounterReset
	if err := compatibleB.ReduceResolution(0); err != nil {
		return err
	}
	if err := appendPair(app, "compatible_hist", "compatible_float", "", "compatible", base, compatibleA); err != nil {
		return err
	}
	if err := appendPair(app, "compatible_hist", "compatible_float", "", "compatible", base+30_000, compatibleB); err != nil {
		return err
	}
	if err := app.Commit(); err != nil {
		return err
	}

	incompatibleLabels := labels.FromStrings(labels.MetricName, "incompatible_hist", "case", "mixed-schema")
	app = database.Appender(context.Background())
	if _, err := app.AppendHistogram(0, incompatibleLabels, base, tsdbutil.GenerateTestHistogram(scale), nil); err != nil {
		return err
	}
	if _, err := app.AppendHistogram(0, incompatibleLabels, base+30_000, tsdbutil.GenerateTestCustomBucketsHistogram(2*scale), nil); err != nil {
		return err
	}
	if err := app.Commit(); err != nil {
		return err
	}

	mixedLabels := labels.FromStrings(labels.MetricName, "mixed_types", "case", "mixed-types")
	app = database.Appender(context.Background())
	if _, err := app.Append(0, mixedLabels, base, float64(scale)); err != nil {
		return err
	}
	if _, err := app.Append(0, mixedLabels, base+15_000, float64(2*scale)); err != nil {
		return err
	}
	if err := app.Commit(); err != nil {
		return err
	}
	app = database.Appender(context.Background())
	if _, err := app.AppendHistogram(0, mixedLabels, base+30_000, tsdbutil.GenerateTestHistogram(3*scale), nil); err != nil {
		return err
	}
	if _, err := app.AppendHistogram(0, mixedLabels, base+45_000, tsdbutil.GenerateTestHistogram(4*scale), nil); err != nil {
		return err
	}
	if err := app.Commit(); err != nil {
		return err
	}
	return database.Close()
}

func main() {
	if len(os.Args) != 4 {
		panic("usage: controller PROMETHEUS RUNTIME CONFIG")
	}
	candidate, runtime, config := os.Args[1], os.Args[2], os.Args[3]
	launcher := os.Getenv("MICRO1_CANDIDATE_LAUNCHER")
	if launcher == "" {
		panic("candidate launcher is unavailable")
	}
	dataPath := filepath.Join(runtime, "data")
	if err := os.MkdirAll(runtime, 0o755); err != nil {
		panic(err)
	}
	base := time.Now().Add(-24 * time.Hour).UnixMilli()
	base -= base % 30_000
	if err := populate(dataPath, base, randomScale()); err != nil {
		panic(fmt.Sprintf("trusted fixture generation failed: %v", err))
	}
	if err := chownTree(runtime); err != nil {
		panic(err)
	}

	port, err := reservePort()
	if err != nil {
		panic(err)
	}
	baseURL := fmt.Sprintf("http://127.0.0.1:%d", port)
	command := exec.Command(launcher, candidate, runtime,
		"--config.file="+config,
		"--storage.tsdb.path="+dataPath,
		"--storage.tsdb.retention.time=30d",
		"--web.listen-address=127.0.0.1:"+strconv.Itoa(port),
		"--enable-feature=promql-extended-range-selectors",
		"--log.level=error")
	command.Stdout, command.Stderr = os.Stderr, os.Stderr
	if err := command.Start(); err != nil {
		panic(err)
	}
	defer func() {
		_ = command.Process.Signal(syscall.SIGTERM)
		done := make(chan struct{})
		go func() { _ = command.Wait(); close(done) }()
		select {
		case <-done:
		case <-time.After(2 * time.Second):
			_ = command.Process.Kill()
		}
	}()
	if err := waitReady(baseURL+"/-/ready", time.Now().Add(20*time.Second)); err != nil {
		panic(err)
	}

	at := func(offsetSeconds int64) string {
		return strconv.FormatFloat(float64(base)/1000+float64(offsetSeconds), 'f', 3, 64)
	}
	comparisons := []struct {
		name, histogramExpression, floatExpression string
		offset                                     int64
	}{
		{"anchored increase", "histogram_count(increase(hist_counter[60s] anchored))", "increase(float_counter[60s] anchored)", 50},
		{"anchored rate", "histogram_count(rate(hist_counter[60s] anchored))", "rate(float_counter[60s] anchored)", 50},
		{"smoothed increase", "histogram_count(increase(hist_counter[60s] smoothed))", "increase(float_counter[60s] smoothed)", 50},
		{"smoothed rate", "histogram_count(rate(hist_counter[60s] smoothed))", "rate(float_counter[60s] smoothed)", 50},
		{"anchored sum", "histogram_sum(increase(hist_counter[60s] anchored))", "increase(float_counter_sum[60s] anchored)", 50},
		{"custom buckets", "histogram_count(increase(custom_counter[60s] smoothed))", "increase(custom_float_counter[60s] smoothed)", 50},
		{"custom bucket sum", "histogram_sum(increase(custom_counter[60s] smoothed))", "increase(custom_float_sum[60s] smoothed)", 50},
		{"counter reset anchored", "histogram_count(increase(reset_counter[60s] anchored))", "increase(reset_float_counter[60s] anchored)", 60},
		{"counter reset smoothed", "histogram_count(rate(reset_counter[60s] smoothed))", "rate(reset_float_counter[60s] smoothed)", 60},
		{"gauge delta", "histogram_count(delta(gauge_hist[30s] anchored))", "delta(gauge_float[30s] anchored)", 30},
		{"compatible schemas", "histogram_count(increase(compatible_hist[30s] anchored))", "increase(compatible_float[30s] anchored)", 30},
		{"smoothed selector", "histogram_count(hist_counter smoothed)", "(float_counter smoothed) + 0", 7},
	}
	for _, comparison := range comparisons {
		histogramResult, err := query(baseURL, comparison.histogramExpression, at(comparison.offset))
		if err != nil {
			panic(fmt.Sprintf("%s histogram query: %v", comparison.name, err))
		}
		floatResult, err := query(baseURL, comparison.floatExpression, at(comparison.offset))
		if err != nil {
			panic(fmt.Sprintf("%s float control: %v", comparison.name, err))
		}
		if err := requireSame(comparison.name, histogramResult, floatResult); err != nil {
			panic(err)
		}
	}
	histogramRange, err := queryRange(baseURL, "histogram_count(rate(hist_counter[60s] smoothed))", at(0), at(60), "15")
	if err != nil {
		panic(err)
	}
	floatRange, err := queryRange(baseURL, "rate(float_counter[60s] smoothed)", at(0), at(60), "15")
	if err != nil {
		panic(err)
	}
	if err := requireSame("range evaluation", histogramRange, floatRange); err != nil {
		panic(err)
	}

	incompatible, err := query(baseURL, "rate(incompatible_hist[60s] smoothed)", at(45))
	if err != nil {
		panic(fmt.Sprintf("incompatible schema query: %v", err))
	}
	if err := requireWarning("incompatible schemas", incompatible, "mix of histograms with exponential and custom buckets schemas"); err != nil {
		panic(err)
	}
	for _, expression := range []string{"mixed_types smoothed", "sort(mixed_types smoothed)"} {
		mixed, err := query(baseURL, expression, at(45))
		if err != nil {
			panic(fmt.Sprintf("mixed sample query %q: %v", expression, err))
		}
		if err := requireWarning(expression, mixed, "mix of histograms and floats"); err != nil {
			panic(err)
		}
	}
}
