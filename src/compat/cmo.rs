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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (cmo).
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
    pub fn cmo_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 14;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut retValue: usize = 0_usize;
        retValue = (optInTimePeriod + 0) as usize;
        return Ok(retValue);
    }
    pub(crate) fn cmo_impl(
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
            optInTimePeriod = 14;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self.cmo_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut outIdx: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut prevGain: f64 = 0.0_f64;
        let mut prevLoss: f64 = 0.0_f64;
        let mut prevValue: f64 = 0.0_f64;
        let mut tempValue1: f64 = 0.0_f64;
        let mut tempValue2: f64 = 0.0_f64;
        (*outBegIdx) = 0;
        (*outNBElement) = 0;
        // Adjust startIdx to account for the lookback period.
        lookbackTotal = self.cmo_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            return RetCode::Success;
        }
        outIdx = 0;
        // Index into the output.
        // Trap special case where the period is '1'.
        // In that case, just copy the input into the
        // output for the requested range (as-is !)
        if optInTimePeriod == 1 {
            (*outBegIdx) = startIdx;
            i = endIdx - startIdx + 1;
            (*outNBElement) = i;
            // Element loop, not a block copy: the C single-precision variant reads a
            // float array, so a double-sized byte copy would reinterpret and
            // over-read it (#137). Forward order keeps the in-place case correct (#94).
            today = startIdx;
            // for( outIdx = 0; outIdx < i; outIdx += 1 )
            outIdx = 0;
            while outIdx < i {
                outReal[outIdx] = ((inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }]) as f64);
                outIdx += 1;
            }
            return RetCode::Success;
        }
        // Accumulate Wilder's "Average Gain" and "Average Loss"
        // among the initial period.
        today = startIdx - lookbackTotal;
        prevValue = inReal[today];
        prevGain = 0.0;
        prevLoss = 0.0;
        today += 1;
        // for( i = (optInTimePeriod) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod) as usize;
        while i > 0 {
            tempValue1 = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            tempValue2 = tempValue1 - prevValue;
            prevValue = tempValue1;
            if tempValue2 < 0_f64 {
                prevLoss -= tempValue2;
            } else {
                prevGain += tempValue2;
            }
            i -= 1;
        }
        // Subsequent prevLoss and prevGain are smoothed
        // using the previous values (Wilder's approach).
        //  1) Multiply the previous by 'period-1'.
        //  2) Add today value.
        //  3) Divide by 'period'.
        prevLoss /= ((optInTimePeriod) as f64);
        prevGain /= ((optInTimePeriod) as f64);
        // Often documentation present the RSI calculation as follow:
        //    RSI = 100 - (100 / 1 + (prevGain/prevLoss))
        //
        // The following is equivalent:
        //    RSI = 100 * (prevGain/(prevGain+prevLoss))
        //
        // The second equation is used here for speed optimization.
        //
        // prevGain+prevLoss is a sum of non-negative magnitudes, so it is zero only
        // when every change since the seed was exactly zero -- test it exactly, never
        // against a fixed band. A gain carries the quote unit, so a constant put
        // against it zeroes a healthy oscillator for an instrument quoted below it
        // (issue #253).
        if today > startIdx {
            tempValue1 = prevGain + prevLoss;
            if tempValue1 > 0.0 {
                outReal[outIdx] = 100.0 * ((prevGain - prevLoss) / tempValue1);
                outIdx += 1;
            } else {
                outReal[outIdx] = 0.0;
                outIdx += 1;
            }
        } else {
            // Skip the unstable period. Do the processing
            // but do not write it in the output.
            while today < startIdx {
                tempValue1 = inReal[today];
                tempValue2 = tempValue1 - prevValue;
                prevValue = tempValue1;
                prevLoss *= ((optInTimePeriod - 1) as f64);
                prevGain *= ((optInTimePeriod - 1) as f64);
                if tempValue2 < 0_f64 {
                    prevLoss -= tempValue2;
                } else {
                    prevGain += tempValue2;
                }
                prevLoss /= ((optInTimePeriod) as f64);
                prevGain /= ((optInTimePeriod) as f64);
                today += 1;
            }
        }
        // Unstable period skipped... now continue
        // processing if needed.
        while today <= endIdx {
            tempValue1 = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            tempValue2 = tempValue1 - prevValue;
            prevValue = tempValue1;
            prevLoss *= ((optInTimePeriod - 1) as f64);
            prevGain *= ((optInTimePeriod - 1) as f64);
            if tempValue2 < 0_f64 {
                prevLoss -= tempValue2;
            } else {
                prevGain += tempValue2;
            }
            prevLoss /= ((optInTimePeriod) as f64);
            prevGain /= ((optInTimePeriod) as f64);
            tempValue1 = prevGain + prevLoss;
            if tempValue1 > 0.0 {
                outReal[outIdx] = 100.0 * ((prevGain - prevLoss) / tempValue1);
                outIdx += 1;
            } else {
                outReal[outIdx] = 0.0;
                outIdx += 1;
            }
        }
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn cmo(
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
        let _guardLb = self.cmo_lookback(optInTimePeriod)?;
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
        let retCode = self.cmo_impl(
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
