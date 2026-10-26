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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (kc).
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
    pub fn kc_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInATRPeriod: i32,
        mut optInNbDev: f64,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 20;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInATRPeriod) as i32) == (i32::MIN) {
            optInATRPeriod = 10;
        } else if (((optInATRPeriod) as i32) < 1) || (((optInATRPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 2e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return Err(RetCode::BadParam);
        }
        let mut emaLookback: usize = 0_usize;
        let mut atrLookback: usize = 0_usize;
        // A band value needs BOTH the centre line and the ATR at the same bar, so the
        // first valid output is the later of the two lookbacks. Each term is exactly
        // the lookback of the function it comes from and is never restated here, which
        // is what makes KC inherit TA_FUNC_UNST_EMA and TA_FUNC_UNST_ATR from its two
        // callees. Reporting the honest max keeps outBegIdx == lookback (issue #99),
        // which streaming's Open depends on.
        emaLookback = self.ema_lookback(optInTimePeriod)?;
        atrLookback = self.atr_lookback(optInATRPeriod)?;
        return Ok((if emaLookback > atrLookback {
            emaLookback
        } else {
            atrLookback
        }) as usize);
    }
    pub(crate) fn kc_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        mut optInTimePeriod: i32,
        mut optInATRPeriod: i32,
        mut optInNbDev: f64,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outRealUpperBand: &mut [f64],
        outRealMiddleBand: &mut [f64],
        outRealLowerBand: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 20;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInATRPeriod) as i32) == (i32::MIN) {
            optInATRPeriod = 10;
        } else if (((optInATRPeriod) as i32) < 1) || (((optInATRPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 2e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .kc_lookback(optInTimePeriod, optInATRPeriod, optInNbDev)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inHigh.len());
        assert!(_assertStart > endIdx || endIdx < inLow.len());
        assert!(_assertStart > endIdx || endIdx < inClose.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outRealUpperBand.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outRealMiddleBand.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outRealLowerBand.len());
        if (!outRealUpperBand.is_empty()
            && !outRealMiddleBand.is_empty()
            && outRealUpperBand.as_ptr() == outRealMiddleBand.as_ptr())
            || (!outRealUpperBand.is_empty()
                && !outRealLowerBand.is_empty()
                && outRealUpperBand.as_ptr() == outRealLowerBand.as_ptr())
            || (!outRealMiddleBand.is_empty()
                && !outRealLowerBand.is_empty()
                && outRealMiddleBand.as_ptr() == outRealLowerBand.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut retCode: RetCode = RetCode::Success;
        let mut i: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut emaLookback: usize = 0_usize;
        let mut tpStartIdx: usize = 0_usize;
        let mut tempBegIdx: usize = 0_usize;
        let mut tempNbElement: usize = 0_usize;
        let mut tempReal: f64 = 0.0_f64;
        let mut middle: f64 = 0.0_f64;
        let mut tempTP: Vec<f64> = Vec::new();
        let mut tempATR: Vec<f64> = Vec::new();
        emaLookback = self.ema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        lookbackTotal = self
            .kc_lookback(optInTimePeriod, optInATRPeriod, optInNbDev)
            .unwrap_or(usize::MAX);
        // Nothing to produce: the range is shorter than the lookback. Return before
        // touching anything, so that a caller-supplied input which stops short of
        // endIdx is never read past its end.
        if lookbackTotal > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Each leg is entered at its OWN lookback, so each is the shipped function
        // over this range and nothing here over-warms the shorter one: a caller who
        // wants the band converged sets TA_FUNC_UNST_ATR, exactly as they would when
        // calling TA_ATR directly. The typical price is a derived input, so it is
        // materialized only over the window the moving average reads.
        tpStartIdx = startIdx - emaLookback;
        tempTP = vec![0.0_f64; ((endIdx - tpStartIdx + 1) * 1) as usize];
        tempATR = vec![0.0_f64; ((endIdx - startIdx + 1) * 1) as usize];
        let _xr0 = match self.typprice(tpStartIdx, endIdx, inHigh, inLow, inClose, &mut tempTP[..])
        {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        tempBegIdx = _xr0.beg_idx;
        tempNbElement = _xr0.count;
        retCode = RetCode::Success;
        // The ATR consumes the price inputs before the moving average below writes
        // the middle band, which may be aliased onto one of them.
        let _xr1 = match self.atr(
            startIdx,
            endIdx,
            inHigh,
            inLow,
            inClose,
            optInATRPeriod,
            &mut tempATR[..],
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        tempBegIdx = _xr1.beg_idx;
        tempNbElement = _xr1.count;
        retCode = RetCode::Success;
        // tempTP is bar-tpStartIdx relative, so entering the moving average at its
        // own lookback puts its first output on startIdx, where the ATR's already is.
        let _xr2 = match self.ema(
            emaLookback,
            endIdx - tpStartIdx,
            &tempTP,
            optInTimePeriod,
            outRealMiddleBand,
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        (*outBegIdx) = _xr2.beg_idx;
        (*outNBElement) = _xr2.count;
        retCode = RetCode::Success;
        if ((*outNBElement) as usize) == 0 {
            (*outNBElement) = 0;
            return retCode;
        }
        (*outBegIdx) = startIdx;
        // for( i = 0; i < ((((*outNBElement) as usize)) as usize); i += 1 )
        i = 0;
        while i < (((*outNBElement) as usize) as usize) {
            middle = outRealMiddleBand[i];
            tempReal = tempATR[i] * optInNbDev;
            outRealUpperBand[i] = middle + tempReal;
            outRealLowerBand[i] = middle - tempReal;
            i += 1;
        }
        return RetCode::Success;
    }
    pub fn kc(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        optInTimePeriod: i32,
        optInATRPeriod: i32,
        optInNbDev: f64,
        outRealUpperBand: &mut [f64],
        outRealMiddleBand: &mut [f64],
        outRealLowerBand: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.kc_lookback(optInTimePeriod, optInATRPeriod, optInNbDev)?;
        let _guardStart = if startIdx > _guardLb {
            startIdx
        } else {
            _guardLb
        };
        if inHigh.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        if inLow.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        if inClose.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        let _guardOutLen = if _guardStart > endIdx {
            0
        } else {
            endIdx - _guardStart + 1
        };
        if outRealUpperBand.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outRealMiddleBand.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outRealLowerBand.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.kc_impl(
            startIdx,
            endIdx,
            inHigh,
            inLow,
            inClose,
            optInTimePeriod,
            optInATRPeriod,
            optInNbDev,
            &mut outBegIdx,
            &mut outNBElement,
            outRealUpperBand,
            outRealMiddleBand,
            outRealLowerBand,
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
