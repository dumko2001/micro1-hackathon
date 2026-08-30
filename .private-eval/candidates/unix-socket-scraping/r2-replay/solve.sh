#!/bin/sh
set -eu

tar -xzf "$(dirname "$0")/candidate.tar.gz" --strip-components=1 -C /app/prometheus
