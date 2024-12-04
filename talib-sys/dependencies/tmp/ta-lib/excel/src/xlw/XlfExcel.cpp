/*
 Copyright (C) 1998, 1999, 2001, 2002 Jérôme Lecomte
 
 This file is part of XLW, a free-software/open-source C++ wrapper of the
 Excel C API - http://xlw.sourceforge.net/
 
 XLW is free software: you can redistribute it and/or modify it under the
 terms of the XLW license.  You should have received a copy of the
 license along with this program; if not, please email xlw-users@lists.sf.net
 
 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
*/

/*!
\file XlfExcel.cpp
\brief Implements the classes XlfExcel.
*/

// $Id: XlfExcel.cpp 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfExcel.h>
#ifdef PORT_USE_OLD_C_HEADERS
    #include <stdio.h>
#else
    #include <cstdio>
#endif
#include <stdexcept>
#include <xlw/XlfOper.h>

// Stop header precompilation
#ifdef _MSC_VER
#pragma hdrstop
#endif

#ifndef NDEBUG
#include <xlw/XlfExcel.inl>
#endif

extern "C"
{
  //! Main API function to Excel.
  int (__cdecl *Excel4)(int xlfn, LPXLOPER operRes, int count,...);
  //! Main API function to Excel, passing the argument as an array.
  int (__stdcall *Excel4v)(int xlfn, LPXLOPER operRes, int count, LPXLOPER far opers[]);
}

XlfExcel *XlfExcel::this_ = 0;

//! Internal implementation of XlfExcel.
struct XlfExcelImpl
{
  //! Ctor.
  XlfExcelImpl(): handle_(0) {}
  //! Handle to the DLL module.
  HINSTANCE handle_;
};

/*!
You always have the choice with the singleton in returning a pointer or
a reference. By returning a reference and declaring the copy ctor and the
assignment otor private, we limit the risk of a wrong use of XlfExcel
(typically duplication).
*/
XlfExcel& XlfExcel::Instance()
{
  if (!this_)
  {
    this_ = new XlfExcel;
    // intialize library first because log displays
    // XLL name in header of log window
    this_->InitLibrary();
  }
  return *this_;
}

/*!
If not title is specified, the message is assumed to be an error log
*/
void XlfExcel::MsgBox(const char *errmsg, const char *title)
{
  LPVOID lpMsgBuf;
  // retrieve message error from system err code
  if (!title)
  {
    DWORD err = GetLastError();
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                  NULL,
                  err,
                  MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
                  (LPTSTR) &lpMsgBuf,
                  0,
                  NULL);
    // Process any inserts in lpMsgBuf.
    char completeMessage[255];
    sprintf(completeMessage,"%s due to error %d :\n%s", errmsg, err, (LPCSTR)lpMsgBuf);
    MessageBox(NULL, completeMessage,"XLL Error", MB_OK | MB_ICONINFORMATION);
    // Free the buffer.
    LocalFree(lpMsgBuf);
  }
  else
    MessageBox(NULL, errmsg, title, MB_OK | MB_ICONINFORMATION);
  return;
}

/*!
If msg is 0, the status bar is cleared.
*/
void XlfExcel::SendMessage(const char *msg)
{
  if (msg)
    Call(xlcMessage,0,2,XlfOper(true),XlfOper(msg));
  else
    Call(xlcMessage,0,1,XlfOper(false));
  return;
}

bool XlfExcel::IsEscPressed() const
{
  XlfOper ret;
  Call(xlAbort,ret,1,XlfOper(false));
  return ret.AsBool();
}

XlfExcel::XlfExcel(): impl_(0), offset_(0)
{
  impl_ = new XlfExcelImpl();
  return;
}

XlfExcel::~XlfExcel()
{
  FreeMemory(true);
  delete impl_;
  this_ = 0;
  return;
}

/*!
Load \c XlfCALL32.DLL to interface excel (this library is shipped with Excel)
and link it to the XLL.
*/
void XlfExcel::InitLibrary()
{
  HINSTANCE handle = LoadLibrary("XLCALL32.DLL");
  if (handle == 0)
    throw std::runtime_error("Could not load library XLCALL32.DLL");
  Excel4 = (int (__cdecl *)(int, struct xloper *, int, ...))GetProcAddress(handle,"Excel4");
  if (Excel4 == 0)
    throw std::runtime_error("Could not get address of Excel4 callback");
  Excel4v = (int (__stdcall *)(int, struct xloper *, int, struct xloper *[]))GetProcAddress(handle,"Excel4v");
  if (Excel4v == 0)
    throw std::runtime_error("Could not get address of Excel4v callback");
  impl_->handle_ = handle;
  return;
}

std::string XlfExcel::GetName() const
{
  std::string ret;
  XlfOper xName;
  int err = Call(xlGetName, (LPXLOPER)xName, 0);
  if (err != xlretSuccess)
    std::cerr << __HERE__ << "Could not get DLL name" << std::endl;
  else
    ret=xName.AsString();
  return ret;
}

#ifdef __MINGW32__
int __cdecl XlfExcel::Call(int xlfn, LPXLOPER pxResult, int count, ...) const
#else
int cdecl XlfExcel::Call(int xlfn, LPXLOPER pxResult, int count, ...) const
#endif
{
#ifdef _ALPHA_
  /*
  * On the Alpha, arguments may be passed in via registers instead of
  * being located in a contiguous block of memory, so we must use the
  * va_arg functions to retrieve them instead of simply walking through
  * memory.
  	*/
  va_list argList;
  LPXLOPER *plpx = alloca(count*sizeof(LPXLOPER));
#endif

#ifdef _ALPHA_
  /* Fetch all of the LPXLOPERS and copy them into plpx.
  * plpx is alloca'ed and will automatically be freed when the function
  * exits.
  */
  va_start(argList, count);
  for (i = 0; i<count; i++)
    plpx[i] = va_arg(argList, LPXLOPER);
  va_end(argList);
#endif

#ifdef _ALPHA_
  return Callv(xlfn, pxResult, count, plpx);
#else
  return Callv(xlfn, pxResult, count, (LPXLOPER *)(&count + 1));
#endif
}

/*!
If one (or more) cells refered as argument is(are) uncalculated, the framework
throw an exception and return immediately to Excel.
 
If \c pxResult is not 0 and has auxilliary memory, flags it for deletion 
with XlfOper::xlbitCallFreeAuxMem.
 
\sa XlfOper::~XlfOper
*/
int XlfExcel::Callv(int xlfn, LPXLOPER pxResult, int count, LPXLOPER pxdata[]) const
{
#ifndef NDEBUG
  for (size_t i = 0; i<size_t(count);++i)
    if (!pxdata[i])
    {
      if (xlfn & xlCommand)
        std::cerr << __HERE__ << "xlCommand | " << (xlfn & 0x0FFF) << std::endl;
      if (xlfn & xlSpecial)
        std::cerr << __HERE__ << "xlSpecial | " << (xlfn & 0x0FFF) << std::endl;
      if (xlfn & xlIntl)
        std::cerr << __HERE__ << "xlIntl | " << (xlfn & 0x0FFF) << std::endl;
      if (xlfn & xlPrompt)
        std::cerr << __HERE__ << "xlPrompt | " << (xlfn & 0x0FFF) << std::endl;
      std::cerr << __HERE__ << "0 pointer passed as argument #" << i << std::endl;
    }
#endif
  int xlret = Excel4v(xlfn, pxResult, count, pxdata);
  if (pxResult)
  {
    int type = pxResult->xltype;

    bool hasAuxMem = (type & xltypeStr ||
                      type & xltypeRef ||
                      type & xltypeMulti ||
                      type & xltypeBigData);
    if (hasAuxMem)
      pxResult->xltype |= XlfOper::xlbitFreeAuxMem;
  }
  return xlret;
}

namespace
{

//! Needed by IsCalledByFuncWiz.
typedef struct _EnumStruct
{
  bool bFuncWiz;
  short hwndXLMain;
}
EnumStruct, FAR * LPEnumStruct;

//! Needed by IsCalledByFuncWiz.
bool CALLBACK EnumProc(HWND hwnd, LPEnumStruct pEnum)
{
  const size_t CLASS_NAME_BUFFER = 50;

  // first check the class of the window.  Will be szXLDialogClass
  // if function wizard dialog is up in Excel
  char rgsz[CLASS_NAME_BUFFER];
  GetClassName(hwnd, (LPSTR)rgsz, CLASS_NAME_BUFFER);
  if (2 == CompareString(MAKELCID(MAKELANGID(LANG_ENGLISH,
                                  SUBLANG_ENGLISH_US),SORT_DEFAULT), NORM_IGNORECASE,
                         (LPSTR)rgsz,  (lstrlen((LPSTR)rgsz)>lstrlen("bosa_sdm_XL"))
                         ? lstrlen("bosa_sdm_XL"):-1, "bosa_sdm_XL", -1))
  {
    if(LOWORD((DWORD) GetParent(hwnd)) == pEnum->hwndXLMain)
    {
      pEnum->bFuncWiz = TRUE;
      return false;
    }
  }
  // no luck - continue the enumeration
  return true;
}
} // empty namespace

bool XlfExcel::IsCalledByFuncWiz() const
{
  XLOPER xHwndMain;
  EnumStruct    enm;

  if (Excel4(xlGetHwnd, &xHwndMain, 0) == xlretSuccess)
  {
    enm.bFuncWiz = false;
    enm.hwndXLMain = xHwndMain.val.w;
    EnumWindows((WNDENUMPROC) EnumProc,
                (LPARAM) ((LPEnumStruct)  &enm));
    return enm.bFuncWiz;
  }
  return false;    //safe case: Return false if not sure
}
