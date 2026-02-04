// aarch64-linux-gnu-gcc -march=armv8-a+sve -static -O0 -o solve solve.c
// qemu-aarch64 -cpu max,sve=on,sve128=on ./solve

#include <arm_sve.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FLG_LEN 0x40

unsigned long flag[] = {0x9beff28796ecf3e9, 0x2335ae47c5b3ea6a,
                        0x7bd30354a9dfecfe, 0x3243804702b92b8c,
                        0x7caad2839ae4bf07, 0x2749c14807c2e873,
                        0xbcd9c683a3ebf11c, 0x4119a527d9aa0a73};

void reverse_micro_kernelA(short *array, svbool_t active) {
    svuint16_t op1 = svdup_n_u16(0x1dea);
    svuint16_t op2 = svdup_n_u16(0xcafe);
    svuint16_t data = svld1_u16(svptrue_b16(), (uint16_t *)array);
    data = svmls_u16_m(active, data, op1, op2);
    svst1_u16(svptrue_b16(), (uint16_t *)array, data);
}

int main(void) {
    char buf[0x100] = {0};
    
    for(int i=0; i<8; i++) {
        ((unsigned long *)buf)[i] = flag[i];
    }

    unsigned long vlen = svcntd();
    for(unsigned long i = 0; i < FLG_LEN; i += vlen * 8) {
        for(int j = 0; j < 0x100; j++) {
            uint16_t active_array[8];
            for(int k = 0; k < 8; k++) {
                active_array[k] = j > (1 << k);
            }
            svuint16_t active_vec = svld1_u16(svptrue_b16(), active_array);
            svbool_t active = svcmpne_n_u16(svptrue_b16(), active_vec, 0);
            reverse_micro_kernelA((short *)(buf + i), active);
        }
    }

    printf("flag: %s\n", buf);
}