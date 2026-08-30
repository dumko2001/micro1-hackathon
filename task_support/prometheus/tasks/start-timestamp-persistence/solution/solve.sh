#!/bin/sh
set -eu

cd /app/prometheus
trap 'rm -f /app/prometheus/go.work.sum' EXIT
git apply --check /solution/fix.patch
git apply /solution/fix.patch
gofmt -w cmd/prometheus/main.go cmd/promtool/tsdb.go storage tsdb promql/promqltest
go test ./tsdb/chunkenc ./tsdb ./promql/promqltest -count=1
GOMAXPROCS=2 go build -p=1 -trimpath -buildvcs=false -o /app/bin/promtool ./cmd/promtool
