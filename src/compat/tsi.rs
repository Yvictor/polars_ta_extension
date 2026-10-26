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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (tsi).
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
    pub fn tsi_lookback(
        &self,
        mut optInFirstPeriod: i32,
        mut optInSecondPeriod: i32,
    ) -> Result<usize, RetCode> {
        if ((optInFirstPeriod) as i32) == (i32::MIN) {
            optInFirstPeriod = 25;
        } else if (((optInFirstPeriod) as i32) < 2) || (((optInFirstPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSecondPeriod) as i32) == (i32::MIN) {
            optInSecondPeriod = 13;
        } else if (((optInSecondPeriod) as i32) < 2) || (((optInSecondPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // One bar forms the first close-to-close change, then the two EMA warm-ups
        // the pipeline stacks on it. Each term is exactly the lookback of the
        // function it comes from, which is also what makes TSI inherit
        // TA_FUNC_UNST_EMA from its callee.
        return Ok((1
            + self.ema_lookback(optInFirstPeriod)?
            + self.ema_lookback(optInSecondPeriod)?) as usize);
    }
    fn tsi_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInFirstPeriod: i32,
        mut optInSecondPeriod: i32,
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
        if ((optInFirstPeriod) as i32) == (i32::MIN) {
            optInFirstPeriod = 25;
        } else if (((optInFirstPeriod) as i32) < 2) || (((optInFirstPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSecondPeriod) as i32) == (i32::MIN) {
            optInSecondPeriod = 13;
        } else if (((optInSecondPeriod) as i32) < 2) || (((optInSecondPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .tsi_lookback(optInFirstPeriod, optInSecondPeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut kFirst: f64 = 0.0_f64;
        let mut kSecond: f64 = 0.0_f64;
        let mut emaFirstNum: f64 = 0.0_f64;
        let mut emaFirstDen: f64 = 0.0_f64;
        let mut emaSecondNum: f64 = 0.0_f64;
        let mut emaSecondDen: f64 = 0.0_f64;
        let mut sumFirstNum: f64 = 0.0_f64;
        let mut sumFirstDen: f64 = 0.0_f64;
        let mut sumSecondNum: f64 = 0.0_f64;
        let mut sumSecondDen: f64 = 0.0_f64;
        let mut prevClose: f64 = 0.0_f64;
        let mut mom: f64 = 0.0_f64;
        let mut absMom: f64 = 0.0_f64;
        let mut tsiValue: f64 = 0.0_f64;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackFirst: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut nBar: usize = 0_usize;
        let mut nSecond: usize = 0_usize;
        lookbackTotal = self
            .tsi_lookback(optInFirstPeriod, optInSecondPeriod)
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
        // Blau's double smoothing in one pass: the signed momentum and its
        // magnitude are carried through the same two EMA stages, then divided.
        //
        // Each stage seeds the way ema.c does -- a simple average of that stage's
        // first 'period' inputs -- so the result is bit-identical to TA_MOM(1)
        // followed by two TA_EMA calls on each chain. The stage boundary below is
        // the callee LOOKBACK, not (period-1), so that a warm
        // TA_SetUnstablePeriod(TA_FUNC_UNST_EMA) folds in: the second stage then
        // seeds from the values the first would have published. The seed sums
        // accumulate from 0.0 in production order and the recurrence is
        // ((x-prev)*k)+prev rather than the algebraically equal k*x+(1-k)*prev; do
        // not reorder or fuse them (0.0+x is not x for x=-0.0). That order IS the
        // bit-exactness contract against the composed reference.
        //
        // prevClose is carried in a scalar rather than re-read from inReal[t-1]
        // because outReal may alias inReal: the slot holding close[t-1] may already
        // hold an output written a bar earlier.
        kFirst = 2.0 / ((optInFirstPeriod + 1) as f64);
        kSecond = 2.0 / ((optInSecondPeriod + 1) as f64);
        lookbackFirst = self.ema_lookback(optInFirstPeriod).unwrap_or(usize::MAX);
        emaFirstNum = 0.0;
        emaFirstDen = 0.0;
        emaSecondNum = 0.0;
        emaSecondDen = 0.0;
        sumFirstNum = 0.0;
        sumFirstDen = 0.0;
        sumSecondNum = 0.0;
        sumSecondDen = 0.0;
        // The first bar carrying a close-to-close change.
        today = startIdx - lookbackTotal + 1;
        prevClose = inReal[today - 1];
        nBar = 0;
        // Warm-up. Runs through startIdx inclusive: the last pass here completes
        // the second stage's seed, so it produces the first output.
        while today <= startIdx {
            mom = inReal[today] - prevClose;
            prevClose = inReal[today];
            absMom = (mom).abs();
            // Stage 1: the first EMA, over the raw momentum and its magnitude.
            if nBar < ((optInFirstPeriod) as usize) {
                sumFirstNum = sumFirstNum + mom;
                sumFirstDen = sumFirstDen + absMom;
                if nBar == ((optInFirstPeriod - 1) as usize) {
                    emaFirstNum = sumFirstNum / ((optInFirstPeriod) as f64);
                    emaFirstDen = sumFirstDen / ((optInFirstPeriod) as f64);
                }
            } else {
                emaFirstNum = (mom - emaFirstNum as f64).mul_add(kFirst, emaFirstNum);
                emaFirstDen = (absMom - emaFirstDen as f64).mul_add(kFirst, emaFirstDen);
            }
            // Stage 2: the second EMA, over what stage 1 publishes.
            //
            // The stage counter is compared BEFORE it is subtracted, never after.
            // Writing this as `nSecond = nBar - lookbackFirst; if( nSecond >= 0 )`
            // is correct in C, where the counters are signed, and broken everywhere
            // else: the Rust backend renders them as usize, so the subtraction
            // underflows for the first lookbackFirst bars -- a panic in a debug
            // build and a wrap in release. It would also be invisible to the
            // cross-language gate, which runs release servers at unstable period 0,
            // where the branch the wrap wrongly takes happens to be a no-op because
            // both accumulators are still 0.0. smi.c states the same rule.
            if nBar >= lookbackFirst {
                nSecond = nBar - lookbackFirst;
                if nSecond < ((optInSecondPeriod) as usize) {
                    sumSecondNum = sumSecondNum + emaFirstNum;
                    sumSecondDen = sumSecondDen + emaFirstDen;
                    if nSecond == ((optInSecondPeriod - 1) as usize) {
                        emaSecondNum = sumSecondNum / ((optInSecondPeriod) as f64);
                        emaSecondDen = sumSecondDen / ((optInSecondPeriod) as f64);
                    }
                } else {
                    emaSecondNum =
                        (emaFirstNum - emaSecondNum as f64).mul_add(kSecond, emaSecondNum);
                    emaSecondDen =
                        (emaFirstDen - emaSecondDen as f64).mul_add(kSecond, emaSecondDen);
                }
            }
            nBar = nBar + 1;
            today = today + 1;
        }
        // The denominator is an EMA of an EMA of |momentum|: every term is
        // non-negative and every weight positive, so it is zero only when every
        // change that reached it was exactly zero -- 0/0, since the numerator is
        // zero with it, reported as the neutral 0.0 by the CCI (#7) and IMI (#112)
        // convention. Tested exactly rather than against a fixed band: a price
        // change carries the quote unit, and TA_IS_ZERO zeroes the oscillator for
        // any instrument quoted below it (issue #253).
        if emaSecondDen > 0.0 {
            tsiValue = 100.0 * emaSecondNum / emaSecondDen;
        } else {
            tsiValue = 0.0;
        }
        outReal[0] = tsiValue;
        outIdx = 1;
        // Stable zone. Both stages are a pure recursion from here on.
        while today <= endIdx {
            mom = inReal[today] - prevClose;
            prevClose = inReal[today];
            absMom = (mom).abs();
            emaFirstNum = (mom - emaFirstNum as f64).mul_add(kFirst, emaFirstNum);
            emaFirstDen = (absMom - emaFirstDen as f64).mul_add(kFirst, emaFirstDen);
            emaSecondNum = (emaFirstNum - emaSecondNum as f64).mul_add(kSecond, emaSecondNum);
            emaSecondDen = (emaFirstDen - emaSecondDen as f64).mul_add(kSecond, emaSecondDen);
            if emaSecondDen > 0.0 {
                tsiValue = 100.0 * emaSecondNum / emaSecondDen;
            } else {
                tsiValue = 0.0;
            }
            outReal[outIdx] = tsiValue;
            outIdx = outIdx + 1;
            today = today + 1;
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn tsi(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInFirstPeriod: i32,
        optInSecondPeriod: i32,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.tsi_lookback(optInFirstPeriod, optInSecondPeriod)?;
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
        let retCode = self.tsi_impl(
            startIdx,
            endIdx,
            inReal,
            optInFirstPeriod,
            optInSecondPeriod,
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
