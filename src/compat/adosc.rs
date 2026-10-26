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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (adosc).
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
    pub fn adosc_lookback(
        &self,
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
    ) -> Result<usize, RetCode> {
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 3;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 10;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut slowestPeriod: usize = 0_usize;
        // Use the slowest EMA period to evaluate the total lookback.
        if optInFastPeriod < optInSlowPeriod {
            slowestPeriod = (optInSlowPeriod) as usize;
        } else {
            slowestPeriod = (optInFastPeriod) as usize;
        }
        // Adjust startIdx to account for the lookback period.
        return Ok(self.ema_lookback((slowestPeriod) as i32)?);
    }
    fn adosc_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        inVolume: &[f64],
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
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
            optInFastPeriod = 3;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 10;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .adosc_lookback(optInFastPeriod, optInSlowPeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inHigh.len());
        assert!(_assertStart > endIdx || endIdx < inLow.len());
        assert!(_assertStart > endIdx || endIdx < inClose.len());
        assert!(_assertStart > endIdx || endIdx < inVolume.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut slowestPeriod: usize = 0_usize;
        let mut high: f64 = 0.0_f64;
        let mut low: f64 = 0.0_f64;
        let mut close: f64 = 0.0_f64;
        let mut tmp: f64 = 0.0_f64;
        let mut slowEMA: f64 = 0.0_f64;
        let mut slowk: f64 = 0.0_f64;
        let mut one_minus_slowk: f64 = 0.0_f64;
        let mut fastEMA: f64 = 0.0_f64;
        let mut fastk: f64 = 0.0_f64;
        let mut one_minus_fastk: f64 = 0.0_f64;
        let mut ad: f64 = 0.0_f64;
        // Implementation Note:
        //     The fastEMA varaible is not neceseraly the
        //     fastest EMA.
        //     In the same way, slowEMA is not neceseraly the
        //     slowest EMA.
        //
        //     The ADOSC is always the (fastEMA - slowEMA) regardless
        //     of the period specified. In other word:
        //
        //     ADOSC(3,10) = EMA(3,AD) - EMA(10,AD)
        //
        //        while
        //
        //     ADOSC(10,3) = EMA(10,AD)- EMA(3,AD)
        //
        //     In the first case the EMA(3) is truly a faster EMA,
        //     while in the second case, the EMA(10) is still call
        //     fastEMA in the algorithm, even if it is in fact slower.
        //
        //     This gives more flexibility to the user if they want to
        //     experiment with unusual parameter settings.
        // Identify the slowest period.
        // This infomration is used soleley to bootstrap
        // the algorithm (skip the lookback period).
        if optInFastPeriod < optInSlowPeriod {
            slowestPeriod = (optInSlowPeriod) as usize;
        } else {
            slowestPeriod = (optInFastPeriod) as usize;
        }
        // Adjust startIdx to account for the lookback period.
        lookbackTotal = self
            .ema_lookback((slowestPeriod) as i32)
            .unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        (*outBegIdx) = startIdx;
        today = startIdx - lookbackTotal;
        // The following variables are used to
        // calculate the "ad".
        ad = 0.0;
        // Constants for EMA
        fastk = 2.0 / ((optInFastPeriod as f64) + 1.0);
        one_minus_fastk = 1.0 - fastk;
        slowk = 2.0 / ((optInSlowPeriod as f64) + 1.0);
        one_minus_slowk = 1.0 - slowk;
        // Initialize the two EMA
        //
        // Use the same range of initialization inputs for
        // both EMA and simply seed with the first A/D value.
        //
        // Note: Metastock do the same.
        high = inHigh[today];
        low = inLow[today];
        tmp = high - low;
        close = inClose[today];
        if tmp > 0.0 {
            ad += (close - low - (high - close)) / tmp * (inVolume[today] as f64);
        }
        today += 1;
        fastEMA = ad;
        slowEMA = ad;
        // Initialize the EMA and skip the unstable period.
        while today < startIdx {
            high = inHigh[today];
            low = inLow[today];
            tmp = high - low;
            close = inClose[today];
            if tmp > 0.0 {
                ad += (close - low - (high - close)) / tmp * (inVolume[today] as f64);
            }
            today += 1;
            fastEMA = (one_minus_fastk as f64).mul_add(fastEMA, fastk * ad);
            slowEMA = (one_minus_slowk as f64).mul_add(slowEMA, slowk * ad);
        }
        // Perform the calculation for the requested range
        outIdx = 0;
        while today <= endIdx {
            high = inHigh[today];
            low = inLow[today];
            tmp = high - low;
            close = inClose[today];
            if tmp > 0.0 {
                ad += (close - low - (high - close)) / tmp * (inVolume[today] as f64);
            }
            today += 1;
            fastEMA = (one_minus_fastk as f64).mul_add(fastEMA, fastk * ad);
            slowEMA = (one_minus_slowk as f64).mul_add(slowEMA, slowk * ad);
            outReal[outIdx] = fastEMA - slowEMA;
            outIdx += 1;
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn adosc(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        inVolume: &[f64],
        optInFastPeriod: i32,
        optInSlowPeriod: i32,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.adosc_lookback(optInFastPeriod, optInSlowPeriod)?;
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
        if inVolume.len() < endIdx + 1 {
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
        let retCode = self.adosc_impl(
            startIdx,
            endIdx,
            inHigh,
            inLow,
            inClose,
            inVolume,
            optInFastPeriod,
            optInSlowPeriod,
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
