#!/bin/sh
set -eu

input_dir=$1
destination=$2
manifest="$input_dir/SOURCE.SHA256SUMS"

test -f "$manifest"
test -s "$input_dir/PREWARM_PACKAGES"
archive="$input_dir/prometheus-source.tar.gz"
archive_name=$(basename "$archive")
expected_sha=$(awk -v name="$archive_name" '$2 == name {print $1}' "$manifest")

set -- "$input_dir"/*.tar.gz
test "$#" -eq 1
test "$1" = "$archive"
test -f "$archive"
test -n "$expected_sha"
actual_sha=$(sha256sum "$archive" | awk '{print $1}')
test "$actual_sha" = "$expected_sha"

mkdir -p "$destination"
tar -xzf "$archive" -C "$destination" --strip-components=1
test -f "$destination/go.mod"
test -f "$destination/go.sum"
test -f "$destination/promql/engine.go"
test ! -e "$destination/.git"

printf '%s\n' "$actual_sha" > /opt/prometheus-input/PROMETHEUS_SOURCE_SHA256
