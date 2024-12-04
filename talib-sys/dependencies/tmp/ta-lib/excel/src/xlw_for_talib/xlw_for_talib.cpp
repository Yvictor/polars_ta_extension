/* TA-LIB Copyright (c) 1999-2007, Mario Fortier
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 * - Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * - Neither name of author nor the names of its contributors
 *   may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/* List of contributors:
 *
 *  Initial  Name/description
 *  -------------------------------------------------------------------
 *  MF       Mario Fortier
 *  ND       ndoss
 *
 * Change history:
 *
 *  MMDDYY BY   Description
 *  -------------------------------------------------------------------
 *  121502 MF   First version
 *  042003 MF   Make the initialization/shutdown sequence more reliable
 *              with work-around to Excel bugs. Some info here:
 *                  http://longre.free.fr/pages/prog/api-c.htm
 *  031504 MF   Adapt to a few changes to ta_abstract.h
 *  121504 MF   Add support of optional parameter and display default
 *              in the function wizard.
 *  041806 MF   Adapt to latest TA-Lib interface changes.
 *  102606 ND   Code to make TA-Lib use reverse cell orders.
 *  111306 MF   volume and oi now double + remove trio dependency.
 *  012807 MF   Add back trio dependency.
 */

// The released version of TA-Lib process the cells in a
// top-down order (left-right).
//
// By uncomenting the following, you can reverse the logic to
// be down-up (right-left).

//#define DOWN_UP_CELL_ORDER 1

#include <xlw/xlw.h>
#include <iostream>
#include <sstream>
#include <vector>
#include "Win32StreamBuf.h"
#include "ta_libc.h"
#include "ta_memory.h"

#if defined( DOWN_UP_CELL_ORDER )
  // Include the std::reverse and std::swap_ranges algorithm
  #include <algorithm>
#endif

     
extern "C" double trio_nan(void); 

//#define DEBUG

extern "C"
{

// Define some limits. Only functions fitting within 
// these limits are going to be registered with Excel.
// In practice, this is going sufficient for most, if
// not all, the TA functions.
#define NB_MAX_input    10 /* Maximum Excel inputs */
#define NB_MAX_optinput 10 /* Maximum Excel optional parameters */
#define NB_MAX_output   10 /* Maximum Excel outputs */

// Local Functions
static void registerTAFunction( const TA_FuncInfo *funcInfo, void *opaqueData );

static void allocGlobals    (void);
static void freeGlobals     (void);

static int doInitialization(void);
static int doShutdown      (void);

static int lengthDataPairs( const TA_OptInputParameterInfo *paramInfo );
static void concatDataPairs( char *out, const TA_OptInputParameterInfo *paramInfo );

static int lengthDefault( const TA_OptInputParameterInfo *paramInfo );
static void concatDefault( char *out, const TA_OptInputParameterInfo *paramInfo );

static void displayError( TA_RetCode theRetCode );

#if defined( DOWN_UP_CELL_ORDER )
static void reverseTAOutput(double *in, int rows, int cols);
#endif

// In this file you will see often reference to "TA-Lib parameters"
// against "excel parameters". Many conversion code exist because
// there is not a 1-to-1 relationship between the two.
//
// First, TA-Lib parameters are "input", "optional input" and
// "outputs". The Excel parameters are only the merging of the
// "input" and the "optional input".
//
// Another difference is due to the "Price" type of input of TA-Lib.
// For excel, Price is one or many parameters depending if it is "O",
// "OH", "OHL", "OHLC" or "OHLCV". For TA-Lib, all these are only
// one parameter with the ta-abstract interface.



// Global Variable Optimization
//
// Permanently initialize some arrays and constant that are
// re-used at each TA functions calls.
//
// Overtime, these will permanently point on the largest array
// needed among all the TA function call.
typedef struct
{
   // Preserve the allocated buffer from
   // call to call (speed optimization).
   double *doublePtr;
   int     doubleSize;

   int    *intPtr;
   int     intSize;
} ArrayPtrs;

double nanValue;
ArrayPtrs inputPtrs[NB_MAX_input];
ArrayPtrs outputPtrs[NB_MAX_output];
double *outputExcel;
int outputExcelSize;

// Sometimes xlAutoClose can be called without
// a following xlAutoOpen. Example: Do change
// a cell and attempt to exit and then cancel
// the exit, this will cause xlAutoClose to be
// called, but xlAutoOpen will not be called
// again. 
//
// This is why XLW creation and registration are
// done only once (from xlAutoOpen).
//
// TA-Lib is shutdown on xlAutoClose, and re-initialize
// whenever needed. This allow to reset a possible large
// global memory allocation (by using at our advantage
// the bug in Excel 2003). Bug or not, the following set
// of booleans will help to keep control on the initialization
// and shutdown sequence.
int talibInitDone    = 0;
int registrationDone = 0;


// Globals are allocated/freed along with TA-Lib
// initialization and shutdown.
static void allocGlobals(void)
{
   memset( inputPtrs,  0, sizeof(ArrayPtrs)*NB_MAX_input );
   memset( outputPtrs, 0, sizeof(ArrayPtrs)*NB_MAX_output );
   nanValue = trio_nan();
   outputExcelSize = 0;
   outputExcel     = NULL;
}
static void freeGlobals( void )
{
   int i;

   for( i=0; i < NB_MAX_input; i++ )
   {
      FREE_IF_NOT_NULL( inputPtrs[i].doublePtr );
      FREE_IF_NOT_NULL( inputPtrs[i].intPtr );
   }
   for( i=0; i < NB_MAX_output; i++ )
   {
      FREE_IF_NOT_NULL( outputPtrs[i].doublePtr );
      FREE_IF_NOT_NULL( outputPtrs[i].intPtr );
   }

   FREE_IF_NOT_NULL( outputExcel );
}

#define GLOBAL_ARRAY_MACRO(pType,pTypeIO) \
   pType *alloc_##pType##_##pTypeIO( int index, int nbElement ) \
   { \
      if( index > NB_MAX_##pTypeIO ) \
      { \
         return NULL; \
      } \
      if( !pTypeIO##Ptrs[index].pType##Ptr ) \
      { \
         pType *newArray; \
         newArray = (pType *)TA_Malloc( sizeof(pType)*nbElement ); \
         pTypeIO##Ptrs[index].pType##Ptr  = newArray; \
         pTypeIO##Ptrs[index].pType##Size = nbElement; \
      } \
      else if( nbElement > pTypeIO##Ptrs[index].pType##Size ) \
      { \
         TA_Free( pTypeIO##Ptrs[index].pType##Ptr ); \
         pType *newArray; \
         newArray = (pType *)TA_Malloc( sizeof(pType)*nbElement ); \
         pTypeIO##Ptrs[index].pType##Ptr = newArray; \
         pTypeIO##Ptrs[index].pType##Size = nbElement; \
      } \
      return pTypeIO##Ptrs[index].pType##Ptr; \
   } \
   pType *get_##pType##_##pTypeIO( int index ) \
   { \
      return pTypeIO##Ptrs[index].pType##Ptr; \
   }

GLOBAL_ARRAY_MACRO(double,input)
GLOBAL_ARRAY_MACRO(int,input)
GLOBAL_ARRAY_MACRO(double,output)
GLOBAL_ARRAY_MACRO(int,output)

#undef GLOBAL_ARRAY_MACRO

static int doInitialization(void)
{
   TA_RetCode retCode;


   // If already initialize, do nothing.
   if( !talibInitDone )
   {
      allocGlobals();

      #ifdef DEBUG
        XlfExcel::Instance().MsgBox("Initializing TA-Lib", "Debug");
      #endif

      // Displays a message in the status bar.
      XlfExcel::Instance().SendMessage("Initializing TA-Lib...");

      // Initialize TA-Lib

      retCode = TA_Initialize();

      if( retCode != TA_SUCCESS )
      {
         XlfExcel::Instance().MsgBox("Failed to initialize TA_Lib.xll", "Error");
         return 0;
      }

      #ifndef DEBUG
        // Clears the status bar.
        XlfExcel::Instance().SendMessage();
      #endif

      talibInitDone = 1;
   }

   if( !registrationDone )
   {
      #ifdef DEBUG
        XlfExcel::Instance().MsgBox("Registering TA-Lib functions...", "Debug");
      #endif

      // Displays a message in the status bar.
      XlfExcel::Instance().SendMessage("Registering TA-Lib functions...");

      // Register all the TA function. 
      TA_ForEachFunc( registerTAFunction, NULL );

      // Register other misc. function
      const char *utilGroupStr = "TA-LIB [Utilities]";
      XlfFuncDesc versionFunc("xlTA_Version","TA_Version","Return the version of TA-Lib. ", utilGroupStr, XlfFuncDesc::Volatile );
      versionFunc.Register();

      XlfFuncDesc naValueFunc("xlTA_NAError","TA_NAError","Return the excel value #N/A! ", utilGroupStr );
      naValueFunc.Register();

      XlfArgDesc range_param("Range", "Range of cells" );
      XlfArgDesc n_param("n", "Number of cell to add, starting with the last in the provided range" );
      XlfFuncDesc sumLastInRangeFunc("xlTA_SumLastInRange","TA_SumLastInRange","Add the 'n' last cell in the range", utilGroupStr );
      sumLastInRangeFunc.SetArguments(range_param+n_param);
      sumLastInRangeFunc.Register();

      #ifndef DEBUG
        // Clears the status bar.
        XlfExcel::Instance().SendMessage();
      #endif

      registrationDone = 1;
   }

   return 1;
}

static int doShutdown(void)
{
   if( talibInitDone )
   {
     #ifdef DEBUG
       XlfExcel::Instance().MsgBox("Shutting down TA-Lib...", "Debug");
     #endif

     XlfExcel::Instance().SendMessage("Shutting Down TA-Lib...");
     freeGlobals();
   
     TA_RetCode retCode;

     delete &XlfExcel::Instance();

     /* Shutdown TA-Lib. */
     retCode = TA_Shutdown();
     if( retCode != TA_SUCCESS )
     {
       displayError(retCode);
     }


     #ifdef DEBUG
       if( outCoredump )
          fclose( outCoredump );
     #endif

     #ifndef DEBUG

       // Clears the status bar.
       XlfExcel::Instance().SendMessage();
     #endif

     talibInitDone = 0;
   }


   return 1;
}

/*********************/
/* Utility functions */
/*********************/

#if defined( DOWN_UP_CELL_ORDER )
void reverseTAOutput(double *in, int rows, int cols)
{
  double *firstRow = in;
  double *lastRow  = in + (rows-1)*cols;
  for ( ; firstRow < lastRow; firstRow+=cols, lastRow-=cols)
     std::swap_ranges(firstRow, firstRow+cols, lastRow);
}
#endif

// Character used when building a string representing the list of data pairs.
#define EQUAL_CHAR  '='
#define SEP_CHAR    ','
static int lengthDataPairs( const TA_OptInputParameterInfo *paramInfo )
{
   unsigned int i;
   int total = 0;
   char buffer[400];

   // Slightly overestimate is ok. Under-estimate is not good!
   switch( paramInfo->type )
   {
   case TA_OptInput_IntegerList:
      {
         TA_IntegerList *list = (TA_IntegerList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_IntegerDataPair *dataPair = &list->data[i];
            sprintf( buffer, "%d", dataPair->value );
            total += strlen(dataPair->string) + 3 + strlen(buffer);
         }
      }
      break;

   case TA_OptInput_RealList:
      {
         TA_RealList *list = (TA_RealList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_RealDataPair *dataPair = &list->data[i];
            sprintf( buffer, "%g", dataPair->value );
            total += strlen(dataPair->string) + 3 + strlen(buffer);
         }
      }
      break;
   default:
      break;
   }

   return total;
}

static void concatDataPairs( char *out, const TA_OptInputParameterInfo *paramInfo )
{
   // Jump to the end of out
   while( *out != NULL ) out++;

   // Append each entry of the list
   switch( paramInfo->type )
   {
   case TA_OptInput_IntegerList:
      {
         TA_IntegerList *list = (TA_IntegerList *) paramInfo->dataSet;
         int offset = sprintf( out, ": " );
         unsigned int i = 0; 
         while( i < list->nbElement )
         {
            const TA_IntegerDataPair *dataPair = &list->data[i++];
            offset += sprintf( out+offset, "%d%c%s%c ", 
                               dataPair->value,
                               EQUAL_CHAR,
                               dataPair->string,
                               i < list->nbElement? SEP_CHAR:' ' );
         }
      }
      break;

   case TA_OptInput_RealList:
      {
         TA_RealList *list = (TA_RealList *) paramInfo->dataSet;
         int offset = sprintf( out, ": " );
         unsigned int i = 0; 
         while( i < list->nbElement )
         {
            const TA_RealDataPair *dataPair = &list->data[i++];
            offset += sprintf( out+offset, "%g%c%s%c ", 
                               dataPair->value,
                               EQUAL_CHAR,
                               dataPair->string,
                               i < list->nbElement? SEP_CHAR:' ' );
         }
      }
      break;
   default:
      break;
   }
}

#define DEFAULT_PREFIX " (Default="
#define DEFAULT_SUFFIX ")"
static int lengthDefault( const TA_OptInputParameterInfo *paramInfo )
{
   unsigned int i;
   int total = 0;
   char buffer[400];
  
   // Slightly overestimate is ok. Under-estimate is not good!
   switch( paramInfo->type )
   {
   case TA_OptInput_IntegerRange:
      {
         sprintf( buffer, "%d", paramInfo->defaultValue );
         total = strlen( buffer ) + strlen(DEFAULT_PREFIX) + strlen(DEFAULT_SUFFIX);
      }
      break;

   case TA_OptInput_RealRange:
      {
         sprintf( buffer, "%g", paramInfo->defaultValue );
         total = strlen( buffer )  + strlen(DEFAULT_PREFIX) + strlen(DEFAULT_SUFFIX);
      }
      break;

   case TA_OptInput_IntegerList:
      {
         TA_IntegerList *list = (TA_IntegerList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_IntegerDataPair *dataPair = &list->data[i];
            if( (int)dataPair->value == (int)paramInfo->defaultValue )
            {
               total = strlen(dataPair->string) + strlen(DEFAULT_PREFIX) + strlen(DEFAULT_SUFFIX);
               i = list->nbElement; // Exit loop
            }
         }
      }
      break;

   case TA_OptInput_RealList:
      {
         TA_RealList *list = (TA_RealList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_RealDataPair *dataPair = &list->data[i];
            if( dataPair->value == paramInfo->defaultValue )
            {
               total = strlen(dataPair->string) + strlen(DEFAULT_PREFIX) + strlen(DEFAULT_SUFFIX);
               i = list->nbElement; // Exit loop
            }
         }
      }
      break;
   default:
      break;
   }

   return total;
}

static void concatDefault( char *out, const TA_OptInputParameterInfo *paramInfo )
{
   int i;
   // Jump to the end of out
   while( *out != NULL ) out++;

   // Append the default.

   switch( paramInfo->type )
   {
   case TA_OptInput_IntegerRange:
      {
         sprintf( out, "%s%d%s", DEFAULT_PREFIX, (int)paramInfo->defaultValue, DEFAULT_SUFFIX );
      }
      break;

   case TA_OptInput_RealRange:
      {
         sprintf( out, "%s%g%s", DEFAULT_PREFIX, paramInfo->defaultValue, DEFAULT_SUFFIX );
      }
      break;

   case TA_OptInput_IntegerList:
      {
         TA_IntegerList *list = (TA_IntegerList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_IntegerDataPair *dataPair = &list->data[i];
            if( (int)dataPair->value == (int)paramInfo->defaultValue )
            {
               sprintf( out, "%s%s%s", DEFAULT_PREFIX, dataPair->string, DEFAULT_SUFFIX);
               i = list->nbElement; // Exit loop
            }
         }
      }
      break;

   case TA_OptInput_RealList:
      {
         TA_RealList *list = (TA_RealList *) paramInfo->dataSet;
         for( i=0; i < list->nbElement; i++ )
         {
            const TA_RealDataPair *dataPair = &list->data[i];
            if( dataPair->value == paramInfo->defaultValue )
            {
               sprintf( out, "%s%g%s", DEFAULT_PREFIX, dataPair->value, DEFAULT_SUFFIX );
               i = list->nbElement; // Exit loop
            }
         }
      }
      break;
   default:
      break;
   }
}

static int nbExcelInput( const TA_FuncInfo *funcInfo )
{
   unsigned int i;
   int nbParam = 0;

   for( i=0; i < funcInfo->nbInput; i++ )
   {
      const TA_InputParameterInfo *paramInfo;
      TA_GetInputParameterInfo( funcInfo->handle, i, &paramInfo );
      switch( paramInfo->type )
      {
      case TA_Input_Price:
         if( paramInfo->flags & TA_IN_PRICE_OPEN )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_HIGH )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_LOW )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_CLOSE )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_VOLUME )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_OPENINTEREST )
            nbParam++;
         if( paramInfo->flags & TA_IN_PRICE_TIMESTAMP )
            nbParam++;
         break;
      default:
         nbParam++;
         break;
      }
   }

   return nbParam;
}

static void displayError( TA_RetCode theRetCode )
{
   TA_RetCodeInfo retCodeInfo;

   /* Info is always returned, even when 'theRetCode' is invalid. */
   TA_SetRetCodeInfo( theRetCode, &retCodeInfo );

   XlfExcel::Instance().MsgBox(retCodeInfo.infoStr, retCodeInfo.enumStr );
}

// The following will be executed for ALL functions existing
// in TA-Lib.
// Registration is done once when Excel call xlAutoOpen.
static void registerTAFunction( const TA_FuncInfo *funcInfo, void *opaqueData )
{
   char *groupStr = NULL;
   char *excelName = NULL;
   XlfFuncDesc *func = NULL;

   /* Register the TA function to Excel. 
    * Excel must know the parameter. A short description
    * is also registered to help the end-user when he uses
    * the function wizard.
    */
   bool skipRegistration = false;
   XlfArgDescList *argList = new XlfArgDescList();

   // Build the list of parameters
   std::vector<XlfArgDesc *> argListPtr;
   if( (nbExcelInput(funcInfo) > NB_MAX_input)   ||  
       (funcInfo->nbOutput     > NB_MAX_output)  ||
       (funcInfo->nbOptInput   > NB_MAX_optinput) )
   {
      /* The number of parameters exceed what can be handled
       * by this glue code.
       */
      skipRegistration = true;
   }
   else
   {
      unsigned int i;
      for( i=0; i < funcInfo->nbInput; i++ )
      {
         const TA_InputParameterInfo *paramInfo;
         TA_GetInputParameterInfo( funcInfo->handle, i, &paramInfo );
         switch( paramInfo->type )
         {
         case TA_Input_Price:
            if( paramInfo->flags & TA_IN_PRICE_OPEN )
               argListPtr.push_back( new XlfArgDesc("inOpen","One-dimension array of data representing Open price. "));
            if( paramInfo->flags & TA_IN_PRICE_HIGH )
               argListPtr.push_back( new XlfArgDesc("inHigh","One-dimension array of data representing High price. "));
            if( paramInfo->flags & TA_IN_PRICE_LOW )
               argListPtr.push_back( new XlfArgDesc("inLow","One-dimension array of data representing Low price. "));
            if( paramInfo->flags & TA_IN_PRICE_CLOSE )
               argListPtr.push_back( new XlfArgDesc("inClose","One-dimension array of data representing Close price. "));
            if( paramInfo->flags & TA_IN_PRICE_VOLUME )
               argListPtr.push_back( new XlfArgDesc("inVolume","One-dimension array of data representing Volume. "));
            if( paramInfo->flags & TA_IN_PRICE_OPENINTEREST )
               argListPtr.push_back( new XlfArgDesc("inOpenInterest","One-dimension array of data representing Open Interest. "));
            if( paramInfo->flags & TA_IN_PRICE_TIMESTAMP )
               skipRegistration = true; // Not supported yet within Excel
            break;
         case TA_Input_Real:
            argListPtr.push_back( new XlfArgDesc("inReal","One-dimension array of data "));
            break;
         case TA_Input_Integer:
            argListPtr.push_back( new XlfArgDesc("inInteger","One-dimension array of data "));
            break;
         default:
            skipRegistration = true;
         }
      }

      for( i=0; i < funcInfo->nbOptInput; i++ )
      {
         const TA_OptInputParameterInfo *paramInfo;
         TA_GetOptInputParameterInfo( funcInfo->handle, i, &paramInfo );

         // Allocate the info string with all the possible values (when applicable)
         int length = lengthDataPairs( paramInfo ) + lengthDefault( paramInfo );
         char *strInfo = (char *)TA_Malloc( strlen(paramInfo->hint) + 50 + length );
         strcpy( strInfo, paramInfo->hint );         
         concatDataPairs( strInfo, paramInfo );
         concatDefault( strInfo, paramInfo );

         // Must append two spaces, seems there is a bug in the way Excel handle
         // the description and the last 1 or 2 characters are sometimes deleted.
         strcat( strInfo, " " );

         //argListPtr.push_back( new XlfArgDesc(paramInfo->displayName, strInfo) );
         argListPtr.push_back( new XlfArgDesc(paramInfo->displayName, strInfo) );
         TA_Free( strInfo );
      }

      const char *talib_prefix = "TA-Lib [";
      const char *talib_suffix = "]";
   
      groupStr = (char *)TA_Malloc( strlen(funcInfo->group) + strlen(talib_prefix) + strlen(talib_suffix) + 1 );

      strcpy( groupStr, talib_prefix );
      strcat( groupStr, funcInfo->group );
      strcat( groupStr, talib_suffix );

      excelName = (char *)TA_Malloc( strlen(funcInfo->name) + 10 );
      strcpy( excelName, "xl" );
      strcpy( excelName+2, "TA_" );
      strcpy( excelName+5, funcInfo->name );
      func = new XlfFuncDesc( excelName,
                              &excelName[2],
                              funcInfo->hint,
                              groupStr );

      // Set the arguments for the function. Note how you create a XlfArgDescList from
      // two or more XlfArgDesc (operator+). You can not push the XlfArgDesc one by one.
      int nbArg = argListPtr.size();
      switch( nbArg )
      {
      case 1:
         (*argList) = *argListPtr[0];
         break;
      case 2:
         (*argList) = *argListPtr[0] + *argListPtr[1];
         break;
      case 3:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2];
         break;
      case 4:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3];
         break;
      case 5:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4];
         break;
      case 6:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5];
         break;
      case 7:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5] +
                      *argListPtr[6];
         break;
      case 8:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5] +
                      *argListPtr[6] + *argListPtr[7];
         break;
      case 9:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5] +
                      *argListPtr[6] + *argListPtr[7] +
                      *argListPtr[8];
         break;
      case 10:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5] +
                      *argListPtr[6] + *argListPtr[7] +
                      *argListPtr[8] + *argListPtr[9];
         break;
      case 11:
         (*argList) = *argListPtr[0] + *argListPtr[1] +
                      *argListPtr[2] + *argListPtr[3] +
                      *argListPtr[4] + *argListPtr[5] +
                      *argListPtr[6] + *argListPtr[7] +
                      *argListPtr[8] + *argListPtr[9] +
                      *argListPtr[10];
         break;
      case 12:
         (*argList) = *argListPtr[0]  + *argListPtr[1] +
                      *argListPtr[2]  + *argListPtr[3] +
                      *argListPtr[4]  + *argListPtr[5] +
                      *argListPtr[6]  + *argListPtr[7] +
                      *argListPtr[8]  + *argListPtr[9] +
                      *argListPtr[10] + *argListPtr[11];
         break;
      case 13:
         (*argList) = *argListPtr[0]  + *argListPtr[1] +
                      *argListPtr[2]  + *argListPtr[3] +
                      *argListPtr[4]  + *argListPtr[5] +
                      *argListPtr[6]  + *argListPtr[7] +
                      *argListPtr[8]  + *argListPtr[9] +
                      *argListPtr[10] + *argListPtr[11]+
                      *argListPtr[12];
         break;
      case 14:
         (*argList) = *argListPtr[0]  + *argListPtr[1] +
                      *argListPtr[2]  + *argListPtr[3] +
                      *argListPtr[4]  + *argListPtr[5] +
                      *argListPtr[6]  + *argListPtr[7] +
                      *argListPtr[8]  + *argListPtr[9] +
                      *argListPtr[10] + *argListPtr[11]+
                      *argListPtr[12] + *argListPtr[13];
         break;
      case 15:
         (*argList) = *argListPtr[0]  + *argListPtr[1] +
                      *argListPtr[2]  + *argListPtr[3] +
                      *argListPtr[4]  + *argListPtr[5] +
                      *argListPtr[6]  + *argListPtr[7] +
                      *argListPtr[8]  + *argListPtr[9] +
                      *argListPtr[10] + *argListPtr[11]+
                      *argListPtr[12] + *argListPtr[13]+
                      *argListPtr[14];
         break;
      default:
         // Too much parameters
         skipRegistration = true;
     }
  }

  if( !skipRegistration && func && argList )
  {
     (*func).SetArguments(*argList);
     // Registers the function.    
     (*func).Register();
  }

  // All done. Clean-up.
  std::vector<XlfArgDesc *>::iterator it;
  for (it = argListPtr.begin(); it != argListPtr.end(); ++it)   
     delete *it;
  delete argList;
  delete func;

  FREE_IF_NOT_NULL( groupStr );
  FREE_IF_NOT_NULL( excelName );
}

LPXLOPER doTACall( char *funcName, XlfOper *params, int nbParam )
{
    const TA_FuncHandle *funcHandle;
    const TA_FuncInfo   *funcInfo;
    TA_RetCode retCode;
    unsigned int i, j, k;
    int nbValidData, excelArraySize;
    
    retCode = TA_GetFuncHandle( funcName, &funcHandle );
    if( retCode != TA_SUCCESS )
    {
       displayError(retCode);
       XlfExcel::Instance().MsgBox(funcName, "TA_GetFuncHandle Failed!");
       return XlfOper::Error(xlerrValue);
    }

    retCode = TA_GetFuncInfo( funcHandle, &funcInfo );
    if( retCode != TA_SUCCESS )
    {
       displayError(retCode);
       XlfExcel::Instance().MsgBox(funcName, "TA_GetFuncInfo Failed!");
       return XlfOper::Error(xlerrValue);
    }

    // These will be different then NULL when allocated.
    TA_ParamHolder *paramsForTALib = NULL;

    // The following vectors are used to keep track of locally
    // allocated memory. All are freed on exit or exception.
    #define FREE_ALL_ALLOC \
    { \
       if( paramsForTALib ) \
       { \
          TA_ParamHolderFree( paramsForTALib ); \
          paramsForTALib = NULL; \
       } \
    }

    // Coerce all the excel inputs and re-write these
    // within new allocated arrays. This is for a better
    // monitoring of memory leak by using TA_Malloc.
    // This is slightly inneficient, but I choosed the
    // "safest and most well understood by me" solution 
    // for reliability.
    int commonBegIdx, commonEndIdx;
    try
    {
       /**************************
        * Start Allocating Input *
        **************************/
       int inputSize = 0;

       unsigned int curExcelParam = 0;
       int curTALibParam = 0;
       int toDoMask      = 0;
       for( curExcelParam=0; curExcelParam < (nbParam - funcInfo->nbOptInput); curExcelParam++ )
       {
          if( params[curExcelParam].IsMissing() )
          {
             FREE_ALL_ALLOC;
             return XlfOper::Error(xlerrValue);
          }

          // XlfExcel::Coerce method (internally called) will return to Excel
          // if one of the cell was invalidated and need to be recalculated.
          std::vector<double> temp = params[curExcelParam].AsDoubleVector(XlfOper::RowMajor);

          // Trap zero size input vector
          excelArraySize = temp.size();
          if( excelArraySize == 0 )
          {
             FREE_ALL_ALLOC;
             return XlfOper::Error(xlerrValue);
          }

          // Make sure all inputs have the same number of elements
          if( curExcelParam == 0 )
             inputSize = excelArraySize;
          else if( inputSize != excelArraySize )
          {
             FREE_ALL_ALLOC;
             return XlfOper::Error(xlerrValue);
          }

          #if defined( DOWN_UP_CELL_ORDER )
             // Reverse the input
             std::reverse(temp.begin(), temp.end());
          #endif
 
          // 'input' will contain only the valid data among the
          // cells provided by excel.
          const TA_InputParameterInfo *paramInfo;
          TA_GetInputParameterInfo( funcInfo->handle, curTALibParam, &paramInfo );

          // Only one of these two will be != NULL
          double *inputDouble = NULL;
          int    *inputInt    = NULL;

          // Set either inputDouble or inputInt and increment
          // the curTALibParam when needed.
          switch( paramInfo->type )
          {
          case TA_Input_Real:
             inputDouble = alloc_double_input( curExcelParam, excelArraySize );
             if( !inputDouble )
             {
                FREE_ALL_ALLOC;
                return XlfOper::Error(xlerrValue);
             }
             curTALibParam++;
             break;

          case TA_Input_Integer:
             inputInt = alloc_int_input( curExcelParam, excelArraySize );
             if( !inputInt )
             {
                FREE_ALL_ALLOC;
                return XlfOper::Error(xlerrValue);
             }
             curTALibParam++;
             break;

          case TA_Input_Price:
             if( toDoMask == 0 )
                toDoMask = paramInfo->flags;

             if( toDoMask & TA_IN_PRICE_OPEN )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_OPEN;
             }
             else if( toDoMask & TA_IN_PRICE_HIGH )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_HIGH;
             }
             else if( toDoMask & TA_IN_PRICE_LOW )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_LOW;
             }
             else if( toDoMask & TA_IN_PRICE_CLOSE )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_CLOSE;
             }
             else if( toDoMask & TA_IN_PRICE_VOLUME )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_VOLUME;
             }
             else if( toDoMask & TA_IN_PRICE_OPENINTEREST )
             {
                inputDouble = alloc_double_input( curExcelParam, excelArraySize );
                toDoMask &= ~TA_IN_PRICE_OPENINTEREST;
             }
             else /*if( toDoMask & TA_IN_PRICE_TIMESTAMP ) Not supported */
             {
                FREE_ALL_ALLOC;
                return XlfOper::Error(xlerrValue);
             }

             /* Was the last portion of the PRICE to handle for this TA-Lib parameter */
             if( toDoMask == 0 )
                curTALibParam++;
             break;
          }

          // Identify the range of valid data with dataBeg and dataEnd.
          // Copy the data in 'inputDouble' or 'inputInt' at the same time.
          int dataBeg=0;
          int dataEnd=0;
          int inIdx=0;
          std::vector<double>::iterator it;
          bool again = true;

          if( inputDouble )
          {             
             double tempReal;
             for (it = temp.begin(); (it != temp.end()) && again; ++it)   
             {
                tempReal = *it;
                if( _isnan(tempReal) )
                   dataBeg++;
                else
                {
                   again = false;
                   inIdx = dataBeg;
                   inputDouble[inIdx++] = tempReal;
                   dataEnd=dataBeg;
                }
             }

             again=true;
             for (; (it != temp.end()) && again; ++it)
             {
                tempReal = *it;
                if( _isnan(tempReal) )
                   again = false;
                else
                {
                   inputDouble[inIdx++] = tempReal;
                   dataEnd++;
                }
             }
          }
          else
          {
             double tempReal;
             for (it = temp.begin(); (it != temp.end()) && again; ++it)   
             {
                tempReal = *it;
                if( _isnan(tempReal) )
                   dataBeg++;
                else
                {
                   again = false;
                   inIdx = dataBeg;
                   inputInt[inIdx++] = (int)tempReal;
                   dataEnd=dataBeg;
                }
             }

             again=true;
             for (; (it != temp.end()) && again; ++it)
             {
                tempReal = *it;
                if( _isnan(tempReal) )
                   again = false;
                else
                {
                   inputInt[inIdx++] = (int)tempReal;
                   dataEnd++;
                }
             }
          }

          if( curExcelParam == 0 )
          {
             // This is the first input being processed.
             commonBegIdx = dataBeg;
             commonEndIdx = dataEnd;
          }
          else
          {
             // When processing more than one inputs, make
             // sure that they have the same "common" range
             // of input data.
             if( dataBeg > commonBegIdx )
                commonBegIdx = dataBeg;
             if( dataEnd < commonEndIdx )
                commonEndIdx = dataEnd;
          }

          // Trap case where there is no valid data left
          nbValidData = (commonEndIdx-commonBegIdx)+1;
          if( nbValidData <= 0 )
          {
             FREE_ALL_ALLOC;
             return XlfOper::Error(xlerrValue);
          }
       }

       /************************************
        * Allocates arrays for the outputs *
        ************************************/
       for( i=0; i < funcInfo->nbOutput; i++ )
       {
          const TA_OutputParameterInfo *paramInfo;
          retCode = TA_GetOutputParameterInfo( funcInfo->handle, i, &paramInfo );
          if( retCode != TA_SUCCESS )
          {
             FREE_ALL_ALLOC;
             return XlfOper::Error(xlerrValue);
          }

          switch( paramInfo->type )
          {
          case TA_Output_Real:
             alloc_double_output( i, nbValidData );
             break;
          case TA_Output_Integer:
             alloc_int_output( i, nbValidData );
             break;
          }
       }

       /*****************************************
        * Start Setting Input Params for TA-Lib *
        *****************************************/
       retCode = TA_ParamHolderAlloc( funcHandle, &paramsForTALib );
       if( retCode != TA_SUCCESS )
       {
          FREE_ALL_ALLOC;
          return XlfOper::Error(xlerrValue);
       }

       curExcelParam = 0;
       for( i=0; i < funcInfo->nbInput; i++ )
       {
          const TA_InputParameterInfo *paramInfo;
          TA_GetInputParameterInfo( funcInfo->handle, i, &paramInfo );
          switch( paramInfo->type )
          {
          case TA_Input_Real:
             {
                double *tempPtr = get_double_input(curExcelParam++);
                retCode = TA_SetInputParamRealPtr( paramsForTALib, i, 
                                            &tempPtr[commonBegIdx] );
                if( retCode != TA_SUCCESS )
                {
                   displayError(retCode);
                   XlfExcel::Instance().MsgBox(funcName, "TA_SetInputParamRealPtr Failed!");
                }
             }
             break;

          case TA_Input_Integer:
             {
                int *tempPtr = get_int_input(curExcelParam++);
                retCode = TA_SetInputParamIntegerPtr( paramsForTALib, i, 
                                             &tempPtr[commonBegIdx] );
                if( retCode != TA_SUCCESS )
                {
                   displayError(retCode);
                   XlfExcel::Instance().MsgBox(funcName, "TA_SetInputParamIntegerPtr Failed!");
                }
             }
             break;

          case TA_Input_Price:      
             TA_Real   *open = NULL;
             TA_Real   *high = NULL;
             TA_Real   *low = NULL;
             TA_Real   *close = NULL;
             TA_Real   *volume = NULL;
             TA_Real   *openInterest = NULL;

             if( paramInfo->flags & TA_IN_PRICE_OPEN )
                open = &(get_double_input(curExcelParam++)[commonBegIdx]);
             if( paramInfo->flags & TA_IN_PRICE_HIGH )
                high = &(get_double_input(curExcelParam++)[commonBegIdx]); 
             if( paramInfo->flags & TA_IN_PRICE_LOW )
                low = &(get_double_input(curExcelParam++)[commonBegIdx]);
             if( paramInfo->flags & TA_IN_PRICE_CLOSE )
                close = &(get_double_input(curExcelParam++)[commonBegIdx]);
             if( paramInfo->flags & TA_IN_PRICE_VOLUME )
                volume = &(get_double_input(curExcelParam++)[commonBegIdx]);
             if( paramInfo->flags & TA_IN_PRICE_OPENINTEREST )
                openInterest = &(get_double_input(curExcelParam++)[commonBegIdx]);

             retCode = TA_SetInputParamPricePtr( paramsForTALib, i,
                                                 open, high, low, close,
                                                 volume, openInterest );
             if( retCode != TA_SUCCESS )
             {
                displayError(retCode);
                XlfExcel::Instance().MsgBox(funcName, "TA_SetInputParamPricePtr Failed!");
             }
             break;
          }
       }
   
       /**********************************
        * Start Setting Optional Params  *
        **********************************/
       for( i=0; i < funcInfo->nbOptInput; i++ )
       {
          if( params[curExcelParam].IsMissing() )
          {
             curExcelParam++;
             continue;
          }

          const TA_OptInputParameterInfo *paramInfo;
          retCode = TA_GetOptInputParameterInfo( funcInfo->handle, i, &paramInfo );
          if( retCode != TA_SUCCESS )
          {
             displayError(retCode);
             XlfExcel::Instance().MsgBox(funcName, "TA_GetOptInputParameterInfo Failed!");
          }

          switch( paramInfo->type)
          {
          case TA_OptInput_RealRange:
             retCode = TA_SetOptInputParamReal( paramsForTALib, i, params[curExcelParam++].AsDouble() );             
             break;

          case TA_OptInput_IntegerRange:             
             retCode = TA_SetOptInputParamInteger( paramsForTALib, i, params[curExcelParam++].AsInt() );
             break;
   
          case TA_OptInput_RealList:
             // Check for possibly recognizing strings, else assume
             // it is a value if all digits.
             {
                char *str = params[curExcelParam].AsString();
                // Calculate length and check if all digit.
                unsigned int length = 0;
                int nbDigit = 0;
                char car;
                car = str[0];
                while( car != 0 )
                {
                   if( isdigit(car) )
                      nbDigit++;
                   car = str[++length];
                }
   
                if( nbDigit == length )
                {
                   // The string is all digit, so don't try to identify the string.
                   retCode = TA_SetOptInputParamReal( paramsForTALib, i, params[curExcelParam].AsDouble() );                                                     
                }
                else
                {
                   // Try to identify the string, if fails set with the default
                   const TA_OptInputParameterInfo *paramInfo;
                   TA_GetOptInputParameterInfo( funcInfo->handle, i, &paramInfo );
                   TA_RealList *list = (TA_RealList *) paramInfo->dataSet;
                   int foundInList = 0;
                   TA_Real valueForThisString;
                   for( j=0; (j < list->nbElement) && !foundInList; j++ )
                   {
                      const TA_RealDataPair *dataPair = &list->data[j];
                      int sameString = 1;
                      const char * const str2 = dataPair->string;
                      for( k=0; (k < length) && sameString; k++ )
                      {
                         if( toupper( str2[k] ) != toupper( str[k] ) )
                            sameString = 0;
                      }
                      if( sameString )
                      {
                         foundInList = 1;
                         valueForThisString = dataPair->value;
                      }
                   }
                   if( !foundInList )
                      retCode = TA_SetOptInputParamReal( paramsForTALib, i, TA_REAL_MIN );
                   else
                      retCode = TA_SetOptInputParamReal( paramsForTALib, i, valueForThisString );
                }
                curExcelParam++;
             }
             break;
   
          case TA_OptInput_IntegerList:
             // Check for possibly recognizing strings, else assume
             // it is a value if all digits.
             {
                char *str = params[curExcelParam].AsString();
   
                // Calculate length and check if all digit.
                unsigned int length = 0;
                int nbDigit = 0;
                char car;
                car = str[0];
                while( car != 0 )
                {
                   if( isdigit(car) )
                      nbDigit++;
                   car = str[++length];
                }
   
                if( nbDigit == length )
                {
                   // The string is all digit, so don't try to identify the string.
                   retCode = TA_SetOptInputParamInteger( paramsForTALib, i, 
                                                         params[curExcelParam].AsInt() );
                }
                else
                {
                   // Try to identify the string, if fails set with the default
                   const TA_OptInputParameterInfo *paramInfo;
                   TA_GetOptInputParameterInfo( funcInfo->handle, i, &paramInfo );
                   TA_IntegerList *list = (TA_IntegerList *) paramInfo->dataSet;
                   int foundInList = 0;
                   int valueForThisString;
                   for( j=0; (j < list->nbElement) && !foundInList; j++ )
                   {
                      const TA_IntegerDataPair *dataPair = &list->data[j];
                      int sameString = 1;
                      const char * const str2 = dataPair->string;
                      for( k=0; (k < length) && sameString; k++ )
                      {
                         if( toupper( str2[k] ) != toupper( str[k] ) )
                            sameString = 0;
                      }
                      if( sameString )
                      {
                         foundInList = 1;
                         valueForThisString = dataPair->value;
                      }
                   }
                   if( !foundInList )
                      retCode = TA_SetOptInputParamInteger( paramsForTALib, i, TA_INTEGER_MIN );
                   else
                      retCode = TA_SetOptInputParamInteger( paramsForTALib, i, valueForThisString );
                }
                curExcelParam++;
             }           
             break;
          }
          if( retCode != TA_SUCCESS )
          {
             displayError(retCode);
             XlfExcel::Instance().MsgBox(funcName, "TA_SetOptInput Failed!");
          }
       }
          
       /*******************************
        * Start Setting Output Params *
        *******************************/
       for( i=0; i < funcInfo->nbOutput; i++ )
       {
          const TA_OutputParameterInfo *paramInfo;
   
          retCode = TA_GetOutputParameterInfo( funcInfo->handle, i, &paramInfo );
          if( retCode != TA_SUCCESS )
          {
             XlfExcel::Instance().MsgBox(funcName, "TA_GetOutputParameterInfo Failed!");
          }
   
          switch( paramInfo->type )
          {
          case TA_Output_Integer:
             retCode = TA_SetOutputParamIntegerPtr( paramsForTALib, i, get_int_output(i) );
             break;
          case TA_Output_Real:
             retCode = TA_SetOutputParamRealPtr( paramsForTALib, i, get_double_output(i) );
             break;
          }                          
          if( retCode != TA_SUCCESS )
          {
             displayError(retCode);
             XlfExcel::Instance().MsgBox(funcName, "TA_SetOutputParamXXXXPtr Failed!");
          }
       }

       /*****************************
        * End Setting Output Params *
        *****************************/
    }
    catch(...)
    {
       FREE_ALL_ALLOC;
       throw;
    }

    // Do the call
    int outBegIdx, outNbElement;
    retCode = TA_CallFunc( paramsForTALib, 0, nbValidData-1, 
                           &outBegIdx, &outNbElement );

    // Check for TA_CallFunc failure.
    if( retCode != TA_SUCCESS )
    {
       // displayError(retCode);
       // XlfExcel::Instance().MsgBox(funcName, "Error Calling TA-Lib Function");
       FREE_ALL_ALLOC;
       return XlfOper::Error(xlerrValue);
    }

    //char buffer[200];
    //sprintf( buffer, "outBeg=%d, outNbElement=%d\n", outBegIdx, outNbElement );
    //XlfExcel::Instance().MsgBox(funcName, buffer );

    // Build the excel output. This time merge all outputs within a large
    // allocated buffer so that XLW can correctly build the output for excel.
    // At the same time, fill up unused section of the output with NAN.
    int outputExcelSizeNeeded = excelArraySize*funcInfo->nbOutput;
    if( !outputExcel || (outputExcelSizeNeeded > outputExcelSize) )
    {
       FREE_IF_NOT_NULL( outputExcel );
       outputExcel = (double *)(TA_Malloc(sizeof(double)*outputExcelSizeNeeded));
       outputExcelSize = outputExcelSizeNeeded;
    }

    if( !outputExcel )
    {
       FREE_ALL_ALLOC;
       return XlfOper::Error(xlerrValue);
    }

    int outIdx=0;
    int nbNan = (funcInfo->nbOutput) * (commonBegIdx+outBegIdx);

    while( nbNan-- )
       outputExcel[outIdx++] = nanValue;

    int outIdxColStart = outIdx;
    unsigned int nbOutput = funcInfo->nbOutput; 
    for( i=0; i < nbOutput; i++ )
    {
       const TA_OutputParameterInfo *paramInfo;
   
       TA_GetOutputParameterInfo( funcInfo->handle, i, &paramInfo );

       int outIdxRow = outIdxColStart;
   
       switch( paramInfo->type )
       {
       case TA_Output_Real:
          {
             double *outputDoublePtr = get_double_output(i);
             for( j=0; j < (unsigned int)outNbElement; j++ )
             {
                outputExcel[outIdxRow] = outputDoublePtr[j];
                outIdxRow += nbOutput;
             }
          }
          break;
       case TA_Output_Integer:
          {
             int *outputIntPtr = get_int_output(i);
             for( j=0; j < (unsigned int)outNbElement; j++ )
             {
                outputExcel[outIdxRow] = (double)outputIntPtr[j];
                outIdxRow += nbOutput;
             }
          }
          break;       
       }

       outIdxColStart++;
       outIdx += outNbElement;
    }

    while( outIdx < excelArraySize )
       outputExcel[outIdx++] = nanValue;

    #if defined( DOWN_UP_CELL_ORDER )
       reverseTAOutput(outputExcel, excelArraySize, nbOutput);
    #endif

    // Package the output using Xlf and we are done!
    XlfOper &retOper = XlfOper(excelArraySize,funcInfo->nbOutput,outputExcel);
    FREE_ALL_ALLOC;
    return retOper;
}


LPXLOPER EXCEL_EXPORT xlTA_Version()
{
   doInitialization(); // Make sure TA-Lib is initialized
   EXCEL_BEGIN;   
   return XlfOper(TA_GetVersionString());
   EXCEL_END;
}

// Make the sumation of the last 'n' cells in the 'range'
LPXLOPER EXCEL_EXPORT xlTA_SumLastInRange( XlfOper range_param, XlfOper n_param )
{
   doInitialization(); // Make sure TA-Lib is initialized
   EXCEL_BEGIN;

   double sum = 0.0;
 
   // Transform the Excel parameter
   std::vector<double> range = range_param.AsDoubleVector(XlfOper::RowMajor);
   int n = n_param.AsInt();

   // Validate the range
   int size = range.size();

   if( n > 0 )
   {
      if( n > size )
         n = size;

      // Add up the values and return
      for( int i=size-1; n > 0; n--, i-- )
         sum += range[i];
   }

   return XlfOper(sum);
   EXCEL_END;
}

LPXLOPER EXCEL_EXPORT xlTA_NAError()
{
   doInitialization(); // Make sure everything is initialized
   EXCEL_BEGIN;
   return XlfOper::Error(xlerrNA);
   EXCEL_END;
}

long EXCEL_EXPORT xlAutoAdd()
{
   #ifdef DEBUG
      XlfExcel::Instance().MsgBox("AutoAdd called...", "Debug");
   #endif
   return doInitialization();
}

long EXCEL_EXPORT xlAutoRemove()
{
   #ifdef DEBUG
      XlfExcel::Instance().MsgBox("AutoRemove called...", "Debug");
   #endif

   return doShutdown();
}

long EXCEL_EXPORT xlAutoOpen()
{
   return doInitialization();
}

long EXCEL_EXPORT xlAutoClose()
{
   return doShutdown();
}

#define CNVT_ARG_EXCEL_TO_TALIB(paramNb) \
        if( p##paramNb.IsError() ) \
           return XlfOper::Error(xlerrValue); \
        argList.push_back(p##paramNb);

#define EXCEL_GLUE_CODE_WITH_1_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_2_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_3_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_4_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_5_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_6_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_7_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_8_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_9_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_10_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_11_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10, XlfOper p11) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      CNVT_ARG_EXCEL_TO_TALIB(11) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_12_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10, XlfOper p11, XlfOper p12) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      CNVT_ARG_EXCEL_TO_TALIB(11) \
      CNVT_ARG_EXCEL_TO_TALIB(12) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_13_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10, XlfOper p11, XlfOper p12, XlfOper p13) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      CNVT_ARG_EXCEL_TO_TALIB(11) \
      CNVT_ARG_EXCEL_TO_TALIB(12) \
      CNVT_ARG_EXCEL_TO_TALIB(13) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_14_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10, XlfOper p11, XlfOper p12, XlfOper p13, XlfOper p14) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      CNVT_ARG_EXCEL_TO_TALIB(11) \
      CNVT_ARG_EXCEL_TO_TALIB(12) \
      CNVT_ARG_EXCEL_TO_TALIB(13) \
      CNVT_ARG_EXCEL_TO_TALIB(14) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#define EXCEL_GLUE_CODE_WITH_15_PARAM(funcName) \
LPXLOPER EXCEL_EXPORT xlTA_##funcName(XlfOper p1, XlfOper p2, XlfOper p3, XlfOper p4, XlfOper p5, XlfOper p6, XlfOper p7, XlfOper p8, XlfOper p9, XlfOper p10, XlfOper p11, XlfOper p12, XlfOper p13, XlfOper p14, XlfOper p15) \
{ \
doInitialization(); \
EXCEL_BEGIN; \
      std::vector<XlfOper> argList; \
      CNVT_ARG_EXCEL_TO_TALIB(1) \
      CNVT_ARG_EXCEL_TO_TALIB(2) \
      CNVT_ARG_EXCEL_TO_TALIB(3) \
      CNVT_ARG_EXCEL_TO_TALIB(4) \
      CNVT_ARG_EXCEL_TO_TALIB(5) \
      CNVT_ARG_EXCEL_TO_TALIB(6) \
      CNVT_ARG_EXCEL_TO_TALIB(7) \
      CNVT_ARG_EXCEL_TO_TALIB(8) \
      CNVT_ARG_EXCEL_TO_TALIB(9) \
      CNVT_ARG_EXCEL_TO_TALIB(10) \
      CNVT_ARG_EXCEL_TO_TALIB(11) \
      CNVT_ARG_EXCEL_TO_TALIB(12) \
      CNVT_ARG_EXCEL_TO_TALIB(13) \
      CNVT_ARG_EXCEL_TO_TALIB(14) \
      CNVT_ARG_EXCEL_TO_TALIB(15) \
      return doTACall(#funcName,&argList[0],argList.size()); \
EXCEL_END; \
}

#include "excel_glue.c"

}
