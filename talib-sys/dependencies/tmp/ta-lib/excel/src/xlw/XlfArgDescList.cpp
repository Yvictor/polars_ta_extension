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
\file XlfArgDescList.cpp
\brief Implements the XlfArgDescList class.
*/

// $Id: XlfArgDescList.cpp 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfArgDescList.h>

// Stop header precompilation
#ifdef _MSC_VER
#pragma hdrstop
#endif

XlfArgDescList::XlfArgDescList()
{}

XlfArgDescList::XlfArgDescList(const XlfArgDescList& list)
{
  arguments_ = list.arguments_;
}

XlfArgDescList::XlfArgDescList(const XlfArgDesc& first)
{
  arguments_.push_back(first);
}

XlfArgDescList& XlfArgDescList::operator+(const XlfArgDesc& newarg)
{
  arguments_.push_back(newarg);
  return *this;
}

XlfArgDescList::iterator XlfArgDescList::begin()
{
  return arguments_.begin();
}

XlfArgDescList::const_iterator XlfArgDescList::begin() const
{
  return arguments_.begin();
}

XlfArgDescList::iterator XlfArgDescList::end()
{
  return arguments_.end();
}

XlfArgDescList::const_iterator XlfArgDescList::end() const
{
  return arguments_.end();
}

size_t XlfArgDescList::size() const
{
  return arguments_.size();
}

XlfArgDescList operator+(const XlfArgDesc& lhs, const XlfArgDesc& rhs)
{
  return XlfArgDescList(lhs)+rhs;
}