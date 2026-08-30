#!/bin/sh
set -eu

cd /app/prometheus
git apply --check /solution/fix.patch
git apply /solution/fix.patch
git apply --check /solution/fix-isolation.patch
git apply /solution/fix-isolation.patch
gofmt -w scrape/scrape.go scrape/target.go
go test ./scrape/...
