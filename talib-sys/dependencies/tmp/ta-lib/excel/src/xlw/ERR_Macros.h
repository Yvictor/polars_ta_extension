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

// $Id: ERR_Macros.h 152 2003-04-20 04:42:47Z fortier $

#ifndef INC_ERR_Macros_H
#define INC_ERR_Macros_H

/*!
\file ERR_Macros.h
\brief Basic error handler
*/

#include <xlw/port.h>

#ifdef PORT_PRAGMA
    #pragma once
#endif

#include <windows.h>
#ifdef PORT_USE_OLD_IO_HEADERS
    #ifdef PORT_NO_LONG_FILE_NAMES
        #include <strstrea.h>
    #else
        #include <strstream.h>
    #endif
#else
    #include <strstream>
#endif

//! Log a message to the user interface.
/*!
You can customize the output of the error message (currently a message box) and
use your own error handling mechanism.
*/
#if defined(NDEBUG) || !defined(_MSC_VER)
    #define ERR_LOG_INTERNAL(msg) ::MessageBox(0,msg,"C++ Excel32 wrapper Log",MB_OK)
#else
    #define ERR_LOG_INTERNAL(msg) OutputDebugString(msg)
#endif

//! Converts a data stream to a 0-terminated string and passes it the LOG macro.
/*!
\param message Whatever type (or serie of types) that has a stream
operator defined. For instance, you could use it like
\code double f=0.0;
ERR_LOG("Here the value of f is \"" << f << "\"");
\endcode

\warning The buffer has a limited size set to 1024 bytes.
The line might be troncated if it is too long.

The enclosing
\code if (true) { ... } else \endcode
is designed to avoid warning in condition code like the following. See
\ref CppFaqLite.
\code
if (...)
  ERR_LOG();
\endcode
*/
#define ERR_LOG(message) if (true) \
{ \
	char tmp___[1024]; \
	ostrstream os____(tmp___,1024); \
	os____ << __FILE__ << "(" << __LINE__ << "): " << message << '\n' << ends; \
	ERR_LOG_INTERNAL(tmp___); \
} else

//! Wrapper for the try keyword.
#define ERR_TRY try
//! Wrapper for catch keyword.
#define ERR_CATCH catch
//! Wrapper for throw keyword without argument.
/*!
You might use it to forward an exception further up in the call stack
after it's been catched by a catch block.
*/
#define ERR_RETHROW throw
//! Wrapper for cathing an exception and forward it immediately
#define ERR_CATCH_AND_THROW { }
//! Wrapper for a catch of all exceptions.
#define ERR_CATCH_ALL catch (...)
//! Wrapper for the throw of an exception with message.
/*! Adds the name of the exception thrown and calls ERR_LOG() macro
    with the message.
	\sa ERR_LOG()
*/





#define ERR_THROW_MSG(except, message) if (true) \
{ \
	char tmp__[1024]; \
	ostrstream os___(tmp__,1024); \
	os___ << message << ends; \
	ERR_LOG("EXCEPTION (" #except ") : " << message); \
	throw except(tmp__); \
} else




//! Wrapper for throw of an exception without message.
#define ERR_THROW(exception) { throw exception(); }
//! Wrapper for assertion test.
/*!
Checks if \e condition is \c true. If not, calls ERR_THROW_MSG() with
\e exception and \e message as arguments.
These assertions are \e not \e removed for \e release versions.
\sa ERR_THROW_MSG()
\bug In conditional statement, see ERR_LOG().
*/
#define ERR_CHECKX(condition, exception, message) if (!(condition)) \
{ ERR_THROW_MSG(exception, message); }

//! Wrapper for warning message sending.
/*! Forward the message to ERR_LOG() prefixed by the text "WARNING :".
	\sa ERR_LOG()
	\bug In conditional statement, see ERR_LOG().
*/
#define ERR_LOGW(message) { ERR_LOG("WARNING : " << message); }

//! Wrapper for warning test.
/*!
Checks if \e condition is \c true. If not, calls ERR_LOGW() with
\e message as arguments.
These assertions \b still \b hold for \e release versions.
\sa ERR_LOGW().
\bug In conditional statement, see ERR_LOG().
*/
#define ERR_CHECKW(condition, msg) if (!(condition)) \
{ ERR_LOGW(msg); }

#ifndef NDEBUG
//! Same as ERR_CHECKX(), removed from code if NDEBUG is not defined.
#define ERR_CHECKX2(condition, exception, message) ERR_CHECKX(condition, exception, "(DBG) " << message)
//! Same as ERR_CHECKW(), removed from code if NDEBUG is not defined.
#define ERR_CHECKW2(condition, msg) ERR_CHECKW(condition, "(DBG) " << msg)
//! Same as ERR_LOGW(), removed from code if NDEBUG is not defined.
#define ERR_LOGW2(msg) ERR_LOGW("(DBG) " << msg)
//! Same as ERR_LOG(), removed from code if NDEBUG is not defined.
#define ERR_LOG2(msg) ERR_LOG("(DBG) " << msg)
#else
#define ERR_CHECKX2(condition, exception, message)
#define ERR_CHECKW2(condition, message)
#define ERR_LOGW2(msg)
#define ERR_LOG2(msg)
#endif // DEBUG

#endif