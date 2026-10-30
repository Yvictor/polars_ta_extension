#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "ta_libc.h"
#include "ta_abstract.h"
int main(void) {
 assert(TA_Initialize()==TA_SUCCESS);
 assert(strncmp(TA_GetVersionString(),"0.8.1 ",6)==0);
 printf("{\"version\":\"%s\"}\n",TA_GetVersionString());
 char name[128];
 while(fgets(name,sizeof(name),stdin)) {
  name[strcspn(name,"\r\n")]=0;assert(strlen(name)>0);
  const TA_FuncHandle *handle=NULL; const TA_FuncInfo *info=NULL;
  assert(TA_GetFuncHandle(name,&handle)==TA_SUCCESS);
  assert(TA_GetFuncInfo(handle,&info)==TA_SUCCESS);
  printf("{\"function\":\"%s\",\"official_name\":\"%s\",\"nbOptInput\":%u,\"real_options\":[",name,info->name,info->nbOptInput);
  unsigned count=0;
  for(unsigned i=0;i<info->nbOptInput;i++) {
   const TA_OptInputParameterInfo *opt=NULL;
   assert(TA_GetOptInputParameterInfo(handle,i,&opt)==TA_SUCCESS);
   if(opt->type==TA_OptInput_RealRange) {
    const TA_RealRange *range=opt->dataSet;assert(range);
    printf("%s{\"index\":%u,\"name\":\"%s\",\"kind\":\"RealRange\",\"default\":%.17g,\"minimum\":%.17g,\"maximum\":%.17g}",count?",":"",i,opt->paramName,opt->defaultValue,range->min,range->max);count++;
   } else assert(opt->type!=TA_OptInput_RealList);
  }
  printf("]}\n");
 }
 assert(TA_Shutdown()==TA_SUCCESS);return 0;
}
