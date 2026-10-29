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

//! TA-Lib0.8.3 scalar SAREXT batch body, adapted to free safe functions.
//! Preserve the original0.8.1 short-output expression `0.0 - sar` at exactly
//! two stores; this differs from0.8.3 unary negation when sar is positive zero.
//! See scripts/sarext_legacy_provenance.json for immutable source hashes.
#![forbid(unsafe_code)]
#![allow(non_snake_case, unused_variables, unused_mut, unused_assignments)]
use ta_lib::{Core, OutRange, RetCode};

fn c_min(a: f64, b: f64) -> f64 {
    core::hint::select_unpredictable(a < b, a, b)
}

pub(crate) fn call(
    core: &Core,
    startIdx: usize,
    endIdx: usize,
    inHigh: &[f64],
    inLow: &[f64],
    optInStartValue: f64,
    optInOffsetOnReverse: f64,
    optInAccelerationInitLong: f64,
    optInAccelerationLong: f64,
    optInAccelerationMaxLong: f64,
    optInAccelerationInitShort: f64,
    optInAccelerationShort: f64,
    optInAccelerationMaxShort: f64,
    outReal: &mut [f64],
) -> Result<OutRange, RetCode> {
    if startIdx > Core::INDEX_MAX {
        return Err(RetCode::OutOfRangeStartIndex);
    }
    if endIdx > Core::INDEX_MAX || endIdx < startIdx {
        return Err(RetCode::OutOfRangeEndIndex);
    }
    let _guardLb = core.sarext_lookback(
        optInStartValue,
        optInOffsetOnReverse,
        optInAccelerationInitLong,
        optInAccelerationLong,
        optInAccelerationMaxLong,
        optInAccelerationInitShort,
        optInAccelerationShort,
        optInAccelerationMaxShort,
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
    let retCode = dispatched_scalar(
        core,
        startIdx,
        endIdx,
        inHigh,
        inLow,
        optInStartValue,
        optInOffsetOnReverse,
        optInAccelerationInitLong,
        optInAccelerationLong,
        optInAccelerationMaxLong,
        optInAccelerationInitShort,
        optInAccelerationShort,
        optInAccelerationMaxShort,
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

// Public multiversion0.7.4 supplies runtime FMA detection and the portable
// fallback. Keep the scalar body inline so its .mul_add lowers in that context.
#[multiversion::multiversion(targets("x86_64+fma"), dispatcher = "direct")]
fn dispatched_scalar(
    core: &Core,
    startIdx: usize,
    endIdx: usize,
    inHigh: &[f64],
    inLow: &[f64],
    mut optInStartValue: f64,
    mut optInOffsetOnReverse: f64,
    mut optInAccelerationInitLong: f64,
    mut optInAccelerationLong: f64,
    mut optInAccelerationMaxLong: f64,
    mut optInAccelerationInitShort: f64,
    mut optInAccelerationShort: f64,
    mut optInAccelerationMaxShort: f64,
    outBegIdx: &mut usize,
    outNBElement: &mut usize,
    outReal: &mut [f64],
) -> RetCode {
    scalar(
        core,
        startIdx,
        endIdx,
        inHigh,
        inLow,
        optInStartValue,
        optInOffsetOnReverse,
        optInAccelerationInitLong,
        optInAccelerationLong,
        optInAccelerationMaxLong,
        optInAccelerationInitShort,
        optInAccelerationShort,
        optInAccelerationMaxShort,
        outBegIdx,
        outNBElement,
        outReal,
    )
}

#[inline(always)]
fn scalar(
    core: &Core,
    startIdx: usize,
    endIdx: usize,
    inHigh: &[f64],
    inLow: &[f64],
    mut optInStartValue: f64,
    mut optInOffsetOnReverse: f64,
    mut optInAccelerationInitLong: f64,
    mut optInAccelerationLong: f64,
    mut optInAccelerationMaxLong: f64,
    mut optInAccelerationInitShort: f64,
    mut optInAccelerationShort: f64,
    mut optInAccelerationMaxShort: f64,
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
    if optInStartValue == Core::REAL_DEFAULT {
        optInStartValue = 0e0;
    } else if !((optInStartValue >= Core::REAL_MIN) && (optInStartValue <= Core::REAL_MAX)) {
        return RetCode::BadParam;
    }
    if optInOffsetOnReverse == Core::REAL_DEFAULT {
        optInOffsetOnReverse = 0e0;
    } else if !((optInOffsetOnReverse >= 0e0) && (optInOffsetOnReverse <= Core::REAL_MAX)) {
        return RetCode::BadParam;
    }
    if optInAccelerationInitLong == Core::REAL_DEFAULT {
        optInAccelerationInitLong = 2e-2;
    } else if !((optInAccelerationInitLong >= 0e0) && (optInAccelerationInitLong <= Core::REAL_MAX))
    {
        return RetCode::BadParam;
    }
    if optInAccelerationLong == Core::REAL_DEFAULT {
        optInAccelerationLong = 2e-2;
    } else if !((optInAccelerationLong >= 0e0) && (optInAccelerationLong <= Core::REAL_MAX)) {
        return RetCode::BadParam;
    }
    if optInAccelerationMaxLong == Core::REAL_DEFAULT {
        optInAccelerationMaxLong = 2e-1;
    } else if !((optInAccelerationMaxLong >= 0e0) && (optInAccelerationMaxLong <= Core::REAL_MAX)) {
        return RetCode::BadParam;
    }
    if optInAccelerationInitShort == Core::REAL_DEFAULT {
        optInAccelerationInitShort = 2e-2;
    } else if !((optInAccelerationInitShort >= 0e0)
        && (optInAccelerationInitShort <= Core::REAL_MAX))
    {
        return RetCode::BadParam;
    }
    if optInAccelerationShort == Core::REAL_DEFAULT {
        optInAccelerationShort = 2e-2;
    } else if !((optInAccelerationShort >= 0e0) && (optInAccelerationShort <= Core::REAL_MAX)) {
        return RetCode::BadParam;
    }
    if optInAccelerationMaxShort == Core::REAL_DEFAULT {
        optInAccelerationMaxShort = 2e-1;
    } else if !((optInAccelerationMaxShort >= 0e0) && (optInAccelerationMaxShort <= Core::REAL_MAX))
    {
        return RetCode::BadParam;
    }
    let _assertLb = core
        .sarext_lookback(
            optInStartValue,
            optInOffsetOnReverse,
            optInAccelerationInitLong,
            optInAccelerationLong,
            optInAccelerationMaxLong,
            optInAccelerationInitShort,
            optInAccelerationShort,
            optInAccelerationMaxShort,
        )
        .unwrap_or(usize::MAX);
    let _assertStart = if startIdx > _assertLb {
        startIdx
    } else {
        _assertLb
    };
    assert!(_assertStart > endIdx || endIdx < inHigh.len());
    assert!(_assertStart > endIdx || endIdx < inLow.len());
    assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
    let mut startIdx = startIdx;
    let mut retCode: RetCode = RetCode::Success;
    let mut isLong: usize = 0_usize;
    let mut todayIdx: usize = 0_usize;
    let mut outIdx: usize = 0_usize;
    let mut tempInt: usize = 0_usize;
    let mut newHigh: f64 = 0.0_f64;
    let mut newLow: f64 = 0.0_f64;
    let mut prevHigh: f64 = 0.0_f64;
    let mut prevLow: f64 = 0.0_f64;
    let mut afLong: f64 = 0.0_f64;
    let mut afShort: f64 = 0.0_f64;
    let mut ep: f64 = 0.0_f64;
    let mut sar: f64 = 0.0_f64;
    let mut ep_temp: [f64; 1 as usize] = [0.0_f64; 1 as usize];
    // > 0 indicates long. == 0 indicates short
    // This function is the same as TA_SAR, except that the caller has
    // greater control on the SAR dynamic and initial state.
    //
    // In additon, the TA_SAREXT returns negative values when the position
    // is short. This allow to distinguish when the SAR do actually reverse.
    // Implementation of the SAR has been a little bit open to interpretation
    // since Wilder (the original author) did not define a precise algorithm
    // on how to bootstrap the algorithm. Take any existing software application
    // and you will see slight variation on how the algorithm was adapted.
    //
    // What is the initial trade direction? Long or short?
    // ===================================================
    // The interpretation of what should be the initial SAR values is
    // open to interpretation, particularly since the caller to the function
    // does not specify the initial direction of the trade.
    //
    // In TA-Lib, the following default logic is used:
    //  - Calculate +DM and -DM between the first and
    //    second bar. The highest directional indication will
    //    indicate the assumed direction of the trade for the second
    //    price bar.
    //  - In the case of a tie between +DM and -DM,
    //    the direction is LONG by default.
    //
    // What is the initial "extreme point" and thus SAR?
    // =================================================
    // The following shows how different people took different approach:
    //  - Metastock use the first price bar high/low depending of
    //    the direction. No SAR is calculated for the first price
    //    bar.
    //  - Tradestation use the closing price of the second bar. No
    //    SAR are calculated for the first price bar.
    //  - Wilder (the original author) use the SIP from the
    //    previous trade (cannot be implement here since the
    //    direction and length of the previous trade is unknonw).
    //  - The Magazine TASC seems to follow Wilder approach which
    //    is not practical here.
    //
    // TA-Lib "consume" the first price bar and use its high/low as the
    // initial SAR of the second price bar. I found that approach to be
    // the closest to Wilders idea of having the first entry day use
    // the previous extreme point, except that here the extreme point is
    // derived solely from the first price bar. I found the same approach
    // to be used by Metastock.
    //
    //
    // Can I force the initial SAR?
    // ============================
    // Yes. Using the optInStartValue_0 parameter:
    //  optInStartValue_0 >  0 : SAR is long at optInStartValue_0.
    //  optInStartValue_0 <  0 : SAR is short at fabs(optInStartValue_0).
    //
    // And when optInStartValue_0 == 0, the logic is the same as for TA_SAR
    // (See previous two sections).
    // Identify the minimum number of price bar needed
    // to calculate at least one output.
    //
    // Move up the start index if there is not
    // enough initial data.
    if startIdx < 1 {
        startIdx = 1;
    }
    // Make sure there is still something to evaluate.
    if startIdx > endIdx {
        (*outBegIdx) = 0;
        (*outNBElement) = 0;
        return RetCode::Success;
    }
    let inHigh = &inHigh[..=endIdx];
    let inLow = &inLow[..=endIdx];
    // Check if the acceleration factors are being defined by the user.
    // Make sure the acceleration and maximum are coherent.
    // If not, correct the acceleration.
    // Default afLong = 0.02
    // Default afShort = 0.02
    afLong = optInAccelerationInitLong;
    afShort = optInAccelerationInitShort;
    if afLong > optInAccelerationMaxLong {
        optInAccelerationInitLong = optInAccelerationMaxLong;
        afLong = optInAccelerationInitLong;
    }
    optInAccelerationLong = c_min(optInAccelerationMaxLong, optInAccelerationLong);
    if afShort > optInAccelerationMaxShort {
        optInAccelerationInitShort = optInAccelerationMaxShort;
        afShort = optInAccelerationInitShort;
    }
    optInAccelerationShort = c_min(optInAccelerationMaxShort, optInAccelerationShort);
    // Initialise SAR calculations
    if optInStartValue == 0_f64 {
        // Default action
        // Identify if the initial direction is long or short.
        // (ep is just used as a temp buffer here, the name
        //  of the parameter is not significant).
        let _xr0 = match core.minus_dm(startIdx, startIdx, inHigh, inLow, 1, &mut ep_temp) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        tempInt = _xr0.beg_idx;
        tempInt = _xr0.count;
        retCode = RetCode::Success;
        if ep_temp[0] > 0_f64 {
            isLong = 0;
        } else {
            isLong = 1;
        }
    } else if optInStartValue > 0_f64 {
        // Start Long
        isLong = 1;
    } else {
        // optInStartValue_0 < 0 => Start Short
        isLong = 0;
    }
    (*outBegIdx) = startIdx;
    outIdx = 0;
    // Write the first SAR.
    todayIdx = startIdx;
    newHigh = inHigh[todayIdx - 1];
    newLow = inLow[todayIdx - 1];
    if optInStartValue == 0_f64 {
        // Default action
        if isLong == 1 {
            ep = inHigh[todayIdx];
            sar = newLow;
        } else {
            ep = inLow[todayIdx];
            sar = newHigh;
        }
    } else if optInStartValue > 0_f64 {
        // Start Long at specified value.
        ep = inHigh[todayIdx];
        sar = optInStartValue;
    } else {
        // if optInStartValue < 0 => Start Short at specified value.
        ep = inLow[todayIdx];
        sar = (optInStartValue).abs();
    }
    // Cheat on the newLow and newHigh for the
    // first iteration.
    newLow = inLow[todayIdx];
    newHigh = inHigh[todayIdx];
    while todayIdx <= endIdx {
        prevLow = newLow;
        prevHigh = newHigh;
        newLow = inLow[todayIdx];
        newHigh = inHigh[todayIdx];
        todayIdx += 1;
        if isLong == 1 {
            // Switch to short if the low penetrates the SAR value.
            if newLow <= sar {
                // Switch and Overide the SAR with the ep
                isLong = 0;
                sar = ep;
                // Make sure the overide SAR is within
                // yesterday's and today's range.
                if sar < prevHigh {
                    sar = prevHigh;
                }
                if sar < newHigh {
                    sar = newHigh;
                }
                // Output the overide SAR
                if optInOffsetOnReverse != 0.0 {
                    sar += sar * optInOffsetOnReverse;
                }
                outReal[outIdx] = 0.0 - sar;
                outIdx += 1;
                // Adjust afShort and ep
                afShort = optInAccelerationInitShort;
                ep = newLow;
                // Calculate the new SAR
                sar = (afShort as f64).mul_add(ep - sar, sar);
                // Make sure the new SAR is within
                // yesterday's and today's range.
                if sar < prevHigh {
                    sar = prevHigh;
                }
                if sar < newHigh {
                    sar = newHigh;
                }
            } else {
                // No switch
                // Output the SAR (was calculated in the previous iteration)
                outReal[outIdx] = sar;
                outIdx += 1;
                // Adjust afLong and ep.
                if newHigh > ep {
                    ep = newHigh;
                    afLong += optInAccelerationLong;
                    if afLong > optInAccelerationMaxLong {
                        afLong = optInAccelerationMaxLong;
                    }
                }
                // Calculate the new SAR
                sar = (afLong as f64).mul_add(ep - sar, sar);
                // Make sure the new SAR is within
                // yesterday's and today's range.
                if sar > prevLow {
                    sar = prevLow;
                }
                if sar > newLow {
                    sar = newLow;
                }
            }
        // Switch to long if the high penetrates the SAR value.
        } else if newHigh >= sar {
            // Switch and Overide the SAR with the ep
            isLong = 1;
            sar = ep;
            // Make sure the overide SAR is within
            // yesterday's and today's range.
            if sar > prevLow {
                sar = prevLow;
            }
            if sar > newLow {
                sar = newLow;
            }
            // Output the overide SAR
            if optInOffsetOnReverse != 0.0 {
                sar -= sar * optInOffsetOnReverse;
            }
            outReal[outIdx] = sar;
            outIdx += 1;
            // Adjust afLong and ep
            afLong = optInAccelerationInitLong;
            ep = newHigh;
            // Calculate the new SAR
            sar = (afLong as f64).mul_add(ep - sar, sar);
            // Make sure the new SAR is within
            // yesterday's and today's range.
            if sar > prevLow {
                sar = prevLow;
            }
            if sar > newLow {
                sar = newLow;
            }
        } else {
            // No switch
            // Output the SAR (was calculated in the previous iteration)
            outReal[outIdx] = 0.0 - sar;
            outIdx += 1;
            // Adjust afShort and ep.
            if newLow < ep {
                ep = newLow;
                afShort += optInAccelerationShort;
                if afShort > optInAccelerationMaxShort {
                    afShort = optInAccelerationMaxShort;
                }
            }
            // Calculate the new SAR
            sar = (afShort as f64).mul_add(ep - sar, sar);
            // Make sure the new SAR is within
            // yesterday's and today's range.
            if sar < prevHigh {
                sar = prevHigh;
            }
            if sar < newHigh {
                sar = newHigh;
            }
        }
    }
    (*outNBElement) = outIdx;
    return RetCode::Success;
}

#[cfg(test)]
mod tests {
    use super::*;
    const DEFAULTS: [f64; 8] = [0., 0., 0.02, 0.02, 0.2, 0.02, 0.02, 0.2];
    fn compare(start: usize, end: usize, high: &[f64], low: &[f64], p: [f64; 8], capacity: usize) {
        let core = crate::native::core();
        let canary = f64::from_bits(0x7ff8_0012_3456_789a);
        let mut actual = vec![canary; capacity + 4];
        let mut expected = actual.clone();
        let a = call(
            core,
            start,
            end,
            high,
            low,
            p[0],
            p[1],
            p[2],
            p[3],
            p[4],
            p[5],
            p[6],
            p[7],
            &mut actual[2..capacity + 2],
        );
        let b = core.sarext(
            start,
            end,
            high,
            low,
            p[0],
            p[1],
            p[2],
            p[3],
            p[4],
            p[5],
            p[6],
            p[7],
            &mut expected[2..capacity + 2],
        );
        assert_eq!(a, b);
        let written = a.as_ref().map_or(0, |r| r.count);
        for (i, (a, b)) in actual.iter().zip(expected).enumerate() {
            if (2..2 + written).contains(&i) {
                if a.is_nan() || b.is_nan() {
                    assert!(a.is_nan() && b.is_nan());
                } else if b.to_bits() == (-0.0f64).to_bits() && a.to_bits() == 0 {
                } else {
                    assert_eq!(a.to_bits(), b.to_bits());
                }
            } else {
                assert_eq!(a.to_bits(), b.to_bits(), "physical canary at{i}");
            }
        }
    }

    #[test]
    fn public_range_validation_and_raw_unwritten_tails_match_core() {
        let high = [0., -0., 1., -1., 2., f64::NAN, f64::INFINITY, -2.];
        let low = [-1., 0., -0., -2., 1., f64::NEG_INFINITY, -1., -3.];
        for (start, end) in [
            (0, 0),
            (0, 1),
            (0, 7),
            (1, 7),
            (3, 5),
            (5, 3),
            (usize::MAX, usize::MAX),
            (0, Core::INDEX_MAX + 1),
            (Core::INDEX_MAX + 1, 1),
        ] {
            for capacity in [0, 1, 8, 20] {
                compare(start, end, &high, &low, DEFAULTS, capacity);
            }
        }
        for len in 0..8 {
            compare(0, 7, &high[..len], &low, DEFAULTS, 20);
            compare(0, 7, &high, &low[..len], DEFAULTS, 20);
        }
    }

    #[test]
    fn invalid_nonfinite_parameters_do_not_write_any_output() {
        let high = [2.; 8];
        let low = [1.; 8];
        for i in 0..8 {
            for v in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
                let mut options = DEFAULTS;
                options[i] = v;
                compare(0, 7, &high, &low, options, 8);
            }
        }
    }
    #[test]
    fn cold_parallel_dispatch_matches_portable_scalar_without_shared_mutable_inputs() {
        let barrier = std::sync::Barrier::new(8);
        std::thread::scope(|scope| {
            for worker in 0..8 {
                let barrier = &barrier;
                scope.spawn(move || {
                    let core = crate::native::core();
                    let high: Vec<f64> = (0..193)
                        .map(|i| [2., -0., 0., -1., f64::NAN, f64::INFINITY, 4.][(i + worker) % 7])
                        .collect();
                    let low: Vec<f64> = (0..193)
                        .map(|i| [1., -2., -0., 0., f64::NEG_INFINITY, 3.][(i + worker) % 6])
                        .collect();
                    let mut expected = vec![f64::from_bits(0x7ff8_0012_3456_789a); 201];
                    let mut beg = 0;
                    let mut count = 0;
                    let status = scalar(
                        core,
                        0,
                        192,
                        &high,
                        &low,
                        DEFAULTS[0],
                        DEFAULTS[1],
                        DEFAULTS[2],
                        DEFAULTS[3],
                        DEFAULTS[4],
                        DEFAULTS[5],
                        DEFAULTS[6],
                        DEFAULTS[7],
                        &mut beg,
                        &mut count,
                        &mut expected[2..199],
                    );
                    assert_eq!(status, RetCode::Success);
                    // Run this test alone in a fresh process to exercise the
                    // production dispatcher's first atomic selection concurrently.
                    barrier.wait();
                    for _ in 0..32 {
                        let mut actual = vec![f64::from_bits(0x7ff8_0012_3456_789a); 201];
                        let range = call(
                            core,
                            0,
                            192,
                            &high,
                            &low,
                            DEFAULTS[0],
                            DEFAULTS[1],
                            DEFAULTS[2],
                            DEFAULTS[3],
                            DEFAULTS[4],
                            DEFAULTS[5],
                            DEFAULTS[6],
                            DEFAULTS[7],
                            &mut actual[2..199],
                        )
                        .unwrap();
                        assert_eq!((range.beg_idx, range.count), (beg, count));
                        for (i, (a, b)) in actual.iter().zip(&expected).enumerate() {
                            if (2..2 + count).contains(&i) && (a.is_nan() || b.is_nan()) {
                                assert!(a.is_nan() && b.is_nan());
                            } else {
                                assert_eq!(a.to_bits(), b.to_bits());
                            }
                        }
                    }
                });
            }
        });
    }
}
