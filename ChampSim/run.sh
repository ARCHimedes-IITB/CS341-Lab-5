#!/bin/bash

BIN="bimodal-no-ip_stride-ip_stride-no-lru-1core"
RES=$1

./build_champsim.sh bimodal no ip_stride ip_stride no lru 1

./run_champsim.sh $BIN 10 10 trace.champsimtrace.xz

mv results_10M/*.txt ../results/prefetch_throttling_result/$1.txt