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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (apo).
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
    pub fn apo_lookback(
        &self,
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInMAType: MAType,
    ) -> Result<usize, RetCode> {
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 12;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::EMA;
        }
        // The slow MA is the key factor determining the lookback period.
        return Ok(self.ma_lookback((optInSlowPeriod).max(optInFastPeriod), optInMAType)?);
    }
    pub(crate) fn apo_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInMAType: MAType,
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
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 12;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::EMA;
        }
        let _assertLb = self
            .apo_lookback(optInFastPeriod, optInSlowPeriod, optInMAType)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut tempBuffer: Vec<f64> = Vec::new();
        let mut retCode: RetCode = RetCode::Success;
        let mut tempInteger: usize = 0_usize;
        let mut fastBeg: usize = 0_usize;
        let mut fastNb: usize = 0_usize;
        let mut offset: usize = 0_usize;
        let mut i: usize = 0_usize;
        // Nothing to produce: the range is shorter than the lookback. Return before
        // touching anything.
        //
        // Without this the fast MA below runs first, and its lookback is SMALLER
        // than apo's own — so it reads the whole range and computes a result the
        // empty slow MA then discards. Observably identical (the slow MA's own early
        // return already yields 0,0 here), but it is the difference between "a range
        // shorter than the lookback reads nothing" being true of this function and
        // being false: with a caller-supplied inReal that stops short of endIdx, that
        // discarded work is an out-of-bounds read. Pinned by the zero-length no-I/O
        // probe over every guarded core.
        if self
            .ma_lookback((optInSlowPeriod).max(optInFastPeriod), optInMAType)
            .unwrap_or(usize::MAX)
            > endIdx
        {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // Allocate an intermediate buffer.
        tempBuffer = vec![0.0_f64; ((endIdx - startIdx + 1) * 1) as usize];
        // Make sure slow is really slower than
        // the fast period! if not, swap...
        if optInSlowPeriod < optInFastPeriod {
            // swap
            tempInteger = (optInSlowPeriod) as usize;
            optInSlowPeriod = optInFastPeriod;
            optInFastPeriod = (tempInteger) as i32;
        }
        // Calculate the fast MA into the tempBuffer.
        let _xr0 = match self.ma(
            startIdx,
            endIdx,
            inReal,
            optInFastPeriod,
            optInMAType,
            &mut tempBuffer[..],
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        fastBeg = _xr0.beg_idx;
        fastNb = _xr0.count;
        retCode = RetCode::Success;
        // Calculate the slow MA into the output.
        let _xr1 = match self.ma(
            startIdx,
            endIdx,
            inReal,
            optInSlowPeriod,
            optInMAType,
            outReal,
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        (*outBegIdx) = _xr1.beg_idx;
        (*outNBElement) = _xr1.count;
        retCode = RetCode::Success;
        // fastNb - *outNBElement == slowBeg - fastBeg (the fast MA has at least as
        // many outputs), so tempBuffer[i+offset] is the fast MA at the same bar as
        // outReal[i], with a non-negative index. An empty slow MA skips the loop.
        offset = fastNb - (*outNBElement);
        // Calculate (fast MA)-(slow MA) in the output.
        // for( i = 0; i < ((((*outNBElement) as usize)) as usize); i += 1 )
        i = 0;
        while i < (((*outNBElement) as usize) as usize) {
            outReal[i] = ((tempBuffer[i + offset] - outReal[i]) as f64);
            i += 1;
        }
        return RetCode::Success;
    }
    pub fn apo(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInFastPeriod: i32,
        optInSlowPeriod: i32,
        optInMAType: MAType,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.apo_lookback(optInFastPeriod, optInSlowPeriod, optInMAType)?;
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
        let retCode = self.apo_impl(
            startIdx,
            endIdx,
            inReal,
            optInFastPeriod,
            optInSlowPeriod,
            optInMAType,
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
