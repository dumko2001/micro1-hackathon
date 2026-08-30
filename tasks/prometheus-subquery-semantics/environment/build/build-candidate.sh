#!/bin/sh
set -eu

cd "${PROMETHEUS_ROOT:-/app/prometheus}"
xargs go test < /opt/prometheus-input/PREWARM_PACKAGES
mkdir -p /app/bin
go build -trimpath -buildvcs=false -o /app/bin/prometheus ./cmd/prometheus
/app/bin/prometheus --version
