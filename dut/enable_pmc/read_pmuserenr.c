#include <stdio.h>
#include <unistd.h>
#include <stdint.h>

#define BIT0_MASK (1 << 0)

static inline uint64_t read_pmccntr(void) {
	uint64_t val;
	asm volatile("mrs %0, pmuserenr_el0" : "=r"(val));
	return val;
}

void main(void) {
	uint64_t pmc;

	pmc = read_pmccntr();	
	printf("PMUSERENR_EL0.EN VALUE: %d\n", pmc & BIT0_MASK); // If 1, kernel mod worked

	return;
}
