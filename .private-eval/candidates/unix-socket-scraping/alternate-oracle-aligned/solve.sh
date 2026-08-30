#!/bin/sh
set -eu

repo=${1:-/app/prometheus}
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

git -C "$repo" apply --check "$here/fix.patch"
git -C "$repo" apply "$here/fix.patch"
