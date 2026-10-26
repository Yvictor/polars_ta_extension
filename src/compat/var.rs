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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (var).
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
    pub fn var_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInNbDev: f64,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 5;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 1e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return Err(RetCode::BadParam);
        }
        return Ok((optInTimePeriod - 1) as usize);
    }
    pub(crate) fn var_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        mut optInNbDev: f64,
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
        if optInNbDev == Self::REAL_DEFAULT {
            optInNbDev = 1e0;
        } else if !((optInNbDev >= Self::REAL_MIN) && (optInNbDev <= Self::REAL_MAX)) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .var_lookback(optInTimePeriod, optInNbDev)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut tempReal: f64 = 0.0_f64;
        let mut shift: f64 = 0.0_f64;
        let mut periodTotal1: f64 = 0.0_f64;
        let mut periodTotal2: f64 = 0.0_f64;
        let mut meanValue1: f64 = 0.0_f64;
        let mut variance: f64 = 0.0_f64;
        let mut invPeriod: f64 = 0.0_f64;
        let mut i: usize = 0_usize;
        let mut j: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut windowStart: usize = 0_usize;
        let mut nbInitialElementNeeded: usize = 0_usize;
        let mut barsSinceReseed: usize = 0_usize;
        // Identify the minimum number of price bar needed to calculate
        // at least one output.
        nbInitialElementNeeded = (optInTimePeriod - 1) as usize;
        // Move up the start index if there is not enough initial data.
        if startIdx < nbInitialElementNeeded {
            startIdx = nbInitialElementNeeded;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        invPeriod = 1.0 / (optInTimePeriod as f64);
        // Measure deviations against a shift near the window: the running sums
        // periodTotal1 = sum(inReal-shift) and periodTotal2 = sum((inReal-shift)^2)
        // stay at variance scale, so variance = periodTotal2/period - mean^2 no longer
        // subtracts two ~mean^2 quantities. Anchor the shift to the first window value
        // (also gives an exact 0 for period 1, with no division by period-1).
        trailingIdx = startIdx - nbInitialElementNeeded;
        shift = inReal[trailingIdx];
        periodTotal1 = 0.0;
        periodTotal2 = 0.0;
        // for( j = trailingIdx; j < startIdx; j += 1 )
        j = trailingIdx;
        while j < startIdx {
            tempReal = inReal[j] - shift;
            periodTotal1 += tempReal;
            tempReal *= tempReal;
            periodTotal2 += tempReal;
            j += 1;
        }
        // inReal and outReal may be the same buffer: each trailing value is consumed
        // before its slot is overwritten by the output.
        i = startIdx;
        outIdx = 0;
        barsSinceReseed = (32 * optInTimePeriod) as usize;
        loop {
            // Add the incoming value, measured against the shift.
            tempReal = inReal[i] - shift;
            periodTotal1 += tempReal;
            tempReal *= tempReal;
            periodTotal2 += tempReal;
            meanValue1 = periodTotal1 * invPeriod;
            variance = periodTotal2 * invPeriod - meanValue1 * meanValue1;
            // Remove the trailing value (prepares the next window).
            tempReal = inReal[trailingIdx] - shift;
            periodTotal1 -= tempReal;
            tempReal *= tempReal;
            periodTotal2 -= tempReal;
            trailingIdx += 1;
            // Re-anchor the shift and rebuild the running sums with a fresh two-pass
            // when the shift is stale enough that the subtraction loses digits - i.e.
            // the variance has shrunk below 1e-6 of the mean squared deviation it is
            // extracted from (that ratio bounds the cancellation error to ~eps/1e-6 ~
            // 2e-10, so partial cancellation, not just total collapse, is caught); OR
            // when the value just removed sat so far from the shift that its squared term
            // (tempReal) dwarfs the surviving sum (a large outlier passing through the
            // window buries the small terms below its ulp, and the residual left when it
            // leaves is cancellation garbage); OR at least every 32 windows so a slow
            // drift stays bounded regardless of the series length. The strict `<` also
            // leaves an exactly-constant window (variance 0, scale 0) alone instead of
            // reseeding it every bar. Guarantees a non-negative output.
            barsSinceReseed -= 1;
            if variance < 0.000001 * (periodTotal2 * invPeriod)
                || tempReal > 1000000.0 * periodTotal2
                || barsSinceReseed <= 0
            {
                barsSinceReseed = (32 * optInTimePeriod) as usize;
                windowStart = i - nbInitialElementNeeded;
                tempReal = 0.0;
                for j in (windowStart as usize)..(i as usize) + 1 {
                    tempReal += inReal[j];
                }
                j = (i as usize) + 1;
                shift = tempReal * invPeriod;
                periodTotal1 = 0.0;
                periodTotal2 = 0.0;
                for j in (windowStart as usize)..(i as usize) + 1 {
                    tempReal = inReal[j] - shift;
                    periodTotal1 += tempReal;
                    tempReal *= tempReal;
                    periodTotal2 += tempReal;
                }
                j = (i as usize) + 1;
                meanValue1 = periodTotal1 * invPeriod;
                variance = periodTotal2 * invPeriod - meanValue1 * meanValue1;
                // Floor the fresh figure at the same ratio the trigger above uses, now
                // measured against the RE-ANCHORED sums. With the shift AT the window
                // mean the deviations sum to ~0, so a real window has variance ~
                // periodTotal2*invPeriod and a ratio of ~1; the ratio drops toward 0
                // only when every deviation is the same value, i.e. when the spread is
                // at or under the rounding error of the mean itself. There is then no
                // spread the anchor could resolve, the surviving digits are noise, and
                // the honest answer is 0.
                //
                // The constant is 1e-12, NOT the 1e-6 the trigger above uses, and the
                // difference is load-bearing. periodTotal2*invPeriod is not the
                // variance here: it is variance + e^2, where e is the rounding error of
                // the reseed's own left-to-right sum for the mean -- exactly the term
                // the two-pass subtraction then cancels out. So the ratio measures how
                // badly that sum rounded, not how much signal survives, and matching
                // the trigger's 1e-6 fired ten orders before cancellation eats any
                // digits. It zeroed a variance the line above had just computed to nine
                // correct significant figures: 100011 bars at 31498938283.624615 with
                // two small outliers at period 99991 gives 1.0219900060103338e-09
                // (128-bit), and this returned 0 with TA_SUCCESS. At 1e-12 that window
                // survives and every intended bit-zero still zeroes -- the live ratios
                // on flat data are 0 or ~1e-16, six orders the other side.
                //
                // This is the ONE dead-zone in the var/stddev/bbands family, and it is
                // relative rather than the `variance < 0.0` it replaced because two
                // things ride on it:
                //
                //  - SIGN. periodTotal2 is a fresh sum of squares, so the right-hand
                //    side is >= 0 and any negative variance is clamped unconditionally -
                //    where `< 0.0` needed the three-case argument below to know that a
                //    negative one ever reaches this line.
                //  - SCALE. STDDEV and BBANDS square-root this, and each used to zero
                //    anything under a fixed TA_EPSILON first. That compares a SQUARED
                //    quantity to 1e-14, which is a cliff at a price level and not a
                //    noise floor: a $100.00 instrument quoted in 1e-8 ticks has a real
                //    variance around 1e-16 and came back exactly 0 on every bar (#243).
                //    Expressed here in the window's own units, the floor lets both of
                //    them square-root what they are handed unconditionally.
                //
                // Clamping HERE and not at the output write is what keeps this off the
                // per-bar path, and it is sufficient because a negative variance always
                // reseeds on the same bar - the guard above covers all three cases:
                // periodTotal2 > 0 makes its first disjunct `negative < positive`;
                // periodTotal2 < 0 makes the second disjunct's right side negative,
                // which the squared tempReal always exceeds; periodTotal2 == 0 reduces
                // the first to `variance < 0`. CHANGING THAT GUARD MEANS RE-CHECKING
                // THIS - the alternative is an unconditional clamp at the output write,
                // which needs no such argument but does cost ~3%.
                if variance < 0.000000000001 * (periodTotal2 * invPeriod) {
                    variance = 0.0;
                }
                // Re-remove the trailing value under the new shift so the carried state
                // matches the non-reseed path.
                tempReal = inReal[windowStart] - shift;
                periodTotal1 -= tempReal;
                tempReal *= tempReal;
                periodTotal2 -= tempReal;
            }
            outReal[outIdx] = variance;
            outIdx += 1;
            i += 1;
            if !(i <= endIdx) {
                break;
            }
        }
        // All done. Indicate the output limits and return.
        (*outNBElement) = outIdx;
        (*outBegIdx) = startIdx;
        return RetCode::Success;
    }
    pub fn var(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInNbDev: f64,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.var_lookback(optInTimePeriod, optInNbDev)?;
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
        let retCode = self.var_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            optInNbDev,
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
