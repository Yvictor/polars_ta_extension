# Microsoft Developer Studio Generated NMAKE File, Based on xlw_for_talib.dsp
!IF "$(CFG)" == ""
CFG=XLW_FOR_TALIB - WIN32 RELEASE
!MESSAGE No configuration specified. Defaulting to XLW_FOR_TALIB - WIN32 RELEASE.
!ENDIF 

!IF "$(CFG)" != "xlw_for_talib - Win32 Release"
!MESSAGE Invalid configuration "$(CFG)" specified.
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "xlw_for_talib.mak" CFG="XLW_FOR_TALIB - WIN32 RELEASE"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "xlw_for_talib - Win32 Release" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE 
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

OUTDIR=.\..\..\temp
INTDIR=.\..\..\temp
# Begin Custom Macros
OutDir=.\..\..\temp
# End Custom Macros

!IF "$(RECURSE)" == "0" 

ALL : "..\..\ta-lib.xll" "$(OUTDIR)\xlw_for_talib.bsc"

!ELSE 

ALL : "xlw - Win32 Release" "..\..\ta-lib.xll" "$(OUTDIR)\xlw_for_talib.bsc"

!ENDIF 

!IF "$(RECURSE)" == "1" 
CLEAN :"xlw - Win32 ReleaseCLEAN" 
!ELSE 
CLEAN :
!ENDIF 
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\Win32StreamBuf.obj"
	-@erase "$(INTDIR)\Win32StreamBuf.sbr"
	-@erase "$(INTDIR)\xlw_for_talib.obj"
	-@erase "$(INTDIR)\xlw_for_talib.sbr"
	-@erase "$(OUTDIR)\ta-lib.exp"
	-@erase "$(OUTDIR)\ta-lib.lib"
	-@erase "$(OUTDIR)\xlw_for_talib.bsc"
	-@erase "..\..\ta-lib.xll"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /MD /W3 /GX /O2 /I "..\..\..\c\include" /I "..\..\..\c\src\ta_abstract" /I "..\..\..\c\src\ta_common" /I ".." /D "DOWN_UP_CELL_ORDER" /D "NDEBUG" /D "WIN32" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\xlw_for_talib.pch" /YX /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

.c{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

MTL=midl.exe
MTL_PROJ=/nologo /D "NDEBUG" /mktyplib203 /win32 
RSC=rc.exe
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\xlw_for_talib.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\Win32StreamBuf.sbr" \
	"$(INTDIR)\xlw_for_talib.sbr"

"$(OUTDIR)\xlw_for_talib.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /dll /incremental:no /pdb:"$(OUTDIR)\ta-lib.pdb" /machine:I386 /out:"..\..\ta-lib.xll" /implib:"$(OUTDIR)\ta-lib.lib" 
LINK32_OBJS= \
	"$(INTDIR)\Win32StreamBuf.obj" \
	"$(INTDIR)\xlw_for_talib.obj" \
	"..\..\..\c\lib\ta_libc_cdr.lib" \
	"$(OUTDIR)\xlw.lib"

"..\..\ta-lib.xll" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<


!IF "$(NO_EXTERNAL_DEPS)" != "1"
!IF EXISTS("xlw_for_talib.dep")
!INCLUDE "xlw_for_talib.dep"
!ELSE 
!MESSAGE Warning: cannot find "xlw_for_talib.dep"
!ENDIF 
!ENDIF 


!IF "$(CFG)" == "xlw_for_talib - Win32 Release"

!IF  "$(CFG)" == "xlw_for_talib - Win32 Release"

"xlw - Win32 Release" : 
   cd "\Latest\TA-Lib\ta-lib\excel\src"
   $(MAKE) /$(MAKEFLAGS) /F ".\ta-lib.mak" CFG="xlw - Win32 Release" 
   cd ".\xlw_for_talib"

"xlw - Win32 ReleaseCLEAN" : 
   cd "\Latest\TA-Lib\ta-lib\excel\src"
   $(MAKE) /$(MAKEFLAGS) /F ".\ta-lib.mak" CFG="xlw - Win32 Release" RECURSE=1 CLEAN 
   cd ".\xlw_for_talib"

!ENDIF 

SOURCE=.\Win32StreamBuf.cpp

"$(INTDIR)\Win32StreamBuf.obj"	"$(INTDIR)\Win32StreamBuf.sbr" : $(SOURCE) "$(INTDIR)"


SOURCE=.\xlw_for_talib.cpp

"$(INTDIR)\xlw_for_talib.obj"	"$(INTDIR)\xlw_for_talib.sbr" : $(SOURCE) "$(INTDIR)"



!ENDIF 

