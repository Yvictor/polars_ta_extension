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

// SMA-only backport of TA-Lib b3f0fa17d0e3485c39ed042d86fff7116c0430a4,
// ta_codegen/input/mavp/mavp.c. Other MA and guarded routes remain unchanged.
use super::*;

pub(super) fn call(
    price: &[f64],
    periods: &[f64],
    min: i32,
    max: i32,
    output: &mut [f64],
) -> Result<OutRange, RetCode> {
    let end = price
        .len()
        .checked_sub(1)
        .ok_or(RetCode::OutOfRangeEndIndex)?;
    if end > Core::INDEX_MAX {
        return Err(RetCode::OutOfRangeEndIndex);
    }
    let start = crate::native::core().mavp_lookback(min, max, MAType::SMA)?;
    let min = if min == i32::MIN { 2 } else { min };
    let max = if max == i32::MIN { 30 } else { max };
    if periods.len() < price.len() {
        return Err(RetCode::BadParam);
    }
    let count = price.len().saturating_sub(start);
    if output.is_empty() || output.len() < count {
        return Err(RetCode::BadParam);
    }
    if count == 0 {
        return Ok(OutRange {
            beg_idx: 0,
            count: 0,
        });
    }

    let mut selected = vec![0_i32; count];
    let (mut min_used, mut max_used) = (max, min);
    for (slot, &value) in selected.iter_mut().zip(&periods[start..=end]) {
        let period = if !(value >= f64::from(min)) {
            min
        } else if value > f64::from(max) {
            max
        } else {
            value as i32
        };
        *slot = period;
        min_used = min_used.min(period);
        max_used = max_used.max(period);
    }
    if min_used == max_used {
        return crate::native::core().ma(start, end, price, min_used, MAType::SMA, output);
    }
    let mut last = vec![-1_i32; (max_used - min_used + 1) as usize];
    for (i, &period) in selected.iter().enumerate() {
        last[(period - min_used) as usize] = i as i32;
    }
    for period in min_used..=max_used {
        let last = last[(period - min_used) as usize];
        if last < 0 {
            continue;
        }
        // `last` was recorded from `selected`, so width <= count. The
        // lookback proves start >= period - 1, and start + count == price.len().
        // Cut every iterator to the same checked width before any stores;
        // their zip therefore visits exactly the original 0..=last rows.
        let width = last as usize + 1;
        let selected = &selected[..width];
        let incoming = &price[start..][..width];
        let output = &mut output[..width];
        if period == 1 {
            for ((&value, &chosen), slot) in incoming.iter().zip(selected).zip(output.iter_mut()) {
                if chosen == period {
                    *slot = value;
                }
            }
        } else {
            // Preserve SMA's original seed, add/copy/subtract order and anchor.
            let lag = period as usize - 1;
            let mut total = 0.;
            for &value in &price[start - lag..start] {
                total += value;
            }
            let outgoing = &price[start - lag..][..width];
            for (((&incoming, &outgoing), &chosen), slot) in incoming
                .iter()
                .zip(outgoing)
                .zip(selected)
                .zip(output.iter_mut())
            {
                total += incoming;
                let value = total;
                total -= outgoing;
                if chosen == period {
                    *slot = value / f64::from(period);
                }
            }
        }
    }
    Ok(OutRange {
        beg_idx: start,
        count,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    const POISON: f64 = f64::from_bits(0x7ff8_0000_0000_55aa);
    fn same(a: f64, b: f64) -> bool {
        a.to_bits() == b.to_bits() || (a.is_nan() && b.is_nan())
    }
    #[test]
    fn selected_sma_is_exact_against_released_mavp_and_keeps_tails() {
        let core = crate::native::core();
        let mut cases = 0;
        for n in [1, 2, 29, 30, 31, 64, 257] {
            for (min, max) in [(1, 1), (1, 14), (2, 30), (1, 128)] {
                for shape in 0..5 {
                    let periods: Vec<_> = (0..n)
                        .map(|i| match shape {
                            0 => 14.,
                            1 => [3., 5., 9., 14.][i % 4],
                            2 => (min + i as i32 % (max - min + 1)) as f64,
                            3 => [3., 5., 9., 14.][(i * 4 / n).min(3)],
                            _ => [f64::NAN, f64::NEG_INFINITY, 1., 3.75, 9., f64::INFINITY][i % 6],
                        })
                        .collect();
                    for pattern in 0..6 {
                        let mut price: Vec<_> = (0..n)
                            .map(|i| match pattern {
                                0 => 100. + ((i * 17) % 97) as f64 / 100.,
                                1 => {
                                    if i % 2 == 0 {
                                        -0.
                                    } else {
                                        0.
                                    }
                                }
                                2 => 1e9 + (i % 11) as f64 / 100.,
                                3 => 2e307,
                                _ => 100. + (i % 17) as f64 / 100.,
                            })
                            .collect();
                        if pattern == 4 {
                            price[n / 2] = f64::NAN;
                        }
                        if pattern == 5 {
                            price[n / 2] = f64::INFINITY;
                        }
                        let mut old = vec![POISON; n + 8];
                        let mut new = old.clone();
                        let expected = core
                            .mavp(0, n - 1, &price, &periods, min, max, MAType::SMA, &mut old)
                            .unwrap();
                        let actual = call(&price, &periods, min, max, &mut new).unwrap();
                        assert_eq!(
                            (expected.beg_idx, expected.count),
                            (actual.beg_idx, actual.count)
                        );
                        assert!(
                            old.iter().zip(&new).all(|(&a, &b)| same(a, b)),
                            "n{n}/{min}/{max}/shape{shape}/pattern{pattern}"
                        );
                        assert!(new[actual.count..]
                            .iter()
                            .all(|v| v.to_bits() == POISON.to_bits()));
                        cases += 1;
                    }
                }
            }
        }
        assert_eq!(cases, 840);
    }
    #[test]
    fn unequal_selected_prefixes_match_each_direct_sma_without_touching_tail() {
        let core = crate::native::core();
        let mut checked = 0;
        for n in [31usize, 32, 33, 64, 65, 257, 1025] {
            for pattern in 0..4 {
                let price: Vec<_> = (0..n)
                    .map(|i| match pattern {
                        0 => 100. + ((i * 17) % 97) as f64 / 100.,
                        1 => {
                            if i % 2 == 0 {
                                -0.
                            } else {
                                0.
                            }
                        }
                        2 => {
                            if i == n / 2 {
                                f64::NEG_INFINITY
                            } else {
                                100.
                            }
                        }
                        _ => {
                            if i == n / 2 {
                                f64::NAN
                            } else {
                                100.
                            }
                        }
                    })
                    .collect();
                let start = 29;
                let count = n - start;
                // Different last uses, including single-row prefixes and a
                // final selected row, exercise all four equal-width cuts.
                let periods: Vec<_> = (0..n)
                    .map(|i| {
                        if i == start {
                            1.
                        } else if i == start + 1 {
                            30.
                        } else if i + 1 == n {
                            2.
                        } else {
                            [3., 5., 9., 14.][i % 4]
                        }
                    })
                    .collect();
                let mut output = vec![POISON; count + 8];
                let range = call(&price, &periods, 1, 30, &mut output).unwrap();
                assert_eq!((range.beg_idx, range.count), (start, count));
                for period in [1, 2, 3, 5, 9, 14, 30] {
                    let mut direct = vec![POISON; count];
                    let range = core
                        .ma(start, n - 1, &price, period, MAType::SMA, &mut direct)
                        .unwrap();
                    assert_eq!((range.beg_idx, range.count), (start, count));
                    for (i, &selected) in periods[start..].iter().enumerate() {
                        if selected == f64::from(period) {
                            assert!(
                                same(output[i], direct[i]),
                                "n{n}/pattern{pattern}/period{period}/row{i}"
                            );
                            if period == 1 {
                                assert_eq!(output[i].to_bits(), price[start + i].to_bits());
                            }
                            checked += 1;
                        }
                    }
                }
                assert!(output[count..]
                    .iter()
                    .all(|v| v.to_bits() == POISON.to_bits()));
            }
        }
        assert_eq!(checked, 5216);
    }

    #[test]
    fn maximum_lag_and_minimal_output_preserve_range_and_canaries() {
        let price: Vec<_> = (0..10003).map(|i| 100. + (i % 17) as f64 / 100.).collect();
        let mut periods = vec![1.; price.len()];
        periods[9999..].copy_from_slice(&[1., 10000., 2., 1.]);
        let mut expected = vec![POISON; 4];
        let range = crate::native::core()
            .mavp(
                0,
                price.len() - 1,
                &price,
                &periods,
                1,
                10000,
                MAType::SMA,
                &mut expected,
            )
            .unwrap();
        let mut storage = [POISON; 6];
        let actual = call(&price, &periods, 1, 10000, &mut storage[1..5]).unwrap();
        assert_eq!((actual.beg_idx, actual.count), (range.beg_idx, range.count));
        assert_eq!(actual.count, 4);
        assert!(storage[1..5]
            .iter()
            .zip(&expected)
            .all(|(&a, &b)| same(a, b)));
        assert_eq!(storage[0].to_bits(), POISON.to_bits());
        assert_eq!(storage[5].to_bits(), POISON.to_bits());
    }

    #[test]
    fn helper_matches_released_parameter_and_buffer_rejections() {
        let price = vec![100.; 64];
        let periods = vec![14.; 64];
        for (min, max, input_len, period_len, output_len) in [
            (i32::MIN, i32::MIN, 64usize, 64usize, 64usize),
            (30, 2, 64, 64, 64),
            (0, 30, 64, 64, 64),
            (2, 10001, 64, 64, 64),
            (2, 30, 0, 0, 64),
            (2, 30, 64, 63, 64),
            (2, 30, 64, 64, 34),
            (1, 1, 1, 1, 0),
            (2, 30, 29, 29, 0),
        ] {
            let mut old = vec![POISON; output_len];
            let mut new = old.clone();
            let expected = crate::native::core().mavp(
                0,
                input_len.checked_sub(1).unwrap_or(usize::MAX),
                &price[..input_len],
                &periods[..period_len],
                min,
                max,
                MAType::SMA,
                &mut old,
            );
            let actual = call(
                &price[..input_len],
                &periods[..period_len],
                min,
                max,
                &mut new,
            );
            assert_eq!(
                expected.as_ref().map(|r| (r.beg_idx, r.count)),
                actual.as_ref().map(|r| (r.beg_idx, r.count))
            );
            assert!(old.iter().zip(&new).all(|(&a, &b)| same(a, b)));
        }
    }
    #[test]
    fn only_normal_explicit_sma_skips_prefix_restoration() {
        let price = vec![100.; 200];
        let periods: Vec<_> = (0..200).map(|i| [3., 5., 9., 14.][i % 4]).collect();
        for matype in 0..14 {
            let params = Params::from([("matype".to_owned(), Param::Int(matype))]);
            let mut outputs = [Output::Real(vec![POISON; 200])];
            let result = super::super::call(
                ta_lib::abstract_api::FuncId::MAVP,
                &[&price, &periods],
                &params,
                &mut outputs,
                29,
            );
            assert_eq!(result.is_some(), matype == 0);
            if let Some(result) = result {
                assert!(!result.restore_native_prefix);
                result.result.unwrap();
            }
        }
        for case in 0..4 {
            let mut price = price.clone();
            let mut periods = periods.clone();
            let max = match case {
                0 => 129,
                1 => 10001,
                _ => 30,
            };
            if case == 2 {
                price[100] = 1025.;
            }
            if case == 3 {
                periods[100] = f64::NAN;
            }
            let params = Params::from([("maxperiod".to_owned(), Param::Int(max))]);
            let mut outputs = [Output::Real(vec![POISON; 200])];
            let call = super::super::call(
                ta_lib::abstract_api::FuncId::MAVP,
                &[&price, &periods],
                &params,
                &mut outputs,
                0,
            )
            .unwrap();
            assert!(call.restore_native_prefix);
            call.result.unwrap();
        }
    }
}
