/* Untimed public-C contract probe; no product source or benchmark timer. */
#include "ta_libc.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CANARY UINT64_C(0x7ff80000000055aa)
static void word(FILE *f, uint64_t v) {
    unsigned char b[8];
    for (unsigned i=0;i<8;i++) b[i]=(unsigned char)(v>>(i*8));
    assert(fwrite(b,1,8,f)==8);
}
static uint64_t bits(double v) { uint64_t b;memcpy(&b,&v,8);return b; }
static double from_bits(uint64_t b) { double v;memcpy(&v,&b,8);return v; }
int main(int argc,char **argv) {
    assert(argc==2 && sizeof(double)==8);
    assert(TA_Initialize()==TA_SUCCESS);
    assert(strncmp(TA_GetVersionString(),"0.8.4",5)==0);
    FILE *f=fopen(argv[1],"wb");assert(f);
    assert(fwrite("HMARVC01",1,8,f)==8);
    const int periods[]={1,2,3,4,5,6,7,8,20,2600,2601,2703,2704,100000};
    unsigned cases=0;
    for(unsigned pi=0;pi<sizeof(periods)/sizeof(periods[0]);pi++) {
        int p=periods[pi],lb=TA_HMA_Lookback(p),n=10*p;
        if(n<1000)n=1000;
        if(n>1000000)n=1000000;
        assert(lb==p+(int)sqrt((double)p)-2 && lb<n);
        size_t capacity=(size_t)n+8;
        double *input=malloc(capacity*8),*out=malloc(capacity*8),*alias=malloc(capacity*8);
        assert(input && out && alias);
        for(unsigned pattern=0;pattern<4;pattern++) {
            for(size_t i=0;i<capacity;i++)input[i]=from_bits(CANARY);
            for(int i=0;i<n;i++) {
                double x=64.0+((i%37)-18)*0.125;
                input[i+1]=pattern==1 ? 0.0 : pattern==2 ? -0.0 : pattern==3 ? 1e12+x : x;
            }
            const int starts[]={0,lb+1,lb+25};
            for(unsigned si=0;si<3;si++) {
                int start=starts[si],beg=-1,count=-1,abeg=-1,acount=-1;
                for(size_t i=0;i<capacity;i++)out[i]=from_bits(CANARY);
                assert(TA_HMA(start,n-1,input+1,p,&beg,&count,out+1)==TA_SUCCESS);
                assert(beg==(start>lb?start:lb) && count==n-beg && count>0);
                assert(bits(out[0])==CANARY);
                for(int i=0;i<count;i++)assert(isfinite(out[i+1]));
                for(size_t i=(size_t)count+1;i<capacity;i++)assert(bits(out[i])==CANARY);
                memcpy(alias,input,capacity*8);
                assert(TA_HMA(start,n-1,alias+1,p,&abeg,&acount,alias+1)==TA_SUCCESS);
                assert(abeg==beg && acount==count && bits(alias[0])==CANARY);
                assert(memcmp(alias+1,out+1,(size_t)count*8)==0);
                assert(memcmp(alias+1+count,input+1+count,(capacity-1-(size_t)count)*8)==0);
                word(f,(uint64_t)p);word(f,pattern);word(f,(uint64_t)start);word(f,(uint64_t)n);
                word(f,(uint64_t)beg);word(f,(uint64_t)count);word(f,(uint64_t)capacity);
                for(size_t i=0;i<capacity;i++)word(f,bits(out[i]));
                cases++;
            }
        }
        free(input);free(out);free(alias);
    }
    assert(cases==168);assert(fclose(f)==0);assert(TA_Shutdown()==TA_SUCCESS);
    puts("{\"format\":1,\"cases\":168,\"inplace_checks\":168,\"nonempty\":168,\"padding_checked\":true,\"maximum_period\":100000}");
    return 0;
}
