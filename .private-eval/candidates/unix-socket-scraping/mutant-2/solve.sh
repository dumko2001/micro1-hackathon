#!/bin/sh
set -eu

repo=${1:-/app/prometheus}
solution=${MICRO1_REFERENCE_SOLUTION:?}
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
git -C "$repo" apply --check "$solution/fix.patch"
git -C "$repo" apply "$solution/fix.patch"
git -C "$repo" apply --check "$solution/fix-isolation.patch"
git -C "$repo" apply "$solution/fix-isolation.patch"
git -C "$repo" apply --check "$here/defect.patch"
git -C "$repo" apply "$here/defect.patch"
