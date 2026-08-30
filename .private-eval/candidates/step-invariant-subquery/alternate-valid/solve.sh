#!/bin/sh
set -eu
repo=${1:-/app/prometheus}
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
patch="$here/fix.patch"
git -C "$repo" apply --check "$patch"
git -C "$repo" apply "$patch"
