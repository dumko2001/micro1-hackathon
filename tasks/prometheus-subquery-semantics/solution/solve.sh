#!/bin/sh
set -eu

cd /app/prometheus
git apply --check /solution/fix.patch
git apply /solution/fix.patch
gofmt -w promql/engine.go
go test ./promql/...
