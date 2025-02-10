# Preparing ARM Device for Fuzzing
This directory some necessary setup for the ARMv8 device being fuzzed in order to properly access the PMU from userland. If userland access is already enabled on your device the following is not necessary. Otherwise, please copy this directory to the ARM device and follow the below instructions.
## How to Enable User Access to ARMv8 PMU
1. Run `make` to make all necessary files.
2. Run `insmod enable_arm_pmu.ko` to insert kenel module that enables userland access to the PMU.
3. Run `./read_pmuserenr`. If the value is 1, the kernel module was successful at enabling access, otherwise an issue occured.
## Possible Issue Debug
An issue on my machine was the kernel rewriting the PMUSERENR_EL0 register in the event the CPU enters idle state. If the kernel module was unsuccessful, you can disable CPU idle state and retry enabling user access via the following steps:
1. Run `make` if not already done.
2. Run `sudo ./disable_idle.sh`, this will disable the idle state on all CPU cores
3. If the kernel module is currently running (can be checked using `lsmod | grep enable_arm_pmu`), then remove the module using `rmmod enable_arm_mpu`.
4. Rerun `insmod enable_arm_pmu.ko`.
5. Check the PMUSERENR_EL0 value again with `./read_pmuserenr`.