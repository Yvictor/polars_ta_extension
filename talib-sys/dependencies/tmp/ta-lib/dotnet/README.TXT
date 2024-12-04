* TA-Lib for .NET *

How to use TA-Lib with .NET?
============================
Copy and distribute TA-Lib-Core.dll in
the same directory as your application.

Two versions are available.

(1) Assembly for Release:
  ta-lib\dotnet\src\Release\TA-Lib-Core.dll

(2) Assembly for Debug:
  ta-lib\dotnet\src\Debug\TA-Lib-Core.dll

The assembly are not shared (or strongly named) and
consequently does not require to be added to the GAC.

The assembly does not contain language specific feature and
can be used with any .NET language (C#,VB.NET,C++,J#...).

These assemblies can be used with Mono as well.

How to rebuild the TA-LIB assembly?
===================================
Using Visual Studio open ta-lib\dotnet\src\TA-Lib.sln and
rebuild TA-Lib-Core.

Can I re-distribute the TA-Lib assembly?
========================================
TA-Lib can be distributed with commercial software
for no fee. You must respect the LICENSE.TXT included
in this package.

How to uninstall the library?
=============================
Just delete the ta-lib directory and assembly.
TA-LIB does not touch your system settings, 
the GAC or the registry.

Comments/Help
=============
 http://ta-lib.org
 http://tadoc.org
