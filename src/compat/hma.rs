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

// Batch-only HMA from official ta-lib 0.8.3, with bounded multiplier weights
// from TA-Lib 5da9e8d43333c13b5f46f30efe8460de12b1f68b.
// Used multiplier weights are exact integers up to 100000 and never index storage.
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
    pub fn hma_weights_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 20;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut sqrtPeriod: usize = 0_usize;
        sqrtPeriod = ((optInTimePeriod as f64).sqrt() as usize) as usize;
        return Ok(
            (self.wma_lookback(optInTimePeriod)? + self.wma_lookback((sqrtPeriod) as i32)?)
                as usize,
        );
    }
    pub(crate) fn hma_weights_impl(
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
            optInTimePeriod = 20;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .hma_weights_lookback(optInTimePeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackSqrt: usize = 0_usize;
        let mut halfPeriod: usize = 0_usize;
        let mut sqrtPeriod: usize = 0_usize;
        let mut ringSize: usize = 0_usize;
        let mut wmaStartIdx: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut w: f64 = 0.0_f64;
        let mut dividerFull: f64 = 0.0_f64;
        let mut dividerHalf: f64 = 0.0_f64;
        let mut dividerSqrt: f64 = 0.0_f64;
        let mut trailingIdxFull: usize = 0_usize;
        let mut trailingIdxHalf: usize = 0_usize;
        let mut periodSubFull: f64 = 0.0_f64;
        let mut periodSumFull: f64 = 0.0_f64;
        let mut trailingFull: f64 = 0.0_f64;
        let mut periodSubHalf: f64 = 0.0_f64;
        let mut periodSumHalf: f64 = 0.0_f64;
        let mut trailingHalf: f64 = 0.0_f64;
        let mut periodSubSqrt: f64 = 0.0_f64;
        let mut periodSumSqrt: f64 = 0.0_f64;
        let mut trailingSqrt: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut fullOut: f64 = 0.0_f64;
        let mut halfOut: f64 = 0.0_f64;
        let mut diffReal: f64 = 0.0_f64;
        let mut jFull: usize = 0_usize;
        let mut jHalf: usize = 0_usize;
        let mut q: usize = 0_usize;
        let mut rw: f64 = 0.0_f64;
        let mut ringWalk: usize = 0_usize;
        let mut lookbackFull: usize = 0_usize;
        let mut lookbackHalf: usize = 0_usize;
        let mut barsSinceReseedFull: usize = 0_usize;
        let mut barsSinceReseedHalf: usize = 0_usize;
        let mut barsSinceReseedSqrt: usize = 0_usize;
        let mut tempReal2: f64 = 0.0_f64;
        let mut local_dRing: [f64; 50] = [0.0_f64; 50];
        let mut heap_dRing: Vec<f64> = Vec::new();
        let mut dRing: &mut [f64] = &mut [];
        let mut dRing_Idx: usize = 0;
        // The de-lagged series needs only its last sqrt(n) values, so the whole
        // computation runs in one pass over a single window into the input:
        // three interleaved WMA rolling sums plus this small ring. The ring has
        // sqrt(n)-1 slots: on the stack while that fits the 50-slot prolog
        // (optInTimePeriod <= 2703), TA_Malloc from optInTimePeriod = 2704 up.
        // Hull Moving Average (Alan Hull, 2005):
        //
        //    HMA(n) = WMA( 2*WMA(price, Integer(n/2)) - WMA(price, n), Integer(SquareRoot(n)) )
        //
        // Both derived periods use the author's Integer() truncation; some other
        // published sources round to nearest instead, which is a visibly different
        // line. See hma.md and issue #139.
        //
        // Each of the three WMAs keeps TA_WMA's exact accumulation order
        // (periodSub/periodSum, lagged trailing subtract), so this fused pass is
        // BIT-IDENTICAL to composing three TA_WMA calls -- the composite
        // differential in test_composite.c holds it to that, memcmp-exact.
        // No smoothing at period of 1: the output is a copy of the input
        // (same convention as TA_MA for every MAType). Explicit because the
        // formula has no value there -- Integer(1/2) is 0 -- and the degenerate
        // arm below would leave a cancellation residual instead of a copy.
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
        halfPeriod = (optInTimePeriod / 2) as usize;
        sqrtPeriod = ((optInTimePeriod as f64).sqrt() as usize) as usize;
        lookbackSqrt = self.wma_lookback((sqrtPeriod) as i32).unwrap_or(usize::MAX);
        lookbackTotal = self.wma_lookback(optInTimePeriod).unwrap_or(usize::MAX) + lookbackSqrt;
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
        let inReal = &inReal[..=endIdx];
        // The two price WMAs are anchored where the first de-lagged value is
        // needed: lookbackSqrt bars before the first requested output.
        // wmaStartIdx >= optInTimePeriod-1 is implied by the clamp above.
        wmaStartIdx = startIdx - lookbackSqrt;
        dividerFull = (optInTimePeriod as f64) * ((optInTimePeriod + 1) as f64) / 2.0;
        // Prime the full-period WMA over the optInTimePeriod-1 bars before
        // wmaStartIdx, exactly as TA_WMA does (weights 1..period-1).
        lookbackFull = (optInTimePeriod - 1) as usize;
        periodSubFull = 0.0;
        periodSumFull = 0.0;
        trailingIdxFull = wmaStartIdx - lookbackFull;
        i = trailingIdxFull;
        w = 1.0;
        while i < wmaStartIdx {
            tempReal = inReal[i];
            i += 1;
            periodSubFull += tempReal;
            periodSumFull += tempReal * w;
            w += 1.0;
        }
        barsSinceReseedFull = (8 * optInTimePeriod) as usize;
        trailingFull = 0.0;
        outIdx = 0;
        // sqrtPeriod == 1 exactly when optInTimePeriod is 2 or 3; stated on the
        // param so the stream analyzer sees a param-pure dual-mode split.
        if optInTimePeriod == 2 || optInTimePeriod == 3 {
            // Degenerate regime, optInTimePeriod 2 or 3 only: halfPeriod and
            // sqrtPeriod are both 1, and a period-1 WMA is the identity (TA_WMA's
            // own short-circuit). The whole formula collapses to
            //    HMA[t] = 2*price[t] - WMA(price, n)[t]
            // with no de-lag ring at all. In-place note: the output store lands on
            // the SAME slot the trailing read just consumed (zero margin), so the
            // read stays ordered before the store.
            for today in (startIdx as usize)..(endIdx as usize) + 1 {
                tempReal = inReal[today];
                periodSubFull += tempReal;
                periodSubFull -= trailingFull;
                periodSumFull += tempReal * ((optInTimePeriod) as f64);
                barsSinceReseedFull -= 1;
                if barsSinceReseedFull <= 0 {
                    barsSinceReseedFull = (8 * optInTimePeriod) as usize;
                    periodSubFull = 0.0;
                    periodSumFull = 0.0;
                    rw = 1.0;
                    for jFull in (today - lookbackFull as usize)..(today as usize) + 1 {
                        tempReal2 = inReal[jFull];
                        periodSubFull += tempReal2;
                        periodSumFull += tempReal2 * rw;
                        rw += 1.0;
                    }
                    jFull = (today as usize) + 1;
                }
                trailingFull = inReal[trailingIdxFull];
                trailingIdxFull += 1;
                fullOut = periodSumFull / dividerFull;
                periodSumFull -= periodSubFull;
                outReal[outIdx] = 2.0 * tempReal - fullOut;
                outIdx += 1;
            }
            today = (endIdx as usize) + 1;
        } else {
            // General regime: optInTimePeriod >= 4, so halfPeriod >= 2 and
            // sqrtPeriod >= 2 -- no period-1 special cases below this point.
            dividerHalf = (halfPeriod as f64) * ((halfPeriod + 1) as f64) / 2.0;
            dividerSqrt = (sqrtPeriod as f64) * ((sqrtPeriod + 1) as f64) / 2.0;
            // Prime the half-period WMA the same way.
            lookbackHalf = halfPeriod - 1;
            periodSubHalf = 0.0;
            periodSumHalf = 0.0;
            trailingIdxHalf = wmaStartIdx - lookbackHalf;
            i = trailingIdxHalf;
            w = 1.0;
            while i < wmaStartIdx {
                tempReal = inReal[i];
                i += 1;
                periodSubHalf += tempReal;
                periodSumHalf += tempReal * w;
                w += 1.0;
            }
            barsSinceReseedHalf = 8 * halfPeriod;
            trailingHalf = 0.0;
            // The de-lagged value computed at bar t is consumed as the outer WMA's
            // trailing value sqrtPeriod-1 bars later, so a single-cursor ring of
            // sqrtPeriod-1 slots is enough: read the expiring value, overwrite the
            // slot with the current one, advance.
            ringSize = sqrtPeriod - 1;
            if ringSize < 1 {
                return RetCode::InternalError;
            }
            if (ringSize) as usize <= 50usize {
                dRing = &mut local_dRing[..(ringSize) as usize];
            } else {
                heap_dRing = vec![0.0_f64; (ringSize) as usize];
                dRing = &mut heap_dRing;
            }
            dRing_Idx = 0;
            // Warm-up: the sqrtPeriod-1 de-lagged values before the first output
            // prime the outer WMA (weights 1..sqrtPeriod-1) and fill the ring.
            periodSubSqrt = 0.0;
            periodSumSqrt = 0.0;
            trailingSqrt = 0.0;
            w = 1.0;
            // for( today = wmaStartIdx; today < startIdx; today += 1 )
            today = wmaStartIdx;
            while today < startIdx {
                tempReal = inReal[today];
                periodSubFull += tempReal;
                periodSubFull -= trailingFull;
                periodSumFull += tempReal * ((optInTimePeriod) as f64);
                barsSinceReseedFull -= 1;
                if barsSinceReseedFull <= 0 {
                    barsSinceReseedFull = (8 * optInTimePeriod) as usize;
                    periodSubFull = 0.0;
                    periodSumFull = 0.0;
                    rw = 1.0;
                    for jFull in (today - lookbackFull as usize)..(today as usize) + 1 {
                        tempReal2 = inReal[jFull];
                        periodSubFull += tempReal2;
                        periodSumFull += tempReal2 * rw;
                        rw += 1.0;
                    }
                    jFull = (today as usize) + 1;
                }
                trailingFull = inReal[trailingIdxFull];
                trailingIdxFull += 1;
                fullOut = periodSumFull / dividerFull;
                periodSumFull -= periodSubFull;
                periodSubHalf += tempReal;
                periodSubHalf -= trailingHalf;
                periodSumHalf += tempReal * ((halfPeriod) as f64);
                barsSinceReseedHalf -= 1;
                if barsSinceReseedHalf <= 0 {
                    barsSinceReseedHalf = 8 * halfPeriod;
                    periodSubHalf = 0.0;
                    periodSumHalf = 0.0;
                    rw = 1.0;
                    for jHalf in (today - lookbackHalf as usize)..(today as usize) + 1 {
                        tempReal2 = inReal[jHalf];
                        periodSubHalf += tempReal2;
                        periodSumHalf += tempReal2 * rw;
                        rw += 1.0;
                    }
                    jHalf = (today as usize) + 1;
                }
                trailingHalf = inReal[trailingIdxHalf];
                trailingIdxHalf += 1;
                halfOut = periodSumHalf / dividerHalf;
                periodSumHalf -= periodSubHalf;
                diffReal = 2.0 * halfOut - fullOut;
                periodSubSqrt += diffReal;
                periodSumSqrt += diffReal * w;
                w += 1.0;
                dRing[dRing_Idx] = diffReal;
                dRing_Idx += 1;
                if dRing_Idx >= dRing.len() {
                    dRing_Idx = 0;
                }
                today += 1;
            }
            barsSinceReseedSqrt = 8 * sqrtPeriod;
            // Steady state: one pass, three rolling WMAs. Writes trail every read by
            // at least sqrtPeriod-1 slots (the lookback clamp), so outReal == inReal
            // stays safe.
            for today in (startIdx as usize)..(endIdx as usize) + 1 {
                tempReal = inReal[today];
                periodSubFull += tempReal;
                periodSubFull -= trailingFull;
                periodSumFull += tempReal * ((optInTimePeriod) as f64);
                barsSinceReseedFull -= 1;
                if barsSinceReseedFull <= 0 {
                    barsSinceReseedFull = (8 * optInTimePeriod) as usize;
                    periodSubFull = 0.0;
                    periodSumFull = 0.0;
                    rw = 1.0;
                    for jFull in (today - lookbackFull as usize)..(today as usize) + 1 {
                        tempReal2 = inReal[jFull];
                        periodSubFull += tempReal2;
                        periodSumFull += tempReal2 * rw;
                        rw += 1.0;
                    }
                    jFull = (today as usize) + 1;
                }
                trailingFull = inReal[trailingIdxFull];
                trailingIdxFull += 1;
                fullOut = periodSumFull / dividerFull;
                periodSumFull -= periodSubFull;
                periodSubHalf += tempReal;
                periodSubHalf -= trailingHalf;
                periodSumHalf += tempReal * ((halfPeriod) as f64);
                barsSinceReseedHalf -= 1;
                if barsSinceReseedHalf <= 0 {
                    barsSinceReseedHalf = 8 * halfPeriod;
                    periodSubHalf = 0.0;
                    periodSumHalf = 0.0;
                    rw = 1.0;
                    for jHalf in (today - lookbackHalf as usize)..(today as usize) + 1 {
                        tempReal2 = inReal[jHalf];
                        periodSubHalf += tempReal2;
                        periodSumHalf += tempReal2 * rw;
                        rw += 1.0;
                    }
                    jHalf = (today as usize) + 1;
                }
                trailingHalf = inReal[trailingIdxHalf];
                trailingIdxHalf += 1;
                halfOut = periodSumHalf / dividerHalf;
                periodSumHalf -= periodSubHalf;
                diffReal = 2.0 * halfOut - fullOut;
                periodSubSqrt += diffReal;
                periodSubSqrt -= trailingSqrt;
                periodSumSqrt += diffReal * ((sqrtPeriod) as f64);
                // The outer WMA consumes a DERIVED series that is never
                // materialised, so its rescan walks the de-lag ring: dRing_Idx is
                // the oldest slot (the one about to expire) and diffReal is the
                // newest value, which together are the whole window. Oldest first,
                // weight counting up from 1 -- the priming order above.
                barsSinceReseedSqrt -= 1;
                if barsSinceReseedSqrt <= 0 {
                    barsSinceReseedSqrt = 8 * sqrtPeriod;
                    periodSubSqrt = 0.0;
                    periodSumSqrt = 0.0;
                    rw = 1.0;
                    ringWalk = dRing_Idx;
                    // for( q = 0; q < ringSize; q += 1 )
                    q = 0;
                    while q < ringSize {
                        tempReal2 = dRing[ringWalk];
                        periodSubSqrt += tempReal2;
                        periodSumSqrt += tempReal2 * rw;
                        rw += 1.0;
                        ringWalk += 1;
                        if ringWalk >= ringSize {
                            ringWalk = 0;
                        }
                        q += 1;
                    }
                    periodSubSqrt += diffReal;
                    periodSumSqrt += diffReal * ((sqrtPeriod) as f64);
                }
                trailingSqrt = dRing[dRing_Idx];
                dRing[dRing_Idx] = diffReal;
                dRing_Idx += 1;
                if dRing_Idx >= dRing.len() {
                    dRing_Idx = 0;
                }
                outReal[outIdx] = periodSumSqrt / dividerSqrt;
                outIdx += 1;
                periodSumSqrt -= periodSubSqrt;
            }
            today = (endIdx as usize) + 1;
        }
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn hma_weights(
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
        let _guardLb = self.hma_weights_lookback(optInTimePeriod)?;
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
        if outReal.is_empty() || outReal.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.hma_weights_impl(
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

#[cfg(test)]
mod tests {
    use super::*;
    const CANARY: u64 = 0x7ff8_0000_0000_55aa;

    fn check(input: &[f64], start: usize, period: i32) {
        let mut actual = vec![f64::from_bits(CANARY); input.len() + 8];
        let mut expected = actual.clone();
        let end = input.len() - 1;
        let a = LEGACY.hma_weights(start, end, input, period, &mut actual[1..]);
        let b = crate::native::core().hma(start, end, input, period, &mut expected[1..]);
        assert_eq!(
            a,
            b,
            "range: n={} start={start} period={period}",
            input.len()
        );
        for (row, (x, y)) in actual.iter().zip(&expected).enumerate() {
            assert_eq!(
                x.to_bits(),
                y.to_bits(),
                "bits: n={} start={start} period={period} row={row}",
                input.len()
            );
        }
        let range = a.unwrap();
        assert_eq!(actual[0].to_bits(), CANARY);
        assert!(actual[range.count + 1..]
            .iter()
            .all(|v| v.to_bits() == CANARY));
    }

    #[test]
    fn hma_batch_weights_match_frozen_core_across_ranges_and_reseeds() {
        for n in [1, 2, 3, 5, 10, 20, 21, 100, 1000, 10000, 1000000] {
            let input: Vec<f64> = (0..n).map(|i| 100. + (i as f64 * 0.13).sin()).collect();
            for p in [
                1, 2, 3, 4, 9, 10, 15, 16, 17, 20, 25, 26, 81, 82, 100, 101, 2703, 2704, 99999,
                100000,
            ] {
                check(&input, 0, p);
            }
        }
        for n in [22, 23, 53, 54, 55, 98, 99, 178, 179, 180] {
            let input: Vec<f64> = (0..n).map(|i| 100. + (i as f64 * 0.13).sin()).collect();
            check(&input, 0, 20);
        }
        let input: Vec<f64> = (0..1000).map(|i| 100. + (i as f64 * 0.13).sin()).collect();
        for start in [1, 19, 20, 25, 99, 100, 500] {
            check(&input, start, 20);
        }
    }

    #[test]
    fn hma_batch_weights_preserve_ieee_values_and_output_guards() {
        for pattern in 0..10 {
            let mut input: Vec<f64> = (0..1000).map(|i| 100. + (i as f64 * 0.13).sin()).collect();
            match pattern {
                0 => input.fill(0.),
                1 => input.fill(-0.),
                2 => input.fill(100.),
                3 => input
                    .iter_mut()
                    .enumerate()
                    .for_each(|(i, v)| *v = i as f64),
                4 => input
                    .iter_mut()
                    .enumerate()
                    .for_each(|(i, v)| *v = (1000 - i) as f64),
                5 => input
                    .iter_mut()
                    .enumerate()
                    .for_each(|(i, v)| *v = if i % 2 == 0 { 1e100 } else { -1e100 }),
                6 => input[0] = f64::from_bits(0x7ff8_0000_0000_1234),
                7 => input[500] = f64::from_bits(0x7ff8_0000_0000_4321),
                8 => input[0] = f64::INFINITY,
                9 => input[500] = f64::NEG_INFINITY,
                _ => unreachable!(),
            }
            for p in [1, 2, 3, 4, 20, 100] {
                for start in [0, 25, 500] {
                    check(&input, start, p);
                }
            }
        }
    }

    #[test]
    fn hma_batch_rejections_and_lookback_match_frozen_core() {
        for period in [
            i32::MIN,
            -1,
            0,
            1,
            2,
            20,
            2703,
            2704,
            99999,
            100000,
            100001,
            i32::MAX,
        ] {
            assert_eq!(
                LEGACY.hma_weights_lookback(period),
                crate::native::core().hma_lookback(period)
            );
        }
        let input = [1.; 32];
        for (start, end, p, out_len) in [
            (0, 31, 0, 40),
            (0, 31, 100001, 40),
            (5, 4, 20, 40),
            (0, 32, 20, 40),
            (0, 31, 20, 1),
            (0, 31, 20, 0),
            (0, 0, 20, 0),
            (Core::INDEX_MAX + 1, Core::INDEX_MAX + 1, 20, 40),
        ] {
            let mut a = vec![f64::from_bits(CANARY); out_len];
            let mut b = a.clone();
            let ar = LEGACY.hma_weights(start, end, &input, p, &mut a);
            let br = crate::native::core().hma(start, end, &input, p, &mut b);
            assert_eq!(ar, br);
            assert!(ar.is_err());
            assert!(a
                .iter()
                .zip(&b)
                .all(|(x, y)| x.to_bits() == y.to_bits() && x.to_bits() == CANARY));
        }
    }

    #[test]
    fn hma_dispatch_uses_exact_backport_without_prefix_restoration() {
        let input: Vec<f64> = (0..128).map(|i| 100. + (i as f64).sin()).collect();
        let mut outputs = [Output::Real(vec![f64::NAN; input.len()])];
        let mut params = Params::new();
        params.insert("timeperiod".into(), Param::Int(20));
        let call = super::super::call(FuncId::HMA, &[&input], &params, &mut outputs, 22).unwrap();
        assert!(!call.restore_native_prefix);
        assert_eq!(
            call.result.unwrap(),
            OutRange {
                beg_idx: 22,
                count: 106
            }
        );
        let Output::Real(values) = &outputs[0] else {
            unreachable!()
        };
        let mut expected = vec![f64::NAN; 128];
        crate::native::core()
            .hma(0, 127, &input, 20, &mut expected[22..])
            .unwrap();
        assert!(values
            .iter()
            .zip(&expected)
            .all(|(x, y)| x.to_bits() == y.to_bits()));
    }
}
