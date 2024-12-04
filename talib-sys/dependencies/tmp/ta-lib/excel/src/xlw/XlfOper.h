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

#ifndef INC_XlfOper_H
#define INC_XlfOper_H

/*!
\file XlfOper.h
\brief Declares class XlfOper.
*/

// $Id: XlfOper.h 1417 2007-03-18 03:43:33Z fortier $

#include <xlw/EXCEL32_API.h>
#include <xlw/xlcall32.h>
#include <xlw/XlfExcel.h>
#include <vector>

#if defined(_MSC_VER)
#pragma once
#endif

#if defined(DEBUG_HEADERS)
#pragma DEBUG_HEADERS
#endif

class XlfRef;

//! Wrapper around a pointer to the XLOPER Excel data structure.
/*!
This class eases the work of marchalling and unmarshalling data to
the Excel XLOPER format (including memory).
 
XlfOper holds a pointer to a XLOPER.
 
\warning It is important \e not to add any data member to this class
because the library heavily relies on the fact that LPXLOPER and
XlfOper have the same size. It allows the library to interpret any
LPXLOPER sent by Excel as a XlfOper.
*/
class EXCEL32_API XlfOper
{
public:
  //! Default ctor.
  XlfOper();
  //! Copy ctor.
  XlfOper(const XlfOper& oper);
  //! XLOPER * ctor.
  XlfOper(LPXLOPER lpxloper);
  //! double ctor.
  XlfOper(double value);
  //! short ctor.
  XlfOper(short value);
  //! boolean ctor.
  XlfOper(bool value);
  //! 0 terminated chararcter string ctor.
  XlfOper(const char *value);
  //! XlfRef ctor.
  XlfOper(const XlfRef& range);
#ifndef PORT_NO_MEMBER_TEMPLATE
  //! Container ctor.
  template <class FwdIt>
  XlfOper(WORD rows, BYTE cols, FwdIt start)
#ifdef PORT_PARTIAL_MEMBER_TEMPLATE
  {
    Allocate();
    Set(rows,cols,start);
  }
#else
  ;
#endif
#endif
  //! Constructs an Excel error.
  static XlfOper Error(WORD);
  //! Dtor
  ~XlfOper();
  //! Free auxiliary memory associated with the XLOPER
  void FreeAuxiliaryMemory() const;
  //! Assignment operator
  XlfOper& operator=(const XlfOper& xloper);

  //! Is the data missing ?
  bool IsMissing() const;
  //! Is the data an error ?
  bool IsError() const;
  //! Is the data boolean ?
  bool IsBool() const;

  int XLType() const;

  //! Converts to a double.
  double AsDouble(int * pxlret = 0) const;

  //! Lets the user choose how to convert a range in a vector<double>
  /*!
   * Default policy is UniDimensional. The 2 others are typically to facilitate conversion
   * to matrix classes.
   *
   * \sa ConvertToDoubleVector, AsDoubleVector.
   */
  enum DoubleVectorConvPolicy
  {
    /*! Generates an error if the range is not uni dimensional (one row or one column). */
    UniDimensional,
    /*! Flattens the range in a C-like way (rows are continuous). */
    RowMajor,
    /*! Flattens the range in a Fortran-like way (columns are continuous). */
    ColumnMajor
  };

  //! Converts to a std::vector<double>.
  std::vector<double> AsDoubleVector(DoubleVectorConvPolicy policy = UniDimensional, int * pxlret = 0) const;

  //! Converts to a short.
  short AsShort(int * pxlret = 0) const;

  //! Converts to a bool.
  bool AsBool(int * pxlret = 0) const;

  //! Converts to an int.
  int AsInt(int * pxlret = 0) const;

  //! Converts to a char *.
  char * AsString(int * pxlret = 0) const;

  //! Converts to a XlfReg.
  XlfRef AsRef(int * pxlret = 0) const;

  //! Gets the internal LPXLOPER.
  LPXLOPER GetLPXLOPER() const;

  //! Set the underlying XLOPER * to lpxloper
  XlfOper& Set(LPXLOPER lpxloper);
  //! Set to a a double
  XlfOper& Set(double value);
  //! Set to a a short
  XlfOper& Set(short value);
  //! Set to a a boolean
  XlfOper& Set(bool value);
  //! Set to a a zero-terminated character string
  XlfOper& Set(const char *value);
  //! Set to a range
  XlfOper& Set(const XlfRef& range);
  //! Set to an error value
  XlfOper& SetError(WORD error);
  //! Cast to XLOPER *
  operator LPXLOPER();
#ifndef PORT_NO_MEMBER_TEMPLATE
  //! Set to an array
  /*!
  \param r number of rows in the array
  \param c number of columns in the array
  \param it iterator pointing to the begining of a container
    of size r x c (at least) that contain the data.
  \warning Data are to be stored row-wise.
  */
  template<class FwdIt>
  XlfOper& Set(WORD r, BYTE c, FwdIt it)
#ifdef PORT_PARTIAL_MEMBER_TEMPLATE
  {
    lpxloper_->xltype = xltypeMulti;
    lpxloper_->val.array.rows = r;
    lpxloper_->val.array.columns = c;
    lpxloper_->val.array.lparray = (LPXLOPER)XlfExcel::Instance().GetMemory(r*c*sizeof(XLOPER));
    for (size_t i = 0; i < size_t(r*c); ++i, ++it)
      lpxloper_->val.array.lparray[i] = *(LPXLOPER)XlfOper(*it);
    return *this;
  }
#else
  ;
#endif
#endif

private:
  //! Internal LPXLOPER.
  LPXLOPER lpxloper_;

  //! Coerces method is called by conversion operators if needed (never by the user).
  int Coerce(short type, XlfOper& res) const;

  //! Reserves memory in XLL buffer (garbage collected).
  int Allocate();

  //! Anticipates deallocation if possible.
  void Deallocate();

  //! Throws an exception when critical errors occur.
  int ThrowOnError(int) const;
  
  //! Internally used to flag XLOPER returned by Excel.
  static int xlbitFreeAuxMem;

  //! Attempts conversion to double and returns Excel4 error code.
  int ConvertToDoubleVector(std::vector<double>&, DoubleVectorConvPolicy policy = UniDimensional) const;
  //! Attempts conversion to double and returns Excel4 error code.
  int ConvertToDouble(double&) const throw();
  //! Attempts conversion to short and returns Excel4 error code.
  int ConvertToShort(short&) const throw();
  //! Attempts conversion to bool and returns Excel4 error code.
  int ConvertToBool(bool&) const throw();
  //! Attempts conversion to int and returns Excel4 error code.
  int ConvertToInt(int&) const throw();
  //! Attempts conversion to string and returns Excel4 error code.
  int ConvertToString(char *&) const throw();
  //! Attempts conversion to XlRef and returns Excel4 error code.
  int ConvertToRef(XlfRef&) const throw();

  friend XlfExcel;
};

#ifdef PORT_NO_MEMBER_TEMPLATE
/*!
\brief Set an array to an XlfOper.
Because not all compilers support member template this function
is provided in order to replace the template method Set(WORD,BYTE,FwdIt).
*/
template <class FwdIt>
XlfOper& XlfOperSet(XlfOper& oper, WORD rows, BYTE cols, FwdIt it)
{
  LPXLOPER lpxloper=oper;
  lpxloper->xltype = xltypeMulti;
  lpxloper->val.array.rows = rows;
  lpxloper->val.array.columns = cols;
  lpxloper->val.array.lparray = (LPXLOPER)XlfExcel::Instance().GetMemory(rows*cols*sizeof(XLOPER));
  for (size_t i = 0; i < rows*cols; ++i, ++it)
    lpxloper->val.array.lparray[i] = *(LPXLOPER)XlfOper(*it);
  return oper;
}
#else
#ifndef PORT_PARTIAL_MEMBER_TEMPLATE
/*!
\param r number of rows in the array
\param c number of columns in the array
\param it iterator pointing to the begining of a container
of size r x c (at least) that contain the data.
\warning Data are to be stored row-wise.
*/
template<class FwdIt>
XlfOper& XlfOper::Set<FwdIt>(WORD r, BYTE c, FwdIt it);
{
  lpxloper_->xltype = xltypeMulti;
  lpxloper_->val.array.rows = r;
  lpxloper_->val.array.columns = c;
  lpxloper_->val.array.lparray = (LPXLOPER)XlfExcel::Instance().GetMemory(r*c*sizeof(XLOPER));
  for (size_t i = 0; i < r*c; ++i, ++it)
    lpxloper_->val.array.lparray[i] = *(LPXLOPER)XlfOper(*it);
  return *this;
}
#endif
#endif

#ifdef NDEBUG
#include <xlw/XlfOper.inl>
#endif

#endif
