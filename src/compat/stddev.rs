/* TA-LIB Copyright (c) 1999-2026, Mario Fortier
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 * - Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in
 *   the documentation and/or other materials provided with the
 *   distribution.
 *
 * - Neither name of author nor the names of its contributors
 *   may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (stddev).
use super::*;
#[allow(
    non_snake_case,
    unused_variables,
    dead_code,
    unused_mut,
    unused_assignments,
    unused_parens
)]
impl CompatCore {
    pub fn stddev_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInNbDev: f64,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 5;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 1e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return Err(RetCode::BadParam);
        }
        // Lookback is driven by the variance.
        return Ok(self.var_lookback(optInTimePeriod, optInNbDev)?);
    }
    pub(crate) fn stddev_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        mut optInNbDev: f64,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outReal: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 5;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 1e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .stddev_lookback(optInTimePeriod, optInNbDev)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut i: usize = 0_usize;
        let mut retCode: RetCode = RetCode::Success;
        // Nothing to produce: the range is shorter than the lookback. Return before
        // touching anything.
        //
        // Same shape as the guard in apo and bbands: the variance below runs on the
        // same range and its lookback IS stddev's, so it declines and yields 0,0
        // without reading. Observably identical, but it makes "a range shorter than
        // the lookback reads nothing" true of stddev itself rather than only of var.
        // Pinned by the zero-length no-I/O probe over every guarded core.
        if self
            .stddev_lookback(optInTimePeriod, optInNbDev)
            .unwrap_or(usize::MAX)
            > endIdx
        {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // Calculate the variance.
        let _xr0 = match self.var(startIdx, endIdx, inReal, optInTimePeriod, 1.0, outReal) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        (*outBegIdx) = _xr0.beg_idx;
        (*outNBElement) = _xr0.count;
        retCode = RetCode::Success;
        // Calculate the square root of each variance, this
        // is the standard deviation.
        //
        // Multiply also by the ratio specified.
        //
        // Unconditional. var owns the dead-zone and owns the sign: it returns a
        // non-negative variance, already floored to exactly 0 on any window whose
        // re-anchored spread sat under its own rounding noise (var.c). What used to
        // stand here instead - zero the output wherever the variance fell under
        // TA_EPSILON - compared a SQUARED quantity to a fixed 1e-14, which is a cliff
        // at a price level rather than a noise floor: a $100.00 instrument quoted in
        // 1e-8 ticks has a variance around 1e-16 and came back as exactly 0 on every
        // bar, with TA_SUCCESS and nothing to say it had been suppressed (#243).
        // Dropping it also leaves a pure map, which the branch had kept sqrt out of.
        if optInNbDev != 1.0 {
            // for( i = 0; i < ((((*outNBElement) as usize)) as usize); i += 1 )
            i = 0;
            while i < (((*outNBElement) as usize) as usize) {
                outReal[i] = (((outReal[i]).sqrt() * optInNbDev) as f64);
                i += 1;
            }
        } else {
            // for( i = 0; i < ((((*outNBElement) as usize)) as usize); i += 1 )
            i = 0;
            while i < (((*outNBElement) as usize) as usize) {
                outReal[i] = (((outReal[i]).sqrt()) as f64);
                i += 1;
            }
        }
        return RetCode::Success;
    }
    pub fn stddev(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInNbDev: f64,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.stddev_lookback(optInTimePeriod, optInNbDev)?;
        let _guardStart = if startIdx > _guardLb {
            startIdx
        } else {
            _guardLb
        };
        if inReal.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        let _guardOutLen = if _guardStart > endIdx {
            0
        } else {
            endIdx - _guardStart + 1
        };
        if outReal.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.stddev_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            optInNbDev,
            &mut outBegIdx,
            &mut outNBElement,
            outReal,
        );
        match retCode {
            RetCode::Success => Ok(OutRange {
                beg_idx: outBegIdx,
                count: outNBElement,
            }),
            e => Err(e),
        }
    }
}
