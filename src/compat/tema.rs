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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (tema).
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
    pub fn tema_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut retValue: usize = 0_usize;
        // Get lookack for one EMA.
        retValue = self.ema_lookback(optInTimePeriod)?;
        return Ok(retValue * 3);
    }
    fn tema_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
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
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self.tema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut prevEMA1: f64 = 0.0_f64;
        let mut prevEMA2: f64 = 0.0_f64;
        let mut prevEMA3: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut optInK_1: f64 = 0.0_f64;
        let mut i: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut lookbackEMA: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        // For an explanation of this function, please read:
        //
        // Stocks & Commodities V. 12:1 (11-19):
        //   Smoothing Data With Faster Moving Averages
        // Stocks & Commodities V. 12:2 (72-80):
        //   Smoothing Data With Less Lag
        //
        // Both magazine articles written by Patrick G. Mulloy
        //
        // Essentially, a TEMA of time serie 't' is:
        //   EMA1 = EMA(t,period)
        //   EMA2 = EMA(EMA(t,period),period)
        //   EMA3 = EMA(EMA(EMA(t,period),period))
        //   TEMA = 3*EMA1 - 3*EMA2 + EMA3
        //
        // TEMA offers a moving average with less lags then the
        // traditional EMA.
        //
        // Do not confuse a TEMA with EMA3. Both are called "Triple EMA"
        // in the litterature.
        //
        // DEMA is very similar (and from the same author).
        // Will change only on success.
        (*outNBElement) = 0;
        (*outBegIdx) = 0;
        // Adjust startIdx to account for the lookback period.
        lookbackEMA = self.ema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        lookbackTotal = lookbackEMA * 3;
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            return RetCode::Success;
        }
        // No smoothing at period of 1: the output is a copy of the input
        // (same convention as TA_MA for every MAType). Explicit because the
        // 3*e1 - 3*e2 + e3 composition cancels exactly only without FMA
        // contraction; ARM64 fused multiply-add leaves ~1e-14 residue.
        if optInTimePeriod == 1 {
            (*outBegIdx) = startIdx;
            outIdx = 0;
            while startIdx <= endIdx {
                outReal[outIdx] = ((inReal[{
                    let _v = startIdx;
                    startIdx += 1;
                    _v
                }]) as f64);
                outIdx += 1;
            }
            (*outNBElement) = outIdx;
            return RetCode::Success;
        }
        // The three EMA are computed in a single lockstep pass: each new
        // EMA1 value is immediately fed into EMA2, and each new EMA2 value
        // into EMA3. No temporary buffers are needed.
        //
        // The arithmetic order below is the bit-exactness contract
        // (do not reorder or fuse operations):
        //  - EMA recursion: ((x-prev)*k)+prev.
        //  - Each EMA is seeded with the sum of its first 'period'
        //    inputs, accumulated from 0.0 in input order (0.0+x is
        //    not x for x=-0.0), divided by the period.
        //  - The combine keeps the (3.0*EMA1)-(3.0*EMA2) grouping,
        //    added to EMA3 on the left.
        //
        // In-place (inReal == outReal) is supported: outReal[outIdx]
        // is written only after inReal[startIdx+outIdx] was read.
        optInK_1 = 2.0 / ((optInTimePeriod + 1) as f64);
        // Seed EMA1 with a simple average of the first
        // 'period' price bars.
        today = startIdx - lookbackTotal;
        i = (optInTimePeriod) as usize;
        tempReal = 0.0;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            tempReal += inReal[{
                let _v = today;
                today += 1;
                _v
            }];
        }
        prevEMA1 = tempReal / ((optInTimePeriod) as f64);
        // Advance EMA1 alone through its unstable period, up to
        // the bar where EMA2 seeding begins.
        while today <= startIdx - lookbackEMA * 2 {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
        }
        // Seed EMA2 with a simple average of the first 'period'
        // EMA1 values, accumulated as EMA1 produces them.
        tempReal = 0.0;
        tempReal += prevEMA1;
        i = (optInTimePeriod - 1) as usize;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            tempReal += prevEMA1;
        }
        prevEMA2 = tempReal / ((optInTimePeriod) as f64);
        // Advance EMA1 and EMA2 in lockstep through the unstable
        // period of EMA2, up to the bar where EMA3 seeding begins.
        while today <= startIdx - lookbackEMA {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            prevEMA2 = (prevEMA1 - prevEMA2 as f64).mul_add(optInK_1, prevEMA2);
        }
        // Seed EMA3 with a simple average of the first 'period'
        // EMA2 values, accumulated as EMA2 produces them.
        tempReal = 0.0;
        tempReal += prevEMA2;
        i = (optInTimePeriod - 1) as usize;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            prevEMA2 = (prevEMA1 - prevEMA2 as f64).mul_add(optInK_1, prevEMA2);
            tempReal += prevEMA2;
        }
        prevEMA3 = tempReal / ((optInTimePeriod) as f64);
        // Advance all three EMA in lockstep through the unstable
        // period of EMA3, up to the first output bar.
        while today <= startIdx {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            prevEMA2 = (prevEMA1 - prevEMA2 as f64).mul_add(optInK_1, prevEMA2);
            prevEMA3 = (prevEMA2 - prevEMA3 as f64).mul_add(optInK_1, prevEMA3);
        }
        // Stable zone: keep advancing the three EMA in lockstep and
        // write the TEMA into the output.
        outReal[0] = prevEMA3 + (3.0 * prevEMA1 - 3.0 * prevEMA2);
        outIdx = 1;
        while today <= endIdx {
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            prevEMA2 = (prevEMA1 - prevEMA2 as f64).mul_add(optInK_1, prevEMA2);
            prevEMA3 = (prevEMA2 - prevEMA3 as f64).mul_add(optInK_1, prevEMA3);
            outReal[outIdx] = prevEMA3 + (3.0 * prevEMA1 - 3.0 * prevEMA2);
            outIdx += 1;
        }
        // Succeed. Indicate where the output starts relative to
        // the caller input.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn tema(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.tema_lookback(optInTimePeriod)?;
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
        let retCode = self.tema_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
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
