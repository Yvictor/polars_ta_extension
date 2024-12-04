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

#ifndef INC_XlfException_H
#define INC_XlfException_H

/*!
\file XlfException.h
\brief Declares XlfException class hierarchy.
*/

// $Id: XlfException.h 152 2003-04-20 04:42:47Z fortier $

#include <xlw/EXCEL32_API.h>
#include <string>
#include <exception>

#if defined(_MSC_VER)
#pragma once
#endif

#if defined(DEBUG_HEADERS)
#pragma DEBUG_HEADERS
#endif

class EXCEL32_API XlfOper;

//! Excel emergency exceptions
/*!
It is important to distinguish exception thrown as XlfException
from others because they will be caught differently by the wrapper.
See EXCEL_END.

\warning These exceptions don't necessarly correspond to errors, see
for example XlfExceptionUncalculated.

\sa ThrowOnError
*/
class EXCEL32_API XlfException : public std::exception
{
public:
  //! Message string ctor.
  XlfException(const std::string& what = "");
  //! std::exception interface
  const char* what() const throw ();

private:
    std::string what_;
};

//! Argument cell not calculated.
/*!
A cell was requested whose value has been invalidated.

When it occurs, the framework should return immediately
to excel to let it calculate the cell. Excel will then
call again the function immediately after the argument
was re-calculated.

No message is passed to XlfException to speed up return
to MS Excel.
*/
class EXCEL32_API XlfExceptionUncalculated: public XlfException
{};

//! Abort requested.
/*!
Usually thrown by the user after XlfExcel::IsEscPressed had return true.
*/
class EXCEL32_API XlfExceptionAbort: public XlfException
{
public:
  XlfExceptionAbort(): XlfException("abort") {}
};

//! Stack overflow.
class EXCEL32_API XlfExceptionStackOverflow: public XlfException
{
public:
  XlfExceptionStackOverflow(): XlfException("stack overflow") {}
};

#ifdef NDEBUG
#include <xlw/XlfException.inl>
#endif

#endif
