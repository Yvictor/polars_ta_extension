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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (cmou).
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
    pub fn cmou_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 14;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // CMOU needs optInTimePeriod price changes -> optInTimePeriod+1 prices ->
        // the first output is at index optInTimePeriod.
        //
        // Unlike the shipped CMO, there is NO unstable period: CMOU is a plain
        // moving-window sum, so its lookback is exactly the period.
        return Ok((optInTimePeriod) as usize);
    }
    pub(crate) fn cmou_impl(
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
        let _assertLb = self.cmou_lookback(optInTimePeriod).unwrap_or(usize::MAX);
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
        let mut trailingIdx: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut nullRun: usize = 0_usize;
        let mut upSum: f64 = 0.0_f64;
        let mut downSum: f64 = 0.0_f64;
        let mut sum: f64 = 0.0_f64;
        let mut diff: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut prevValue: f64 = 0.0_f64;
        let mut trailingValue: f64 = 0.0_f64;
        // CMOU -- unsmoothed Chande Momentum Oscillator (as in TradingView ta.cmo,
        // QuantConnect, pandas-ta default). Over the trailing optInTimePeriod changes
        // d = inReal[i]-inReal[i-1]: Su = sum of up-moves (d>0), Sd = sum of
        // |down-moves| (d<0); CMOU = 100*(Su-Sd)/(Su+Sd), 0 for a flat window. A plain
        // moving-window sum (drop oldest change, add newest), NOT TA_CMO's Wilder
        // smoothing -- hence no unstable period.
        //
        // In-place safe (outReal == inReal): the trailing read inReal[trailingIdx]
        // precedes this iteration's write (trailingIdx >= outIdx), and the oldest
        // change's older endpoint comes from the `trailingValue` cache, not a re-read.
        (*outBegIdx) = 0;
        (*outNBElement) = 0;
        lookbackTotal = self.cmou_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            return RetCode::Success;
        }
        // Accumulate the up/down sums over the first window: the optInTimePeriod
        // changes ending at startIdx (prices inReal[startIdx-optInTimePeriod ..
        // startIdx]). `trailingValue` caches the oldest price so the window's oldest
        // change can later be dropped by reading only the newer of its two prices.
        // `trailingIdx` points AT that newer price (one past the cached one).
        today = startIdx - lookbackTotal;
        trailingIdx = today + 1;
        prevValue = inReal[today];
        trailingValue = prevValue;
        upSum = 0.0;
        downSum = 0.0;
        // Consecutive changes of exactly zero, counted so that an empty window can
        // be recognized exactly (the shape #244 needed for MFI). The sums cannot
        // answer that question themselves once the window starts sliding: they are
        // maintained by add-then-subtract, so an emptied window leaves them holding
        // rounding residue of arbitrary sign rather than zero.
        nullRun = 0;
        // for( i = 0; i < ((optInTimePeriod) as usize); i += 1 )
        i = 0;
        while i < ((optInTimePeriod) as usize) {
            today += 1;
            tempReal = inReal[today];
            diff = tempReal - prevValue;
            prevValue = tempReal;
            if diff > 0.0 {
                upSum += diff;
            } else if diff < 0.0 {
                downSum -= diff;
            }
            if diff == 0.0 {
                nullRun += 1;
            } else {
                nullRun = 0;
            }
            i += 1;
        }
        // Emit the first output (bar startIdx). Su+Sd is a sum of non-negative
        // magnitudes, so it is zero only for an exactly flat window; guard the 0/0
        // exactly and emit 0.0. Not against a fixed band: a price change carries the
        // quote unit, so a constant put against the total zeroed the oscillator for
        // any instrument quoted below it (issue #253).
        //
        // Scale-then-divide -- (100*(Su-Sd))/(Su+Sd), NOT the 100*((Su-Sd)/(Su+Sd))
        // order TA_CMO/RSI use -- so CMOU is BIT-IDENTICAL to the reference unsmoothed
        // CMO of Tulip Indicators (ti_cmo) and pandas-ta-classic (cmo, talib=False),
        // which both scale before dividing. The two orders differ by <=1 ULP.
        outIdx = 0;
        sum = upSum + downSum;
        if sum > 0.0 {
            outReal[outIdx] = 100.0 * (upSum - downSum) / sum;
            outIdx += 1;
        } else {
            outReal[outIdx] = 0.0;
            outIdx += 1;
        }
        // Slide the window forward one bar at a time.
        today += 1;
        if today <= endIdx {
            let remaining = endIdx - today + 1;
            let trailing_inputs = &inReal[trailingIdx..][..remaining];
            let current_inputs = &inReal[today..][..remaining];
            let output_values = &mut outReal[outIdx..][..remaining];
            for ((&trailing_input, &current_input), output) in trailing_inputs
                .iter()
                .zip(current_inputs)
                .zip(output_values)
            {
                // Drop the oldest change: inReal[trailingIdx] - inReal[trailingIdx-1].
                // inReal[trailingIdx-1] comes from the cache (already overwritten when
                // outReal == inReal); inReal[trailingIdx] is read here, before this
                // iteration writes outReal[outIdx], so it is still the original price.
                tempReal = trailing_input;
                diff = tempReal - trailingValue;
                trailingValue = tempReal;
                trailingIdx += 1;
                if diff > 0.0 {
                    upSum -= diff;
                } else if diff < 0.0 {
                    downSum += diff;
                }
                // Add the newest change: inReal[today] - inReal[today-1].
                tempReal = current_input;
                diff = tempReal - prevValue;
                prevValue = tempReal;
                if diff > 0.0 {
                    upSum += diff;
                } else if diff < 0.0 {
                    downSum -= diff;
                }
                // Once a whole period of flat bars has gone by, every change in the
                // window is exactly zero, so both sums are known to be exactly zero and
                // the residue can be dropped.
                if diff == 0.0 {
                    nullRun += 1;
                } else {
                    nullRun = 0;
                }
                if nullRun >= ((optInTimePeriod) as usize) {
                    nullRun = (optInTimePeriod) as usize;
                    upSum = 0.0;
                    downSum = 0.0;
                }
                sum = upSum + downSum;
                if sum > 0.0 {
                    *output = 100.0 * (upSum - downSum) / sum;
                    outIdx += 1;
                } else {
                    *output = 0.0;
                    outIdx += 1;
                }
                today += 1;
            }
        }
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn cmou(
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
        let _guardLb = self.cmou_lookback(optInTimePeriod)?;
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
        let retCode = self.cmou_impl(
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
mod checked_window_tests {
    use super::*;

    mod reference {
        pub struct CompatCore;
        include!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/tests/fixtures/cmou_56.rs"
        ));
    }

    const CANARY: u64 = 0x7ff8_dead_beef_1234;

    fn compare(input: &[f64], start: usize, end: usize, period: i32, capacity: usize) -> usize {
        let mut old = vec![f64::from_bits(CANARY); capacity];
        let mut new = old.clone();
        let before = reference::CompatCore.cmou(start, end, input, period, &mut old);
        let after = CompatCore.cmou(start, end, input, period, &mut new);
        let count = match (before, after) {
            (Ok(a), Ok(b)) => {
                assert_eq!((a.beg_idx, a.count), (b.beg_idx, b.count));
                a.count
            }
            (Err(a), Err(b)) => {
                assert_eq!(a, b);
                0
            }
            pair => panic!("range/error differs: {pair:?}"),
        };
        for (i, (&a, &b)) in old.iter().zip(&new).enumerate() {
            if i < count && a.is_nan() && b.is_nan() {
                continue;
            }
            assert_eq!(
                a.to_bits(),
                b.to_bits(),
                "period={period} range={start}..={end} row={i}"
            );
            if i >= count {
                assert_eq!(b.to_bits(), CANARY, "write outside returned range");
            }
        }
        count
    }

    fn data(kind: usize, len: usize) -> Vec<f64> {
        let mut state = 0x26_10_29_u64;
        let mut values: Vec<f64> = (0..len)
            .map(|i| {
                state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                match kind {
                    0 => 100. + ((state >> 32) as f64 / u32::MAX as f64 - 0.5),
                    1 => 0.,
                    2 => -0.,
                    3 => {
                        if i % 2 == 0 {
                            -0.
                        } else {
                            0.
                        }
                    }
                    4 => 3.3,
                    5 => i as f64 * 0.25,
                    6 => {
                        if i < len / 2 {
                            1.
                        } else {
                            i as f64 * 0.25
                        }
                    }
                    7 => {
                        if i < len / 2 {
                            i as f64 * 0.25
                        } else {
                            1.
                        }
                    }
                    8 => {
                        if i % 2 == 0 {
                            1e-310
                        } else {
                            -1e-310
                        }
                    }
                    9 => 1e12 + (i % 7) as f64 * 0.25,
                    10 => {
                        if i % 2 == 0 {
                            f64::MAX * 0.75
                        } else {
                            -f64::MAX * 0.75
                        }
                    }
                    11 => f64::NAN,
                    _ => 100. + (i % 11) as f64 * 0.125,
                }
            })
            .collect();
        if len > 0 {
            match kind {
                12 => values[0] = f64::NAN,
                13 => values[len / 2] = f64::NAN,
                14 => values[len / 2] = f64::INFINITY,
                15 => values[len / 2] = f64::NEG_INFINITY,
                _ => (),
            }
        }
        values
    }

    #[test]
    fn exact_pinned_56_ranges_values_errors_and_tails() {
        let mut cases = 0;
        let mut written = 0;
        for len in [0, 1, 2, 3, 13, 14, 15, 16, 31, 64, 129, 257] {
            for kind in 0..16 {
                let input = data(kind, len);
                for period in [Core::INTEGER_DEFAULT, -1, 0, 1, 2, 3, 14, 30, 128, 100000] {
                    for (start, end) in [
                        (0, len.saturating_sub(1)),
                        (1, len.saturating_sub(1)),
                        (len / 2, len.saturating_sub(1)),
                        (0, len / 2),
                        (len, len),
                        (2, 1),
                    ] {
                        for capacity in [0, len.saturating_sub(15), len + 3] {
                            written += compare(&input, start, end, period, capacity);
                            cases += 1;
                        }
                    }
                }
            }
        }
        assert!(written > 100000);
        eprintln!("CMOU_WINDOW_EXACT cases={cases} written_values={written}");
    }

    #[test]
    fn exact_single_tail_bar_nonzero_start_and_maximum_period() {
        let input = data(0, 100033);
        for period in [2, 14, 128, 100000] {
            let start = period as usize;
            for end in [start, start + 1, input.len() - 1] {
                for anchor in [0, start, start + 1] {
                    compare(&input, anchor, end, period, input.len() + 5);
                }
            }
        }
        for (start, end) in [
            (Core::INDEX_MAX + 1, 0),
            (0, Core::INDEX_MAX + 1),
            (Core::INDEX_MAX, Core::INDEX_MAX),
        ] {
            compare(&[1., 2., 3.], start, end, 2, 4);
        }
    }
}
