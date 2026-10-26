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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (correl).
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
    pub fn correl_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        return Ok((optInTimePeriod - 1) as usize);
    }
    pub(crate) fn correl_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal0: &[f64],
        inReal1: &[f64],
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
        let _assertLb = self.correl_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal0.len());
        assert!(_assertStart > endIdx || endIdx < inReal1.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut sumXY: f64 = 0.0_f64;
        let mut sumX: f64 = 0.0_f64;
        let mut sumY: f64 = 0.0_f64;
        let mut sumX2: f64 = 0.0_f64;
        let mut sumY2: f64 = 0.0_f64;
        let mut x: f64 = 0.0_f64;
        let mut y: f64 = 0.0_f64;
        let mut trailingX: f64 = 0.0_f64;
        let mut trailingY: f64 = 0.0_f64;
        let mut shiftX: f64 = 0.0_f64;
        let mut shiftY: f64 = 0.0_f64;
        let mut ssX: f64 = 0.0_f64;
        let mut ssY: f64 = 0.0_f64;
        let mut spXY: f64 = 0.0_f64;
        let mut leavingX: f64 = 0.0_f64;
        let mut leavingY: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut invPeriod: f64 = 0.0_f64;
        let mut lookbackTotal: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut j: usize = 0_usize;
        let mut windowStart: usize = 0_usize;
        let mut barsSinceReseed: usize = 0_usize;
        // Move up the start index if there is not
        // enough initial data.
        // One reciprocal instead of three divisions per bar, as TA_VAR does. The
        // extra rounding it costs is invisible next to what the shift recovers, and
        // it is what keeps this form cheaper than the one it replaces.
        invPeriod = 1.0 / (optInTimePeriod as f64);
        lookbackTotal = (optInTimePeriod - 1) as usize;
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
        trailingIdx = startIdx - lookbackTotal;
        // Measure both series against a shift near the window, exactly as TA_VAR
        // does (#118). The running sums then hold deviations rather than raw levels,
        // so ssX = sumX2-(sumX*sumX)*invPeriod is no longer a difference of two
        // ~period*mean^2 quantities. Without this the extracted sum of squares keeps
        // only the digits that survive that subtraction: at a $100 price level with a
        // 1e-5 spread that is three of them, and the correlation of two perfectly
        // correlated series came back as 0, as -1, or as -1.73 (#242).
        //
        // Anchor on the first window value here; every later re-anchor uses the
        // window mean, which is better centred but costs a pass this one cannot
        // afford before the sums exist.
        shiftX = inReal0[trailingIdx];
        shiftY = inReal1[trailingIdx];
        // Calculate the initial values (the window less its last bar).
        sumY2 = 0.0;
        sumX2 = sumY2;
        sumY = sumX2;
        sumX = sumY;
        sumXY = sumX;
        // for( j = trailingIdx; j < startIdx; j += 1 )
        j = trailingIdx;
        while j < startIdx {
            x = inReal0[j] - shiftX;
            sumX += x;
            sumX2 += x * x;
            y = inReal1[j] - shiftY;
            sumXY += x * y;
            sumY += y;
            sumY2 += y * y;
            j += 1;
        }
        today = startIdx;
        outIdx = 0;
        barsSinceReseed = (32 * optInTimePeriod) as usize;
        leavingX = 0.0;
        leavingY = 0.0;
        loop {
            // Add the incoming value, measured against the shift.
            x = inReal0[today] - shiftX;
            sumX += x;
            sumX2 += x * x;
            y = inReal1[today] - shiftY;
            sumXY += x * y;
            sumY += y;
            sumY2 += y * y;
            ssX = sumX2 - sumX * sumX * invPeriod;
            ssY = sumY2 - sumY * sumY * invPeriod;
            spXY = sumXY - sumX * sumY * invPeriod;
            // Re-anchor and rebuild with a fresh two-pass when the shift has gone
            // stale. Same three triggers as TA_VAR: either sum of squares has shrunk
            // below 1e-6 of the squared deviations it is extracted from; OR the value
            // the PREVIOUS bar removed sat so far from the shift that its squared term
            // dwarfs what remains (a large outlier transiting the window buries the
            // small terms below its ulp, and the residue it leaves is cancellation
            // garbage); OR at least every 32 windows, so a slow drift stays bounded
            // however long the series runs.
            //
            // One bar late is correct, not a compromise. leavingX/leavingY are set by
            // the removal at the BOTTOM of the loop, so the bar on which the outlier
            // actually leaves still computes its own output from sums that legitimately
            // contain it. The trigger then fires on the NEXT bar -- the first one whose
            // sums carry the residue -- and the reseed below recomputes that bar's
            // output before it is written. No bar is ever emitted from the residue.
            //
            // The triggers watch ssX and ssY only, never spXY. A vanishing spXY is a
            // legitimate answer - two uncorrelated series - not a loss of digits, and
            // reseeding on it would rebuild the window on every bar of ordinary data.
            // This is where the analogy with TA_VAR stops: variance has one extracted
            // quantity and all of it is signal.
            //
            // Reading the window here is safe when outReal aliases an input: the
            // outputs written so far occupy [0, outIdx-1] while windowStart is
            // startIdx-lookbackTotal+outIdx, which is >= outIdx.
            barsSinceReseed -= 1;
            if ssX < 0.000001 * sumX2
                || ssY < 0.000001 * sumY2
                || leavingX > 1000000.0 * sumX2
                || leavingY > 1000000.0 * sumY2
                || barsSinceReseed <= 0
            {
                barsSinceReseed = (32 * optInTimePeriod) as usize;
                windowStart = today - lookbackTotal;
                // Both means in one pass over the window: the rebuild below is the
                // only O(period) work on this function's hot path, so it is walked
                // twice, not three times.
                tempReal = 0.0;
                shiftY = 0.0;
                for j in (windowStart as usize)..(today as usize) + 1 {
                    tempReal += inReal0[j];
                    shiftY += inReal1[j];
                }
                j = (today as usize) + 1;
                shiftX = tempReal * invPeriod;
                shiftY = shiftY * invPeriod;
                sumY2 = 0.0;
                sumX2 = sumY2;
                sumY = sumX2;
                sumX = sumY;
                sumXY = sumX;
                for j in (windowStart as usize)..(today as usize) + 1 {
                    x = inReal0[j] - shiftX;
                    sumX += x;
                    sumX2 += x * x;
                    y = inReal1[j] - shiftY;
                    sumXY += x * y;
                    sumY += y;
                    sumY2 += y * y;
                }
                j = (today as usize) + 1;
                ssX = sumX2 - sumX * sumX * invPeriod;
                ssY = sumY2 - sumY * sumY * invPeriod;
                spXY = sumXY - sumX * sumY * invPeriod;
                // A sum of squares is non-negative by definition, but this one is
                // extracted as a difference, so its SIGN is not guaranteed on a window
                // sitting inside a flat stretch. Enforce the invariant HERE and not at
                // the divide: a negative ssX always reseeds on the same bar (it makes
                // the first trigger's `negative < non-negative` true whenever sumX2 is
                // positive, and sumX2 == 0 reduces that trigger to `ssX < 0`), so the
                // divide below can rely on both being >= 0 and needs no sign test of
                // its own. CHANGING THE TRIGGERS MEANS RE-CHECKING THIS.
                if ssX < 0.0 {
                    ssX = 0.0;
                }
                if ssY < 0.0 {
                    ssY = 0.0;
                }
            }
            // Save the trailing values before writing the output, since the input
            // and output might be the same array.
            trailingX = inReal0[trailingIdx] - shiftX;
            trailingY = inReal1[trailingIdx] - shiftY;
            trailingIdx += 1;
            // Output the new coefficient.
            //
            // Each sum of squares is tested against its OWN scale, not the pair
            // against a fixed band. The product ssX*ssY carries the fourth power of
            // the window's spread, so an absolute threshold on it rejects a perfectly
            // well-defined correlation as soon as the data is small - and, worse,
            // lets a pair of NEGATIVE sums through, their signs cancelling into a
            // plausible-looking result of the wrong sign. Testing each factor
            // separately is what forecloses both.
            //
            // The literal is TA_EPSILON. This is deliberately NOT TA_IS_ZERO_SCALED,
            // whose fabs() would admit a LARGE NEGATIVE ssX -- exactly the operand
            // that must never reach the square root. A plain `>` rejects it, and it
            // is also the cheaper test: the two fabs() cost ~7% of this function's
            // runtime, and buy a wrong answer.
            //
            // sqrt(ssX*ssY) rather than sqrt(ssX)*sqrt(ssY): the guard has already
            // established both are positive, so the product needs no protection from
            // a negative operand, and the second square root is worth ~14% of this
            // function's runtime (measured, #395).
            //
            // The product is then tested on its own, because neither factor's test
            // implies it: at that fourth power it underflows to exactly 0.0 while ssX
            // and ssY are still ordinary normals (#395). A zero divisor there gives
            // NaN, which the clamp below does NOT catch -- NaN fails both comparisons
            // -- or an infinity the clamp rewrites into a perfect correlation. Exact,
            // not a band: an absolute band on the product is the #253 defect at a new
            // address. At the other end the product overflows to +Inf and the quotient
            // is 0.0, the degenerate answer anyway.
            if ssX > 0.00000000000001 * sumX2 && ssY > 0.00000000000001 * sumY2 && ssX * ssY > 0.0 {
                tempReal = spXY / (ssX * ssY).sqrt();
                // A correlation coefficient cannot leave [-1,1]; rounding in the
                // three sums can still put it a few ulp outside.
                if tempReal > 1.0 {
                    tempReal = 1.0;
                } else if tempReal < 0_f64 - 1.0 {
                    tempReal = 0_f64 - 1.0;
                }
                outReal[outIdx] = tempReal;
                outIdx += 1;
            } else {
                outReal[outIdx] = 0.0;
                outIdx += 1;
            }
            // Remove the trailing values (prepares the next window).
            leavingX = trailingX * trailingX;
            leavingY = trailingY * trailingY;
            sumX -= trailingX;
            sumX2 -= leavingX;
            sumXY -= trailingX * trailingY;
            sumY -= trailingY;
            sumY2 -= leavingY;
            today += 1;
            if !(today <= endIdx) {
                break;
            }
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn correl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal0: &[f64],
        inReal1: &[f64],
        optInTimePeriod: i32,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.correl_lookback(optInTimePeriod)?;
        let _guardStart = if startIdx > _guardLb {
            startIdx
        } else {
            _guardLb
        };
        if inReal0.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        if inReal1.len() < endIdx + 1 {
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
        let retCode = self.correl_impl(
            startIdx,
            endIdx,
            inReal0,
            inReal1,
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
