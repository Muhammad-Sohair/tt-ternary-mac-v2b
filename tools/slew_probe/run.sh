#!/bin/bash
# Run probe.tcl on a downloaded GDS_logs run directory, with the CI's exact LibreLane image.
# usage (inside WSL, Docker engine running): run.sh MODE RUN_ROOT PDK_ROOT OUT_DIR
#   MODE      pre | grt | rcx   (see probe.tcl)
#   RUN_ROOT  directory that contains runs/wokwi/ (mounted at the CI's checkout path)
#   PDK_ROOT  ciel root holding ciel/sky130/versions/8afc8346... (mounted at the CI's ~/.ciel)
#   OUT_DIR   where out_<MODE>/ and log_<MODE>.txt are written
# The CI paths below are those of tt-ternary-mac-v2 run 40698174384; change them for another run.
set -e
MODE=$1; RUN_ROOT=$2; PDK_ROOT=$3; OUT=$4
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT/probe"
cp "$HERE/probe.tcl" "$OUT/probe/probe.tcl"
docker run --rm -e MODE=$MODE \
  -v "$RUN_ROOT":/home/runner/work/tt-ternary-mac-v2/tt-ternary-mac-v2 \
  -v "$PDK_ROOT":/home/runner/.ciel \
  -v "$OUT":/s \
  ghcr.io/librelane/librelane:3.0.14 \
  openroad -exit -no_splash /s/probe/probe.tcl > "$OUT/probe/log_$MODE.txt" 2>&1
