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

#ifndef INC_XlfAbstractCmdDesc_H
#define INC_XlfAbstractCmdDesc_H

/*!
\file XlfAbstractCmdDesc.h
\brief Declares class XlfAbstractCmdDesc.
*/

// $Id: XlfAbstractCmdDesc.h 152 2003-04-20 04:42:47Z fortier $

#include <xlw/EXCEL32_API.h>
#include <string>

#if defined(_MSC_VER)
#pragma once
#endif

#if defined(DEBUG_HEADERS)
#pragma DEBUG_HEADERS
#endif

//! Abstract command.
class EXCEL32_API XlfAbstractCmdDesc
{
public:
  //! Ctor.
  XlfAbstractCmdDesc(const std::string& name, const std::string& alias, const std::string& comment);
  //! Dtor.
  virtual ~XlfAbstractCmdDesc();
  //! Registers the command to Excel.
  void Register() const;
  //! Unregister the command from Excel.
  void Unregister();

  //! Sets the name of the command in the XLL
  void SetName(const std::string& name);
  //! Gets the name of the command in the XLL.
  const std::string& GetName() const;
  //! Sets the alias to be shown in Excel
  void SetAlias(const std::string& alias);
  //! Gets the alias to be shown in Excel.
  const std::string& GetAlias() const;
  //! Sets the comment string to be shown in the function wizzard.
  void SetComment(const std::string& comment);
  //! Gets the comment string to be shown in the function wizzard.
  const std::string& GetComment() const;

protected:
  //! Actually registers the command (see template method in \ref DP)
  virtual int DoRegister(const std::string& dllName) const = 0;

private:
  //! Name of the command in the XLL.
  std::string name_;
  //! Alias for the command in Excel.
  std::string alias_;
  //! Comment associated to the command.
  std::string comment_;
};

#endif