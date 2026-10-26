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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (t3).
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
    pub fn t3_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInVFactor: f64,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 5;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInVFactor == Self::REAL_DEFAULT {
            optInVFactor = 7e-1;
        } else if !((optInVFactor >= 0e0) && (optInVFactor <= 1e0)) {
            return Err(RetCode::BadParam);
        }
        return Ok((6 * (optInTimePeriod - 1) + 0) as usize);
    }
    fn t3_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        mut optInVFactor: f64,
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
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInVFactor == Self::REAL_DEFAULT {
            optInVFactor = 7e-1;
        } else if !((optInVFactor >= 0e0) && (optInVFactor <= 1e0)) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .t3_lookback(optInTimePeriod, optInVFactor)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut outIdx: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut k: f64 = 0.0_f64;
        let mut one_minus_k: f64 = 0.0_f64;
        let mut e1: f64 = 0.0_f64;
        let mut e2: f64 = 0.0_f64;
        let mut e3: f64 = 0.0_f64;
        let mut e4: f64 = 0.0_f64;
        let mut e5: f64 = 0.0_f64;
        let mut e6: f64 = 0.0_f64;
        let mut c1: f64 = 0.0_f64;
        let mut c2: f64 = 0.0_f64;
        let mut c3: f64 = 0.0_f64;
        let mut c4: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        // For an explanation of this function, please read:
        //
        // Magazine articles written by Tim Tillson
        //
        // Essentially, a T3 of time serie 't' is:
        //   EMA1(x,Period) = EMA(x,Period)
        //   EMA2(x,Period) = EMA(EMA1(x,Period),Period)
        //   GD(x,Period,vFactor) = (EMA1(x,Period)*(1+vFactor)) - (EMA2(x,Period)*vFactor)
        //   T3 = GD (GD ( GD(t, Period, vFactor), Period, vFactor), Period, vFactor);
        //
        // T3 offers a moving average with less lags then the
        // traditional EMA.
        //
        // Do not confuse a T3 with EMA3. Both are called "Triple EMA"
        // in the litterature.
        lookbackTotal = (6 * (optInTimePeriod - 1) + 0) as usize;
        if startIdx <= lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outNBElement) = 0;
            (*outBegIdx) = 0;
            return RetCode::Success;
        }
        // No smoothing at period of 1: the output is a copy of the input
        // (same convention as TA_MA for every MAType). Explicit because the
        // coefficients below sum to 1 only in real arithmetic; going through
        // the math would leave ~1e-14 floating-point drift on every value.
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
        today = startIdx - lookbackTotal;
        k = 2.0 / (((optInTimePeriod) as f64) + 1.0);
        one_minus_k = 1.0 - k;
        // Initialize e1
        tempReal = inReal[{
            let _v = today;
            today += 1;
            _v
        }];
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            tempReal += inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            i -= 1;
        }
        e1 = tempReal / ((optInTimePeriod) as f64);
        // Initialize e2
        tempReal = e1;
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            tempReal += e1;
            i -= 1;
        }
        e2 = tempReal / ((optInTimePeriod) as f64);
        // Initialize e3
        tempReal = e2;
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            tempReal += e2;
            i -= 1;
        }
        e3 = tempReal / ((optInTimePeriod) as f64);
        // Initialize e4
        tempReal = e3;
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            e3 = (one_minus_k as f64).mul_add(e3, k * e2);
            tempReal += e3;
            i -= 1;
        }
        e4 = tempReal / ((optInTimePeriod) as f64);
        // Initialize e5
        tempReal = e4;
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            e3 = (one_minus_k as f64).mul_add(e3, k * e2);
            e4 = (one_minus_k as f64).mul_add(e4, k * e3);
            tempReal += e4;
            i -= 1;
        }
        e5 = tempReal / ((optInTimePeriod) as f64);
        // Initialize e6
        tempReal = e5;
        // for( i = (optInTimePeriod - 1) as usize; i > 0; i -= 1 )
        i = (optInTimePeriod - 1) as usize;
        while i > 0 {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            e3 = (one_minus_k as f64).mul_add(e3, k * e2);
            e4 = (one_minus_k as f64).mul_add(e4, k * e3);
            e5 = (one_minus_k as f64).mul_add(e5, k * e4);
            tempReal += e5;
            i -= 1;
        }
        e6 = tempReal / ((optInTimePeriod) as f64);
        // Skip the unstable period
        while today <= startIdx {
            // Do the calculation but do not write the output
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            e3 = (one_minus_k as f64).mul_add(e3, k * e2);
            e4 = (one_minus_k as f64).mul_add(e4, k * e3);
            e5 = (one_minus_k as f64).mul_add(e5, k * e4);
            e6 = (one_minus_k as f64).mul_add(e6, k * e5);
        }
        // Calculate the constants
        tempReal = optInVFactor * optInVFactor;
        c1 = 0_f64 - tempReal * optInVFactor;
        c2 = 3.0 * (tempReal - c1);
        c3 = (0_f64 - 6.0) * tempReal - 3.0 * (optInVFactor - c1);
        c4 = (3.0 as f64).mul_add(tempReal, (3.0 as f64).mul_add(optInVFactor, 1.0) - c1);
        // Write the first output
        outIdx = 0;
        outReal[outIdx] = (c4 as f64).mul_add(
            e3,
            (c3 as f64).mul_add(e4, (c1 as f64).mul_add(e6, c2 * e5)),
        );
        outIdx += 1;
        // Calculate and output the remaining of the range.
        while today <= endIdx {
            e1 = (one_minus_k as f64).mul_add(
                e1,
                k * inReal[{
                    let _v = today;
                    today += 1;
                    _v
                }],
            );
            e2 = (one_minus_k as f64).mul_add(e2, k * e1);
            e3 = (one_minus_k as f64).mul_add(e3, k * e2);
            e4 = (one_minus_k as f64).mul_add(e4, k * e3);
            e5 = (one_minus_k as f64).mul_add(e5, k * e4);
            e6 = (one_minus_k as f64).mul_add(e6, k * e5);
            outReal[outIdx] = (c4 as f64).mul_add(
                e3,
                (c3 as f64).mul_add(e4, (c1 as f64).mul_add(e6, c2 * e5)),
            );
            outIdx += 1;
        }
        // Indicates to the caller the number of output
        // successfully calculated.
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn t3(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInVFactor: f64,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.t3_lookback(optInTimePeriod, optInVFactor)?;
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
        let retCode = self.t3_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            optInVFactor,
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
