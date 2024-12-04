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
\file XlfAbstractCmdDesc.cpp
\brief Implements the XlfAbstractCmdDesc class.
*/

// $Id: XlfAbstractCmdDesc.cpp 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfAbstractCmdDesc.h>
#include <xlw/XlfExcel.h>
#include <xlw/XlfException.h>
#include <xlw/macros.h>
#include <iostream>

// Stop header precompilation
#ifdef _MSC_VER
#pragma hdrstop
#endif

/*!
\param name Name of the command.
\param alias Alias in Excel for the command.
\param comment Help string associated with the comment
*/
XlfAbstractCmdDesc::XlfAbstractCmdDesc(const std::string& name,
                                       const std::string& alias,
                                       const std::string& comment)
    :name_(name), alias_(alias), comment_(comment)
{}

XlfAbstractCmdDesc::~XlfAbstractCmdDesc()
{}

/*!
Performs the parts of the Registration that are common to a registration
of all the subclasses of XlfAbstractCmdDesc. It then calls the pure
virtual method DoRegister for the subclass dependant parts of the
algorithm.
*/
void XlfAbstractCmdDesc::Register() const
{
  std::string dllName = XlfExcel::Instance().GetName();
  if (dllName.empty())
    throw std::runtime_error("Could not get library name");
  int err = DoRegister(dllName);
  if (err != xlretSuccess)
    std::cerr << __HERE__ << "Error " << err << " while registering " << GetAlias().c_str() << std::endl;
  return;
}

void XlfAbstractCmdDesc::Unregister()
{
  return;
}

void XlfAbstractCmdDesc::SetName(const std::string& name)
{
  name_ = name;
}

const std::string& XlfAbstractCmdDesc::GetName() const
{
  return name_;
}

void XlfAbstractCmdDesc::SetAlias(const std::string& alias)
{
  alias_ = alias;
}

const std::string& XlfAbstractCmdDesc::GetAlias() const
{
  return alias_;
}

void XlfAbstractCmdDesc::SetComment(const std::string& comment)
{
  comment_ = comment;
}

const std::string& XlfAbstractCmdDesc::GetComment() const
{
  return comment_;
}

