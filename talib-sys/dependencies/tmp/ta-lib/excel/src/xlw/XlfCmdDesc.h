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

#ifndef INC_XlfCmdDesc_H
#define INC_XlfCmdDesc_H

/*!
\file XlfCmdDesc.h
\brief Declares class XlfCmdDesc.
*/

// $Id: XlfCmdDesc.h 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfAbstractCmdDesc.h>

#if defined(_MSC_VER)
#pragma once
#endif

#if defined(DEBUG_HEADERS)
#pragma DEBUG_HEADERS
#endif

//! Encapsulates Excel C macro command.
/*!
Commands can be called from the tool bar and do not take any argument
*/
class EXCEL32_API XlfCmdDesc: public XlfAbstractCmdDesc
{
public:
  //! Ctor.
  XlfCmdDesc(const std::string& name, const std::string& alias, const std::string& comment);
  //! Dtor.
  ~XlfCmdDesc();
  //! Adds the command to an Excel menu bar.
  int AddToMenuBar(const std::string& menu, const std::string& text);
  //! Is the command already in a menu bar?
  bool IsAddedToMenuBar();
  //! Activates/Desactivates the check box next to the command menu.
  int Check(bool) const;

protected:
  //! Registers the command to Excel
  int DoRegister() const;

private:
  //! Menu in which the command is to be displayed.
  std::string menu_;
  //! Text in the menu.
  std::string text_;
};

#endif