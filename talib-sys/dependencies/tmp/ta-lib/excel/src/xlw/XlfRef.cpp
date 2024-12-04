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
\file XlfRef.cpp
\brief Implements the XlfRef class.
*/

// $Id: XlfRef.cpp 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfRef.h>
#include <xlw/XlfOper.h>
#include <xlw/XlfException.h>
#include <xlw/macros.h>
#include <iostream>

// Stop header precompilation
#ifdef _MSC_VER
#pragma hdrstop
#endif

#ifndef NDEBUG
#include <xlw/XlfRef.inl>
#endif

/*!
\note In debug build, generates a message if the request is in the range.
*/
XlfOper XlfRef::operator()(WORD r, BYTE c) const
{
#if !defined(NDEBUG)
	if (rowbegin_ + r > rowend_ || colbegin_ + c > colend_)
  {
    std::cerr << __HERE__ << "XlfRef access out of range" << std::endl;
  }
#endif
	XlfOper res;
	res.Set(XlfRef(rowbegin_ + r, colbegin_ + c, sheetId_));
	return res;
}
