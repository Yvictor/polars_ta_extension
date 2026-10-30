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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (zlema).
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
    pub fn zlema_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // ZLEMA owns no TA_FUNC_UNST_ id. It borrows EMA's through this call, which
        // is why zlema.yaml must not declare `unstable_period`.
        return Ok(
            ((((optInTimePeriod - 1) / 2) as usize) + self.ema_lookback(optInTimePeriod)?) as usize,
        );
    }
    fn zlema_impl(
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
        let _assertLb = self.zlema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut optInK_1: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut prevMA: f64 = 0.0_f64;
        let mut i: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut lag: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        optInK_1 = 2.0 / ((optInTimePeriod + 1) as f64);
        // KEEP THIS ARITHMETIC EXACTLY AS WRITTEN -- the de-lag in one rounding
        // (2.0*c - l, not c + (c - l)), the seed sum accumulating from 0.0, and
        // ((v - prevMA)*k) + prevMA. Together they make ZLEMA bit-for-bit equal to
        // an EMA over a materialised de-lagged series, which is the strongest gate
        // this function has. Reordering any one breaks that equality silently, and
        // the de-lag spelling is worth more than rounding noise: c + (c - l) rounds
        // twice, which is 5e-12 relative where 2c - l cancels.
        lag = ((optInTimePeriod - 1) / 2) as usize;
        lookbackTotal = self.zlema_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        // Move up the start index if there is not
        // enough initial data.
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // No smoothing at period of 1: the output is a copy of the input, the
        // convention TA_MA applies to every MAType. Explicit, because at period 1
        // lag is 0 and optInK_1 is exactly 1.0, so the recursion below reduces to
        // (x-prev)+prev -- which returns x only while consecutive values stay
        // within a factor of two of each other. The unstable period still delays
        // the first output.
        if optInTimePeriod == 1 {
            (*outBegIdx) = startIdx;
            outIdx = 0;
            today = startIdx;
            while today <= endIdx {
                outReal[outIdx] = ((inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }]) as f64);
                outIdx += 1;
            }
            (*outNBElement) = outIdx;
            return RetCode::Success;
        }
        (*outBegIdx) = startIdx;
        // In-place safe (outReal == inReal): both of a bar's reads precede its
        // write, and trailingIdx >= outIdx + optInTimePeriod - 1, so the trailing
        // read never reaches a slot already written.
        trailingIdx = startIdx - lookbackTotal;
        today = trailingIdx + lag;
        i = (optInTimePeriod) as usize;
        tempReal = 0.0;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            tempReal += 2.0 * inReal[today] - inReal[trailingIdx];
            today += 1;
            trailingIdx += 1;
        }
        prevMA = tempReal / ((optInTimePeriod) as f64);
        while today <= startIdx {
            prevMA = (2.0 * inReal[today] - inReal[trailingIdx] - prevMA as f64)
                .mul_add(optInK_1, prevMA);
            today += 1;
            trailingIdx += 1;
        }
        outReal[0] = prevMA;
        outIdx = 1;
        while today <= endIdx {
            prevMA = (2.0 * inReal[today] - inReal[trailingIdx] - prevMA as f64)
                .mul_add(optInK_1, prevMA);
            today += 1;
            trailingIdx += 1;
            outReal[outIdx] = prevMA;
            outIdx += 1;
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn zlema(
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
        let _guardLb = self.zlema_lookback(optInTimePeriod)?;
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
        let retCode = self.zlema_impl(
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
