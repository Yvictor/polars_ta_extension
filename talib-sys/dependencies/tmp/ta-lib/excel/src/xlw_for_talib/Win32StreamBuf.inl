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
 * \file Win32StreamBuf.inl
 * \brief Inline implementation of the class Win32StreamBuf
 * \group utils
 */

// $Id: Win32StreamBuf.inl 154 2003-04-20 04:53:06Z fortier $

#ifdef NDEBUG
#define INLINE inline
#else
#define INLINE
#endif

/*!
This method is called to dump stuff in the put area out to the file.
We intercept it to send to debug window.
*/
INLINE int Win32StreamBuf::sync()
{
    SendToDebugWindow();
    buf_.erase();
	return 0;
}

/*!
This method is called to dump stuff in the put area out to the file.
We intercept it to send to debug window.
*/
INLINE int Win32StreamBuf::overflow(int ch)
{
    if (!traits_type::eq_int_type(traits_type::eof(), ch))
    {
        buf_.append(1, traits_type::to_char_type(ch));         // 1
    }
    else
    {
        return sync();
    }
    return traits_type::not_eof(ch);
}

