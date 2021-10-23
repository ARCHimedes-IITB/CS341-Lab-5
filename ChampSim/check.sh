#!/bin/bash

./build_champsim.sh bimodal no no no no lru 1
./run_champsim.sh bimodal-no-no-no-no-lru-1core 1 1 trace.champsimtrace.xz
