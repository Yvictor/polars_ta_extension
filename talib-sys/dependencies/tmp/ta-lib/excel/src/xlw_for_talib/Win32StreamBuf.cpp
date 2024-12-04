/*
 Copyright (C) 1998, 1999, 2001, 2002 Jérôme Lecomte
 
 This file is part of xlw, a free-software/open-source C++ wrapper of the
 Excel C API - http://xlw.sourceforge.net/
 
 xlw is free software: you can redistribute it and/or modify it under the
 terms of the xlw license.  You should have received a copy of the
 license along with this program; if not, please email xlw-users@lists.sf.net
 
 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
*/

/*!
 * \file Win32StreamBuf.cpp
 * \brief Implementation of the class Win32StreamBuf
 * \ingroup utils
 */

// $Id: Win32StreamBuf.cpp 154 2003-04-20 04:53:06Z fortier $

#ifdef _WIN32

#include "Win32StreamBuf.h"

#ifndef NDEBUG
#include "Win32StreamBuf.inl"
#endif

#include <cassert>

#define STRICT
#include <windows.h>

#if !(_WIN32_WINNT >= 0x0400) && !(_WIN32_WINDOWS > 0x0400)
//! Helper method if IsDebuggerPresent is not available.
/*!
This ersatz for IsDebuggerPresent return true if the program
was compiled with NDEBUG flag and false otherwise.
*/
inline bool IsDebuggerPresent()
{
#ifdef NDEBUG
    return false;
#else
	return true;
#endif
}
#endif

/*!
This is where the work happens - We grab a copy of what is in 
the put area and send it to the debug window using OutputDebugString.
*/
void Win32StreamBuf::SendToDebugWindow()
{
    if (IsDebuggerPresent() && !buf_.empty())
		::OutputDebugString(buf_.c_str());
}

#endif // _WIN32
