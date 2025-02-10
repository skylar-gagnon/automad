# This solution was found and adapted slightly from:
# https://github.com/rdolbeau/enable_arm_pmu
#!/bin/bash
CPU_CORES=$(nproc --all)
CPU_CORES=$(echo "$CPU_CORES - 1" | bc)

IDLE_STATES=$(ls /sys/devices/system/cpu/cpu0/cpuidle/ | grep state -c)
IDLE_STATES=$(echo "$IDLE_STATES - 1" | bc)

for X in $(seq 0 $CPU_CORES);
do
	for Y in $(seq 0 $IDLE_STATES);
	do
		echo 1 > /sys/devices/system/cpu/cpu$X/cpuidle/state$Y/disable
	done
done
