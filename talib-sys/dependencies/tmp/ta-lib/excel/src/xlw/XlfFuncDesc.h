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

#ifndef INC_XlfFuncDesc_H
#define INC_XlfFuncDesc_H

/*!
\file XlfFuncDesc.h
\brief Declares class XlfFuncDesc.
*/

// $Id: XlfFuncDesc.h 152 2003-04-20 04:42:47Z fortier $

#include <xlw/XlfAbstractCmdDesc.h>

#if defined(_MSC_VER)
#pragma once
#endif

class XlfArgDescList;

//! Encapsulates a function to be registered to Excel.
/*!
By registering your function, you make it available under Excel in
any spreadsheet as well as in the function wizard.
*/
class EXCEL32_API XlfFuncDesc: public XlfAbstractCmdDesc
{
public:
  //! Policy to reclalculate cells.
  enum RecalcPolicy {
	//! Function gets recalculated if one of the argument has changed.
	NotVolatile, 
	//! Function gets recalculated unconditionally each time the sheet is calculated.
	Volatile 
  } ;

  //! Ctor
  XlfFuncDesc(const std::string& name, const std::string& alias,
              const std::string& comment, const std::string& category,
			  RecalcPolicy recalcPolicy = NotVolatile);
  //! Dtor.
  ~XlfFuncDesc();

  //! Sets the category where your function will appear in the function wizzard.
  void SetCategory(const std::string& category);
  //! Gets the category where your function will appear in the function wizzard.
  const std::string& GetCategory() const;
  //! Sets the arguments definition.
  void SetArguments(const XlfArgDescList& arguments);
  //! Gets the arguments definition.
  const XlfArgDescList& GetArguments() const;

protected:
  //! Registers the function (template method).
  int DoRegister(const std::string& dllName) const;

private:
  //! Default ctor is declared private but not defined.
  XlfFuncDesc(const XlfFuncDesc&);
  //! Copy otor is declared private but not defined.
  XlfFuncDesc& operator=(const XlfFuncDesc&);
  //! Pointer to implementation (pimpl idiom, see \ref HS).
  struct XlfFuncDescImpl * impl_;
};

#endif