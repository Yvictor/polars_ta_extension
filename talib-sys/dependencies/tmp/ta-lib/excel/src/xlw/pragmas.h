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

#ifndef INC_pragmas_H
#define INC_pragmas_H

/*!
\file pragmas.h
\brief Pragmas directives are to be included before any header.

There is not much about this file, it mainly deactives the warning C4251,
C4275 and C4786. The later also guards against a bug in MSVC 6.0 that
causes C4786 to reappear even though you already deactivated it. see
http://www.deja.com for more information about C4786.
*/

// $Id: pragmas.h 152 2003-04-20 04:42:47Z fortier $

#if defined(DEBUG_HEADERS)
#pragma DEBUG_HEADERS
#endif

#if defined(_MSC_VER)
#pragma once

//! Work around used by PORT_QUOTE
#define PORT_QUOTE(x) #x
//! Encloses the argument between quotes
#define PORT_QUOTE_VALUE(x) PORT_QUOTE(x)
//! Displays the message passed in argument (use quotes) with file and line number.
#define PORT_MESSAGE(msg) message(__FILE__"("PORT_QUOTE_VALUE(__LINE__)") : " msg)

// C4251: <identifier> : class <XXX> needs to have dll-interface
// to be used by clients of class <YYY>
#pragma warning( disable : 4251 )

// C4275: non dll-interface class <XXX> used as base for
// dll-interface class <YYY>
#pragma warning( disable : 4275 )

// C4786:'identifier' : identifier was truncated to 'number' characters
// in the debug information
// You should include the pragmas.h *before* any STL header. This trick
// warns you if you fail to include it first.
#if defined(_YVALS)
#pragma message(__FILE__ "(37) : USER WNG : pragma.h included too late to deactive warning 4786.")
#endif
#pragma warning( disable : 4786 )
#include <yvals.h>
#pragma warning( default : 4786 )
#pragma warning( disable : 4786 )

#endif

#endif