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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (trix).
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
    pub fn trix_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut emaLookback: usize = 0_usize;
        emaLookback = self.ema_lookback(optInTimePeriod)?;
        return Ok((emaLookback * 3 + self.rocr_lookback(1)?) as usize);
    }
    fn trix_impl(
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
        let _assertLb = self.trix_lookback(optInTimePeriod).unwrap_or(usize::MAX);
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
        // TRIX = 1-day percent rate-of-change of a triple EMA.
        // Will change only on success.
        (*outNBElement) = 0;
        (*outBegIdx) = 0;
        // Adjust startIdx to account for the lookback period.
        lookbackEMA = self.ema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        lookbackTotal = lookbackEMA * 3 + self.rocr_lookback(1).unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            return RetCode::Success;
        }
        // Single lockstep pass: EMA1 feeds EMA2 feeds EMA3, output is the
        // roc() of consecutive EMA3 values. Output element j is the TRIX
        // of bar startIdx+j (fix #98). The arithmetic order below is the
        // bit-exactness contract — do not reorder or fuse operations; the
        // seed sums accumulate from 0.0 in production order (0.0+x is not
        // x for x=-0.0). In-place safe: outReal[outIdx] is written after
        // inReal[startIdx+outIdx] was read.
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
        while today <= startIdx - (lookbackEMA * 2 + 1) {
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
        while today <= startIdx - (lookbackEMA + 1) {
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
        // period of EMA3, up to the bar before the first output.
        while today <= startIdx - 1 {
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
        // write the 1-day rate-of-change of EMA3 into the output.
        outIdx = 0;
        while today <= endIdx {
            tempReal = prevEMA3;
            prevEMA1 = (inReal[{
                let _v = today;
                today += 1;
                _v
            }] - prevEMA1 as f64)
                .mul_add(optInK_1, prevEMA1);
            prevEMA2 = (prevEMA1 - prevEMA2 as f64).mul_add(optInK_1, prevEMA2);
            prevEMA3 = (prevEMA2 - prevEMA3 as f64).mul_add(optInK_1, prevEMA3);
            if tempReal != 0.0 {
                outReal[outIdx] = (prevEMA3 / tempReal - 1.0) * 100.0;
                outIdx += 1;
            } else {
                outReal[outIdx] = 0.0;
                outIdx += 1;
            }
        }
        // Succeed. Indicate where the output starts relative to
        // the caller input.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn trix(
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
        let _guardLb = self.trix_lookback(optInTimePeriod)?;
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
        let retCode = self.trix_impl(
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
