/*
Template file which code snippet is inserted into
*/
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>
#include <setjmp.h>
#include <signal.h>


#define BUF_SIZE 128

FILE *curr2_input, *curr2_log;
pthread_barrier_t start_mointor;
char *mem;

static inline __attribute__((always_inline)) void fence(void) {
       asm volatile("dsb sy\nisb\n");
}

// Catches seg faults, less core dumps?
void segfault_handler(int sig) {
	asm volatile("nop\n");
}

void thread_setup(int core) {
	cpu_set_t cpuset;
	CPU_ZERO(&cpuset);
	CPU_SET(core, &cpuset);
	pthread_t thread;
	thread = pthread_self();
	int ret = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
	if (ret != 0) {
		fprintf(stderr, "pthread_setaffinity_np() failed\n");
		exit(EXIT_FAILURE);
	}
}

void dummy_func_call(void) {
	asm volatile("nop\n");
	return;
}

void *monitor(void *args) {
	thread_setup(1);
	char buf[BUF_SIZE];
	curr2_input = fopen("/sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/curr2_input", "r");
	curr2_log = fopen("/home/bleen/curr2_log", "a");

	if(curr2_input == NULL | curr2_log == NULL) {
		fprintf(stderr, "failed to open file\n");
		exit(EXIT_FAILURE);
	}

	// First access takes a long time (needs to fetch from main mem?), so loading stuff before monitor starts
	fgets(buf, BUF_SIZE, curr2_input);	
	fprintf(curr2_log, "%s", buf);

	pthread_barrier_wait(&start_mointor);
	do {
		fgets(buf, BUF_SIZE, curr2_input);	
		fprintf(curr2_log, "%s", buf);
		sleep(0.0011);
	} while (1);
	fclose(curr2_input);
	fclose(curr2_log);
}

void *code_under_test(void *args) {
	thread_setup(2);
	pthread_barrier_wait(&start_mointor);
	while (1) {
		asm volatile(
			<|SNIPPET|>
		);
	}
}

//! ---- Main ---- !//
int main(int argc, char **argv[]) {
	// Set-up shared memory (less likely to seg fault?)
	mem = (char *)mmap(NULL, 10 * 4096,				 
		PROT_READ | PROT_WRITE,
		MAP_ANONYMOUS | MAP_PRIVATE | MAP_POPULATE, -1, 0); 
	memset(mem, 0x80, 10 * 4096);

    signal(SIGSEGV, segfault_handler);
	// Launching Threads
	pthread_t monitor_thread, cut_thread;
	pthread_barrier_init(&start_mointor, NULL, 2);
	
	pthread_create(&monitor_thread, NULL, monitor, NULL);
	pthread_create(&cut_thread, NULL, code_under_test, NULL);
	
	pthread_join(monitor_thread, NULL);
	return EXIT_SUCCESS;
}
