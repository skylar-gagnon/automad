#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_SIZE 128

int main(int argc, char **argv[]) {
	FILE *curr2_input, *curr2_log;

	char buf[BUF_SIZE];
	curr2_input = fopen("/sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/curr2_input", "r");
	curr2_log = fopen("/home/bleen/tests/curr2_log", "a");

	if(curr2_input == NULL | curr2_log == NULL) {
		fprintf(stderr, "failed to open file\n");
		exit(EXIT_FAILURE);
	}

	do {
		fgets(buf, BUF_SIZE, curr2_input);	
		fprintf(curr2_log, "%s", buf);
		sleep(0.0011);
	} while (1);

	fclose(curr2_input);
	fclose(curr2_log);
	return EXIT_SUCCESS;
}
