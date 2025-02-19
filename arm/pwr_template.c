/*
Template file which code snippet is inserted into
*/
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>

static inline __attribute__((always_inline)) void fence(void) {
       asm volatile("dsb sy\nisb\n");
}

void main() {
        
        fence();

        /*
        <|GADGET|>
        */

        fence();
        
        return;
}