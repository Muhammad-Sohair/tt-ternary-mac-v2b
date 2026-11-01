#!/bin/bash
# usage (WSL): estimate_caps.sh RUN_TAG LRC  -> $HOME/estcaps_RUN_TAG.log
docker run --rm -e RUN=/work/runs/$1 -e MARGIN=20 -e LRC=$2 -e LI1=0 \
  -v $HOME/v2b_local:/work -v $HOME/pdk:/pdk -v "$(cd "$(dirname "$0")" && pwd)":/t \
  ghcr.io/librelane/librelane:3.0.14 openroad -exit -no_splash /t/estimate_caps.tcl > $HOME/estcaps_$1.log 2>&1
echo "exit $?"; cp $HOME/v2b_local/runs/$1/final/spef/nom/*.spef $HOME/estcaps_$1.nom.spef
