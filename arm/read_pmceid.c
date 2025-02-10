#include <stdio.h>
#include <unistd.h>
#include <stdint.h>

static inline __attribute__((always_inline)) uint32_t read_pmceid0(void) {
	uint32_t val;
	asm volatile("mrs %0, pmceid0_el0" : "=r"(val));
	return val;
}

static inline __attribute__((always_inline)) uint32_t read_pmceid1(void) {
	uint32_t val;
	asm volatile("mrs %0, pmceid1_el0" : "=r"(val));
	return val;
}

static inline __attribute__((always_inline)) void fence(void) {
       asm volatile("dsb sy\nisb\n");
}

void main() {
	uint32_t pmceid0, pmceid1;
	
	pmceid0 = read_pmceid0();
	pmceid1 = read_pmceid1();
	fence();

	printf("PMCEID0: 0x%08x\nPMCEID1: 0x%08x\n",pmceid0, pmceid1);

	return;
}
