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
\file XlfArgDesc.cpp
\brief Implements the XlfArgDesc class.
*/

// $Id: XlfArgDesc.cpp 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfArgDesc.h>
#include <xlw/macros.h>
#include <iostream>

// Stop header precompilation
#ifdef _MSC_VER
#pragma hdrstop
#endif

void XlfArgDesc::CheckNameLength()
{
  if (name_.length() >= 19)
    std::cerr << __HERE__ << "Argument name \"" << name_.c_str()
    << "\" may be too long to fit the in the function wizard" << std::endl;
};

XlfArgDesc::XlfArgDesc()
{}

/*!
\param name Name of the argument.
\param comment Help string associated to the argument.
\param type Argument type (defaults to R for XLOPER *). Other argument
type can be found in Excel documentation under the keyword \e register.
Note that B stands for double or date, I for 16 bits integer, J for
32 bits integer. I rarely use the other types.
*/
XlfArgDesc::XlfArgDesc(const std::string& name,
                       const std::string& comment,
                       char type)
    : name_(name), comment_(comment), type_(type)
{
  CheckNameLength();
}

XlfArgDesc::~XlfArgDesc()
{}

void XlfArgDesc::SetName(const std::string& name)
{
  name_ = name;
  CheckNameLength();
}

const std::string& XlfArgDesc::GetName() const
{
  return name_;
}

void XlfArgDesc::SetComment(const std::string& comment)
{
  comment_ = comment;
}

const std::string& XlfArgDesc::GetComment() const
{
  return comment_;
}

char XlfArgDesc::GetType() const
{
  return type_;
}
