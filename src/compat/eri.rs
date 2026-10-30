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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (eri).
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
    pub fn eri_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // Exactly the EMA of close underneath: its lookback, unstable period
        // included, is this function's lookback.
        return Ok(self.ema_lookback(optInTimePeriod)?);
    }
    fn eri_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        mut optInTimePeriod: i32,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outBullPower: &mut [f64],
        outBearPower: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self.eri_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inHigh.len());
        assert!(_assertStart > endIdx || endIdx < inLow.len());
        assert!(_assertStart > endIdx || endIdx < inClose.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outBullPower.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outBearPower.len());
        if (!outBullPower.is_empty()
            && !outBearPower.is_empty()
            && outBullPower.as_ptr() == outBearPower.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut outIdx: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut prevMA: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut k: f64 = 0.0_f64;
        let mut tempHT: f64 = 0.0_f64;
        let mut tempLT: f64 = 0.0_f64;
        // Elder Ray Index (Alexander Elder, Trading for a Living, 1993): how far
        // the bar's extremes sit from one shared EMA of close.
        //
        //   Bull Power = High - EMA(Close, n)
        //   Bear Power = Low  - EMA(Close, n)
        //
        // One fused loop, not ema() + a combine map: a composed form cannot
        // stream (raw bar inputs are outside check_map_step's provenance), which
        // is the same reason ACCBANDS is fused. The EMA is ema.c op for op --
        // sequential seed sum from 0.0 then one divide, the unstable-period
        // warm-up consumed bar by bar -- so the differential against shipped
        // TA_EMA holds bitwise.
        //
        // No division in the per-bar map: no 0/0, no NaN path (#112 by
        // construction). Bull >= Bear on every bar since high >= low.
        lookbackTotal = self.eri_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // Period 1: ema.c's explicit copy arm, kept here for the same reason it
        // exists there. At n == 1 the recursion below is fl(fl(x-prev)+prev),
        // which returns x only while consecutive closes stay within a factor of
        // two (Sterbenz), so without this arm `High - TA_EMA(Close, 1)` is not
        // what this function returns. The unstable period still delays the first
        // output, through the shared lookback above.
        if optInTimePeriod == 1 {
            outIdx = 0;
            today = startIdx;
            while today <= endIdx {
                tempHT = inHigh[today];
                tempLT = inLow[today];
                tempReal = inClose[today];
                outBullPower[outIdx] = tempHT - tempReal;
                outBearPower[outIdx] = tempLT - tempReal;
                outIdx += 1;
                today += 1;
            }
            (*outBegIdx) = startIdx;
            (*outNBElement) = outIdx;
            return RetCode::Success;
        }
        k = 2.0 / ((optInTimePeriod as f64) + 1.0);
        // Seed: ema.c's DEFAULT arm, op for op.
        today = startIdx - lookbackTotal;
        i = (optInTimePeriod) as usize;
        tempReal = 0.0;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            tempReal += inClose[{
                let _v = today;
                today += 1;
                _v
            }];
        }
        prevMA = tempReal / ((optInTimePeriod) as f64);
        // The warm-up also consumes the EMA unstable period.
        while today <= startIdx {
            prevMA = (inClose[{
                let _v = today;
                today += 1;
                _v
            }] - prevMA as f64)
                .mul_add(k, prevMA);
        }
        // prevMA is the EMA at bar startIdx; today == startIdx + 1. Load the
        // extremes into temps BEFORE writing either output: with two outputs
        // over three inputs the caller may alias any pair, and the second write
        // must not read a clobbered bar.
        tempHT = inHigh[startIdx];
        tempLT = inLow[startIdx];
        outBullPower[0] = tempHT - prevMA;
        outBearPower[0] = tempLT - prevMA;
        outIdx = 1;
        while today <= endIdx {
            prevMA = (inClose[today] - prevMA as f64).mul_add(k, prevMA);
            tempHT = inHigh[today];
            tempLT = inLow[today];
            outBullPower[outIdx] = tempHT - prevMA;
            outBearPower[outIdx] = tempLT - prevMA;
            outIdx += 1;
            today += 1;
        }
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn eri(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        optInTimePeriod: i32,
        outBullPower: &mut [f64],
        outBearPower: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.eri_lookback(optInTimePeriod)?;
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
        if outBullPower.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outBearPower.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.eri_impl(
            startIdx,
            endIdx,
            inHigh,
            inLow,
            inClose,
            optInTimePeriod,
            &mut outBegIdx,
            &mut outNBElement,
            outBullPower,
            outBearPower,
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
