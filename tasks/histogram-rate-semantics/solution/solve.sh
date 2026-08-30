#!/bin/sh
set -eu

cd /app/prometheus
git apply --check /solution/fix.patch
git apply /solution/fix.patch
git apply --check /solution/fix-18943.patch
git apply /solution/fix-18943.patch
gofmt -w promql/engine.go promql/functions.go promql/functions_internal_test.go
go test ./promql/... -run 'TestEvaluations|TestInterpolateHistograms' -count=1
