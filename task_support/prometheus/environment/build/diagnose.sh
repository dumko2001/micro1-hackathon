#!/bin/sh
set -eu

cd "${PROMETHEUS_ROOT:-/app/prometheus}"
printf 'go=' && go version
printf 'archive_sha256=' && cat /opt/prometheus-input/PROMETHEUS_SOURCE_SHA256
printf 'prewarm_packages=' && tr '\n' ' ' < /opt/prometheus-input/PREWARM_PACKAGES && printf '\n'
printf 'module=' && go list -m
