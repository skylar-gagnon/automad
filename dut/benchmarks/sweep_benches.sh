#!/bin/bash

NAMES=(
        "perlbench"
        "bzip2"
        "gcc"
        "mcf"
        "gobmk"
        "hmmer"
        "sjeng"
        "libquantum"
        "h264ref"
        "omnetpp"
        "astar"
        "bwaves"
        "gamess"
        "milc"
        "zeusmp"
        "gomacs"
        "cactusADM"
        "leslie3d"
        "namd"
        "soplex"
        "povray"
        "calculix"
        "GemsFDTD"
        "tonto"
        "lbm"
)

source ./shrc

for NAME in "${NAMES[@]}"; do
        touch curr2_log
        ./monitor & runspec --iterations 1 --config ubuntu_aarch64.cfg $NAME;
        # ./monitor & timeout 10s runspec --iterations 1 --config ubuntu_aarch64.cfg $NAME;
        killall monitor
        killall runspec
        killall specinvoke
        killall ${NAME}_base.ubuntu_aarch64
        sleep 0.1s
        mv curr2_log measurements/full_run/$NAME
        # mv curr2_log measurements/10s/$NAME
done