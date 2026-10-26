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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (smi).
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
    pub fn smi_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInSignalPeriod: i32,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 2;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 25;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 2) || (((optInSignalPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // One high/low window, then the three EMA warm-ups the pipeline stacks on
        // top of it: slow smooths the raw momentum, fast smooths that, and signal
        // smooths the finished SMI line. Every term is exactly the lookback of the
        // function it comes from, so none of them is restated here -- which is also
        // what makes SMI inherit TA_FUNC_UNST_EMA from its callee.
        return Ok((((optInTimePeriod - 1) as usize)
            + self.ema_lookback(optInSlowPeriod)?
            + self.ema_lookback(optInFastPeriod)?
            + self.ema_lookback(optInSignalPeriod)?) as usize);
    }
    fn smi_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        mut optInTimePeriod: i32,
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInSignalPeriod: i32,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outSMI: &mut [f64],
        outSMISignal: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 2;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 25;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 2) || (((optInSignalPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .smi_lookback(
                optInTimePeriod,
                optInFastPeriod,
                optInSlowPeriod,
                optInSignalPeriod,
            )
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inHigh.len());
        assert!(_assertStart > endIdx || endIdx < inLow.len());
        assert!(_assertStart > endIdx || endIdx < inClose.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outSMI.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outSMISignal.len());
        if (!outSMI.is_empty()
            && !outSMISignal.is_empty()
            && outSMI.as_ptr() == outSMISignal.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut kSlow: f64 = 0.0_f64;
        let mut kFast: f64 = 0.0_f64;
        let mut kSignal: f64 = 0.0_f64;
        let mut highest: f64 = 0.0_f64;
        let mut lowest: f64 = 0.0_f64;
        let mut tmp: f64 = 0.0_f64;
        let mut emaSlowNum: f64 = 0.0_f64;
        let mut emaSlowDen: f64 = 0.0_f64;
        let mut emaFastNum: f64 = 0.0_f64;
        let mut emaFastDen: f64 = 0.0_f64;
        let mut sumSlowNum: f64 = 0.0_f64;
        let mut sumSlowDen: f64 = 0.0_f64;
        let mut sumFastNum: f64 = 0.0_f64;
        let mut sumFastDen: f64 = 0.0_f64;
        let mut sumSignal: f64 = 0.0_f64;
        let mut num: f64 = 0.0_f64;
        let mut den: f64 = 0.0_f64;
        let mut halfDen: f64 = 0.0_f64;
        let mut smiValue: f64 = 0.0_f64;
        let mut prevSignal: f64 = 0.0_f64;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackSlow: usize = 0_usize;
        let mut lookbackFast: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut highestIdx: i32 = 0_i32;
        let mut lowestIdx: i32 = 0_i32;
        let mut i: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut nBar: usize = 0_usize;
        let mut nFast: usize = 0_usize;
        let mut nSignal: usize = 0_usize;
        lookbackTotal = self
            .smi_lookback(
                optInTimePeriod,
                optInFastPeriod,
                optInSlowPeriod,
                optInSignalPeriod,
            )
            .unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        (*outBegIdx) = startIdx;
        // Blau's pipeline in one pass. A composed form is not available: the
        // streaming producer model carries exactly one intermediate series
        // (streaming.rs:2076) and SMI has two, the numerator and the denominator,
        // which must be smoothed separately before they are divided.
        //
        // Each of the three stages seeds the way ema.c does -- a simple average of
        // that stage's first 'period' inputs -- so the result is bit-identical to
        // TA_MAX + TA_MIN followed by four TA_EMA calls. The stage boundaries below
        // are the callee LOOKBACKS, not (period-1), so that a warm
        // TA_SetUnstablePeriod(TA_FUNC_UNST_EMA) folds in: each stage then seeds
        // from the values its predecessor would have published, exactly as the
        // composed form does. The seed sums accumulate from 0.0 in production
        // order; do not reorder or fuse them (0.0+x is not x for x=-0.0).
        kSlow = 2.0 / ((optInSlowPeriod + 1) as f64);
        kFast = 2.0 / ((optInFastPeriod + 1) as f64);
        kSignal = 2.0 / ((optInSignalPeriod + 1) as f64);
        lookbackSlow = self.ema_lookback(optInSlowPeriod).unwrap_or(usize::MAX);
        lookbackFast = self.ema_lookback(optInFastPeriod).unwrap_or(usize::MAX);
        emaSlowNum = 0.0;
        emaSlowDen = 0.0;
        emaFastNum = 0.0;
        emaFastDen = 0.0;
        prevSignal = 0.0;
        smiValue = 0.0;
        sumSlowNum = 0.0;
        sumSlowDen = 0.0;
        sumFastNum = 0.0;
        sumFastDen = 0.0;
        sumSignal = 0.0;
        highest = 0.0;
        lowest = 0.0;
        highestIdx = 0 - 1;
        lowestIdx = 0 - 1;
        // The first bar carrying a full high/low window.
        trailingIdx = startIdx - lookbackTotal;
        today = trailingIdx + ((optInTimePeriod - 1) as usize);
        nBar = 0;
        // Warm-up. Runs through startIdx inclusive: the last pass here is the one
        // that completes the signal seed, so it produces the first output pair.
        while today <= startIdx {
            // Set the lowest low
            tmp = inLow[today];
            if lowestIdx < ((trailingIdx) as i32) {
                lowestIdx = (trailingIdx) as i32;
                lowest = inLow[(lowestIdx) as usize];
                i = (lowestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmp = inLow[i];
                    if tmp < lowest {
                        lowestIdx = (i) as i32;
                        lowest = tmp;
                    }
                }
            } else if tmp <= lowest {
                lowestIdx = (today) as i32;
                lowest = tmp;
            }
            // Set the highest high
            tmp = inHigh[today];
            if highestIdx < ((trailingIdx) as i32) {
                highestIdx = (trailingIdx) as i32;
                highest = inHigh[(highestIdx) as usize];
                i = (highestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmp = inHigh[i];
                    if tmp > highest {
                        highestIdx = (i) as i32;
                        highest = tmp;
                    }
                }
            } else if tmp >= highest {
                highestIdx = (today) as i32;
                highest = tmp;
            }
            den = highest - lowest;
            num = inClose[today] - (highest + lowest) * 0.5;
            // Stage 1: the slow EMA, over the raw momentum.
            if nBar < ((optInSlowPeriod) as usize) {
                sumSlowNum = sumSlowNum + num;
                sumSlowDen = sumSlowDen + den;
                if nBar == ((optInSlowPeriod - 1) as usize) {
                    emaSlowNum = sumSlowNum / ((optInSlowPeriod) as f64);
                    emaSlowDen = sumSlowDen / ((optInSlowPeriod) as f64);
                }
            } else {
                emaSlowNum = (num - emaSlowNum as f64).mul_add(kSlow, emaSlowNum);
                emaSlowDen = (den - emaSlowDen as f64).mul_add(kSlow, emaSlowDen);
            }
            // Stage 2: the fast EMA, over what stage 1 publishes.
            //
            // The stage counters are compared BEFORE they are subtracted, never
            // after. Writing this as `nFast = nBar - lookbackSlow; if( nFast >= 0 )`
            // is correct in C, where the counters are signed, and broken everywhere
            // else: the Rust backend renders them as `usize`, so the subtraction
            // underflows for the first lookbackSlow bars -- a panic in a debug build
            // and a wrap in release. It would also be invisible to the cross-language
            // gate, which runs release servers at unstable period 0, where the branch
            // the wrap wrongly takes happens to be a no-op because both accumulators
            // are still 0.0.
            if nBar >= lookbackSlow {
                nFast = nBar - lookbackSlow;
                if nFast < ((optInFastPeriod) as usize) {
                    sumFastNum = sumFastNum + emaSlowNum;
                    sumFastDen = sumFastDen + emaSlowDen;
                    if nFast == ((optInFastPeriod - 1) as usize) {
                        emaFastNum = sumFastNum / ((optInFastPeriod) as f64);
                        emaFastDen = sumFastDen / ((optInFastPeriod) as f64);
                    }
                } else {
                    emaFastNum = (emaSlowNum - emaFastNum as f64).mul_add(kFast, emaFastNum);
                    emaFastDen = (emaSlowDen - emaFastDen as f64).mul_add(kFast, emaFastDen);
                }
            }
            // Stage 3: the SMI line, then the signal EMA over it.
            if nBar >= lookbackSlow + lookbackFast {
                nSignal = nBar - lookbackSlow - lookbackFast;
                halfDen = 0.5 * emaFastDen;
                if halfDen > 0.0 {
                    smiValue = 100.0 * emaFastNum / halfDen;
                } else {
                    smiValue = 0.0;
                }
                if nSignal < ((optInSignalPeriod) as usize) {
                    sumSignal = sumSignal + smiValue;
                    if nSignal == ((optInSignalPeriod - 1) as usize) {
                        prevSignal = sumSignal / ((optInSignalPeriod) as f64);
                    }
                } else {
                    prevSignal = (smiValue - prevSignal as f64).mul_add(kSignal, prevSignal);
                }
            }
            nBar = nBar + 1;
            trailingIdx = trailingIdx + 1;
            today = today + 1;
        }
        outSMI[0] = smiValue;
        outSMISignal[0] = prevSignal;
        outIdx = 1;
        // Stable zone. Every stage is a pure recursion from here on.
        while today <= endIdx {
            // Set the lowest low
            tmp = inLow[today];
            if lowestIdx < ((trailingIdx) as i32) {
                lowestIdx = (trailingIdx) as i32;
                lowest = inLow[(lowestIdx) as usize];
                i = (lowestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmp = inLow[i];
                    if tmp < lowest {
                        lowestIdx = (i) as i32;
                        lowest = tmp;
                    }
                }
            } else if tmp <= lowest {
                lowestIdx = (today) as i32;
                lowest = tmp;
            }
            // Set the highest high
            tmp = inHigh[today];
            if highestIdx < ((trailingIdx) as i32) {
                highestIdx = (trailingIdx) as i32;
                highest = inHigh[(highestIdx) as usize];
                i = (highestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmp = inHigh[i];
                    if tmp > highest {
                        highestIdx = (i) as i32;
                        highest = tmp;
                    }
                }
            } else if tmp >= highest {
                highestIdx = (today) as i32;
                highest = tmp;
            }
            den = highest - lowest;
            num = inClose[today] - (highest + lowest) * 0.5;
            emaSlowNum = (num - emaSlowNum as f64).mul_add(kSlow, emaSlowNum);
            emaSlowDen = (den - emaSlowDen as f64).mul_add(kSlow, emaSlowDen);
            emaFastNum = (emaSlowNum - emaFastNum as f64).mul_add(kFast, emaFastNum);
            emaFastDen = (emaSlowDen - emaFastDen as f64).mul_add(kFast, emaFastDen);
            // The denominator is an EMA of an EMA of the high-low range: every term
            // is non-negative and every weight is positive, so it carries no
            // cancellation residue and is zero only when every range that reached it
            // was exactly zero -- 0/0, since a window of H == L bars makes num zero
            // too, reported as the neutral 0.0 by the CCI (#7) and IMI (#112)
            // convention. Test it exactly: the range carries the quote unit, so the
            // fixed TA_IS_ZERO band this used to be zeroed the oscillator for any
            // instrument quoted below it (issue #253). Issue #107's machine-flat
            // window is caught by the exact test as well, since the residue an
            // EMA leaves there is zero, not sub-epsilon.
            halfDen = 0.5 * emaFastDen;
            if halfDen > 0.0 {
                smiValue = 100.0 * emaFastNum / halfDen;
            } else {
                smiValue = 0.0;
            }
            prevSignal = (smiValue - prevSignal as f64).mul_add(kSignal, prevSignal);
            outSMI[outIdx] = smiValue;
            outSMISignal[outIdx] = prevSignal;
            outIdx = outIdx + 1;
            trailingIdx = trailingIdx + 1;
            today = today + 1;
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn smi(
        &self,
        startIdx: usize,
        endIdx: usize,
        inHigh: &[f64],
        inLow: &[f64],
        inClose: &[f64],
        optInTimePeriod: i32,
        optInFastPeriod: i32,
        optInSlowPeriod: i32,
        optInSignalPeriod: i32,
        outSMI: &mut [f64],
        outSMISignal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.smi_lookback(
            optInTimePeriod,
            optInFastPeriod,
            optInSlowPeriod,
            optInSignalPeriod,
        )?;
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
        if outSMI.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outSMISignal.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.smi_impl(
            startIdx,
            endIdx,
            inHigh,
            inLow,
            inClose,
            optInTimePeriod,
            optInFastPeriod,
            optInSlowPeriod,
            optInSignalPeriod,
            &mut outBegIdx,
            &mut outNBElement,
            outSMI,
            outSMISignal,
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
