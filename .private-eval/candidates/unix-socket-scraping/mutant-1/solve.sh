#!/bin/sh
set -eu
repo=${1:-/app/prometheus}
solution=${MICRO1_REFERENCE_SOLUTION:?}
git -C "$repo" apply --check "$solution/fix.patch"
git -C "$repo" apply "$solution/fix.patch"
