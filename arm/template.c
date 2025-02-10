/*
Template file which code snippet is inserted into
*/
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>

/* 
AVAILABLE PM EVENTS
Machine Specific, check via reading PMCEID0_EL0 and PMCEID1_EL0
*/
#define SW_INCR                 (0x0000 << 0)
#define L1I_CACHE_REFILL        (0x0001 << 0)
#define L1I_TLB_REFILL          (0x0002 << 0)
#define L1D_CACHE_REFILL        (0x0003 << 0)
#define L1D_CACHE               (0x0004 << 0)
#define L1D_TLB_REFILL          (0x0005 << 0)
#define INST_RETIRED            (0x0008 << 0)
#define EXC_TAKEN               (0x0009 << 0)
#define EXC_RETURN              (0x000A << 0)
#define CID_WRITE_RETIRED       (0x000B << 0)
#define BR_MIS_PRED             (0x0010 << 0)
#define CPU_CYCLES              (0x0011 << 0)
#define BR_PRED                 (0x0012 << 0)
#define MEM_ACCESS              (0x0013 << 0)
#define L1I_CACHE               (0x0014 << 0)
#define L1D_CACHE_WB            (0x0015 << 0)
#define L2D_CACHE               (0x0016 << 0)
#define L2D_CACHE_REFILL        (0x0017 << 0)
#define L2D_CACHE_WB            (0x0018 << 0)
#define BUS_ACCESS              (0x0019 << 0)
#define MEMORY_ERROR            (0x001A << 0)
#define INST_SPEC               (0x001B << 0)
#define TTBR_WRITE_RETIRED      (0x001C << 0)
#define BUS_MASTER_CYCLE        (0x001D << 0)
#define COUNTER_OVERFLOW        (0x001E << 0)
#define CACHE_ALLOCATE          (0x0020 << 0)
#define BR_RETIRED              (0x0021 << 0)
#define BR_MIS_PRED_RETIRED     (0x0022 << 0)
#define L1D_TLB                 (0x0025 << 0)
#define L1I_TLB                 (0x0026 << 0)
#define L3D_CACHE_ALLOCATE      (0x0029 << 0)
#define L3D_CACHE               (0x002B << 0)
#define L2TLB_REFILL            (0x002D << 0)
#define REMOTE_ACCESS           (0x0031 << 0)
#define ITLB_WLK                (0x0035 << 0)
#define LL_CACHE_RD             (0x0036 << 0)
#define LL_CACHE_MISS_RD        (0x0037 << 0)
#define L1D_CACHE_LMISS_RD      (0x0039 << 0)
#define OP_RETIRED              (0x003A << 0)
#define OP_SPEC                 (0x003B << 0)

/* 
AVAILABLE PM EVENTS
Unlabeled in documentation, but show as available
*/
#define NAME1                   (0x0027 << 0)
#define NAME2                   (0x0030 << 0)
#define NAME3                   (0x0032 << 0)
#define NAME4                   (0x0033 << 0)
#define NAME5                   (0x0038 << 0)

/* OTHER SETTINGS */
#define CYCLE_CNTR_EN           (0x0001 << 31)
#define PMEVCNTR_EN             (0x003F << 0) // Enables counters 0 -> 5, machine specific, check via PMCR_EL0.N
#define PMCNTR_CLR              (0x0003 << 1)

static inline __attribute__((always_inline)) void fence(void) {
       asm volatile("dsb sy\nisb\n");
}

static inline __attribute__((always_inline)) uint64_t read_pmccntr(void) {
        uint64_t val;
        asm volatile("mrs %0, pmccntr_el0" : "=r"(val));
        return val;
}

static inline __attribute__((always_inline)) void enable_pmcntrs(void) {
        uint64_t reg;
        asm volatile("mrs %0, pmcntenset_el0" : "=r"(reg));
        asm volatile("msr pmcntenset_el0, %0" : : "r"(reg | CYCLE_CNTR_EN | PMEVCNTR_EN));
        return;
}

static inline __attribute__((always_inline)) void set_pmcntr_events(uint16_t* events) {
        uint64_t reg;
        asm volatile("mrs %0, pmevtyper0_el0" : "=r"(reg));
        asm volatile("msr pmevtyper0_el0, %0" : : "r"(reg | events[0]));

        asm volatile("mrs %0, pmevtyper1_el0" : "=r"(reg));
        asm volatile("msr pmevtyper1_el0, %0" : : "r"(reg | events[1]));

        asm volatile("mrs %0, pmevtyper2_el0" : "=r"(reg));
        asm volatile("msr pmevtyper2_el0, %0" : : "r"(reg | events[2]));

        asm volatile("mrs %0, pmevtyper3_el0" : "=r"(reg));
        asm volatile("msr pmevtyper3_el0, %0" : : "r"(reg | events[3]));

        asm volatile("mrs %0, pmevtyper4_el0" : "=r"(reg));
        asm volatile("msr pmevtyper4_el0, %0" : : "r"(reg | events[4]));

        asm volatile("mrs %0, pmevtyper5_el0" : "=r"(reg));
        asm volatile("msr pmevtyper5_el0, %0" : : "r"(reg | events[5]));
        return;
}

static inline __attribute__((always_inline)) void clear_pmcntrs(void) {
        uint64_t reg;
        asm volatile("mrs %0, pmcr_el0" : "=r"(reg));
        asm volatile("msr pmcr_el0, %0" : : "r"(reg | PMCNTR_CLR));
        return;
}

static inline __attribute__((always_inline)) uint32_t* read_pmevcntrs(void) {
        uint32_t* pmevcntrs = (int*)malloc(6 * sizeof(uint32_t));
        asm volatile("mrs %0, pmevcntr0_el0" : "=r"(pmevcntrs[0]));
        asm volatile("mrs %0, pmevcntr1_el0" : "=r"(pmevcntrs[1]));
        asm volatile("mrs %0, pmevcntr2_el0" : "=r"(pmevcntrs[2]));
        asm volatile("mrs %0, pmevcntr3_el0" : "=r"(pmevcntrs[3]));
        asm volatile("mrs %0, pmevcntr4_el0" : "=r"(pmevcntrs[4]));
        asm volatile("mrs %0, pmevcntr5_el0" : "=r"(pmevcntrs[5]));
        return pmevcntrs;
}

void main() {
        uint64_t cycles;
        uint16_t events[6] = {INST_RETIRED, NAME1, NAME2, NAME3, NAME4, NAME5};
        uint32_t* pmevcntrs;

        enable_pmcntrs();
        set_pmcntr_events(events);
        clear_pmcntrs();
        fence();

        /*
        <|GADGET|>
        */

        fence();
        cycles = read_pmccntr();
        pmevcntrs = read_pmevcntrs();

        printf("CYCLES: %ld\nPMC0: %d\nPMC1: %d\nPMC2: %d\nPMC3: %d\nPMC4: %d\nPMC5: %d\n", cycles, pmevcntrs[0], pmevcntrs[1], pmevcntrs[2], pmevcntrs[3], pmevcntrs[4], pmevcntrs[5]);
        free(pmevcntrs);
        return;
}