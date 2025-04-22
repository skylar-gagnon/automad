# This solution was found and adapted slightly from:
# https://github.com/vusec/fpvi-scsb/blob/main/fp_reverse_engineering/test_operands/armv8/enable_arm_pmu/
obj-m	:= enable_arm_pmu.o
PWD	:= $(shell pwd)

KERN = /lib/modules/$(shell uname -r)/build

all:
	gcc read_pmuserenr.c -o read_pmuserenr
	make -C $(KERN) M=$(PWD) modules
clean:
	rm read_pmuserenr
	make -C $(KERN) M=$(PWD) clean
