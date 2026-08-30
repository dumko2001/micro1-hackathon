#!/bin/sh
set -eu

cd /app/prometheus
git apply --check /solution/fix.patch
git apply /solution/fix.patch
gofmt -w tsdb/head.go
go test ./tsdb -run 'TestCompactStaleHead_EvictedSeriesRecordKeptInCheckpoint' -count=1
