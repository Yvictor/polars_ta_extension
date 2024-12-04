How to rebuild the Excel add-in?
================================

You need Visual Studio 2005 to re-build.

Step #1 : Build ta_libc_cdr.lib
-----------------------------------
(1) Open workspace: ta-lib\c\ide\vs2005\lib_proj\ta_lib.sln
(2) Select "ta_libc" as the active project (will appear in bold)
(3) Select the configuration "Win32 CDR Multithread DLL Release".
(4) Build "ta_libc". The file "ta_libc_cdr.lib" will be created in ta-lib\c\lib
(5) Close this workspace.

Step #2 : Build ta-lib.xll or ta-lib-reverse.xll
-------------------------------------------------
(1) Open workspace: ta-lib\excel\src\ta-lib.sln
(2) Select "xlw_for_talib" as the active project.
(3) Select either the configuration "Release" or "Release Reverse"
(4) Build "xlw_for_talib". The file "ta-lib.xll" or "ta-lib-reverse.xll" 
    will be created in the directory ta-lib\excel


Further information about XLW can be found here:
   http://xlw.sourceforge.net

Community Forum: 
   http://tadoc.org

