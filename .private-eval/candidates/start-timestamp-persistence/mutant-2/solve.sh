#!/bin/sh
set -eu
cd /app/prometheus
git apply "$MICRO1_REFERENCE_SOLUTION/fix.patch"
git apply /tmp/micro1-candidate-fixture/fix.patch
