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
\file XlfRef.inl
\brief Implements inline methods of class XlfRef.
*/

// $Id: XlfRef.inl 152 2003-04-20 04:42:47Z fortier $

#ifdef NDEBUG
#define INLINE inline
#else
#define INLINE
#endif

INLINE XlfRef::XlfRef()
    :rowbegin_(0), rowend_(0), colbegin_(0), colend_(0), sheetId_(0)
{}

INLINE XlfRef::XlfRef(WORD top, BYTE left, WORD bottom, BYTE right, DWORD sheetId)
    :rowbegin_(top), rowend_(bottom + 1), colbegin_(left), colend_(right + 1), sheetId_(sheetId)
{}

INLINE XlfRef::XlfRef(WORD row, BYTE col, DWORD sheetId)
    :rowbegin_(row), rowend_(row + 1), colbegin_(col), colend_(col + 1), sheetId_(sheetId)
{}

INLINE WORD XlfRef::GetRowBegin() const
{
  return rowbegin_;
}

INLINE WORD XlfRef::GetRowEnd() const
{
  return rowend_;
}

INLINE BYTE XlfRef::GetColBegin() const
{
  return colbegin_;
}

INLINE BYTE XlfRef::GetColEnd() const
{
  return colend_;
}

INLINE DWORD XlfRef::GetSheetId() const
{
  return sheetId_;
}

INLINE BYTE XlfRef::GetNbCols() const
{
  return colend_-colbegin_;
}

INLINE WORD XlfRef::GetNbRows() const
{
  return rowend_-rowbegin_;
}

INLINE void XlfRef::SetRowBegin(WORD rowbegin)
{
  rowbegin_ = rowbegin;
}

INLINE void XlfRef::SetRowEnd(WORD rowend)
{
  rowend_ = rowend;
}

INLINE void XlfRef::SetColBegin(BYTE colbegin)
{
  colbegin_ = colbegin;
}

INLINE void XlfRef::SetColEnd(BYTE colend)
{
  colend_ = colend;
}

INLINE void XlfRef::SetSheetId(DWORD sheetId)
{
  sheetId_ = sheetId;
}