#!/bin/bash
# usage (WSL): replay.sh TAG MARGIN LRC LI1 [TIMEOUT_S]   -> logs to $HOME/replay_TAG.log
T=${5:-900}
timeout $T docker run --rm -e RUN=/work/runs/lrc1 -e MARGIN=$2 -e LRC=$3 -e LI1=$4 \
  -v $HOME/v2b_local:/work -v $HOME/pdk:/pdk -v "$(cd "$(dirname "$0")" && pwd)":/t \
  ghcr.io/librelane/librelane:3.0.14 openroad -exit -no_splash /t/replay_postgrt_repair.tcl > $HOME/replay_$1.log 2>&1
echo "$1 exit $?"
