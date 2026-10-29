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

// Checked batch window from TA-Lib PR #566, commit
// 2ea9da4c800244d3e09a8b7ef30b340913e03b38. Only the pinned 0.8.3 contract is used.
#![forbid(unsafe_code)]
use ta_lib::{Core, OutRange};

/// None leaves validation/error reporting to the existing native route.
pub(super) fn try_call(
    start: usize,
    end: usize,
    input: [&[f64]; 4],
    output: &mut [i32],
) -> Option<OutRange> {
    if start > Core::INDEX_MAX || end > Core::INDEX_MAX || end < start {
        return None;
    }
    let bound = end.checked_add(1)?;
    // High/low are numerically unused, but their public length checks are required.
    if input.iter().any(|values| values.len() < bound) || output.is_empty() {
        return None;
    }
    let first = start.max(2);
    if first > end {
        return Some(OutRange {
            beg_idx: 0,
            count: 0,
        });
    }
    let count = end - first + 1;
    let width = count + 1;
    let close = input[3].get(first.checked_sub(1)?..)?.get(..width)?;
    let open = input[0].get(first.checked_sub(1)?..)?.get(..width)?;
    let output = output.get_mut(..count)?;
    for ((close, open), slot) in close.windows(2).zip(open.windows(2)).zip(output.iter_mut()) {
        *slot = if (if close[1] >= open[1] { 1 } else { -1 }) == 1
            && (if close[0] >= open[0] { 1 } else { -1 }) == -1
            && (close[1] >= open[0] && open[1] < close[0]
                || close[1] > open[0] && open[1] <= close[0])
            || (if close[1] >= open[1] { 1 } else { -1 }) == -1
                && (if close[0] >= open[0] { 1 } else { -1 }) == 1
                && (open[1] >= close[0] && close[1] < open[0]
                    || open[1] > close[0] && close[1] <= open[0])
        {
            let color = if close[1] >= open[1] { 1 } else { -1 };
            if open[1] != close[0] && close[1] != open[0] {
                color * 100
            } else {
                color * 80
            }
        } else {
            0
        };
    }
    Some(OutRange {
        beg_idx: first,
        count,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use ta_lib::{
        abstract_api::{FuncId, InputType, OutputType},
        RetCode,
    };
    const CANARY: i32 = 1234567;

    fn compare(start: usize, end: usize, input: [&[f64]; 4], capacity: usize) {
        let mut expected = vec![CANARY; capacity + 6];
        let mut actual = expected.clone();
        let want = Core::new().cdlengulfing(
            start,
            end,
            input[0],
            input[1],
            input[2],
            input[3],
            &mut expected[2..2 + capacity],
        );
        let got = try_call(start, end, input, &mut actual[2..2 + capacity]);
        match want {
            Ok(range) => assert_eq!(got, Some(range)),
            Err(_) => assert_eq!(got, None),
        }
        assert_eq!(actual, expected);
    }

    #[test]
    fn pinned_metadata_is_ohlc_integer_with_no_parameters() {
        let info = FuncId::CDLENGULFING.info();
        assert_eq!(info.inputs.len(), 1);
        assert!(matches!(info.inputs[0].kind, InputType::Price));
        assert_eq!(info.inputs[0].flags.0, 15);
        assert!(info.opt_inputs.is_empty());
        assert_eq!(info.outputs.len(), 1);
        assert!(matches!(info.outputs[0].kind, OutputType::Integer));
        assert_eq!(Core::new().cdlengulfing_lookback(), Ok(2));
    }

    #[test]
    fn all_13_to_the_four_ieee_pairs_match_official_083() {
        let values = [
            f64::NEG_INFINITY,
            -f64::MAX,
            -2.,
            -1.,
            -0.,
            0.,
            f64::from_bits(1),
            1.,
            2.,
            f64::MAX,
            f64::INFINITY,
            f64::from_bits(0x7ff8_0000_0000_0042),
            f64::from_bits(0xfff0_0000_0000_0001),
        ];
        let core = Core::new();
        let mut hits = [0; 5];
        for previous_open in values {
            for previous_close in values {
                for current_open in values {
                    for current_close in values {
                        let open = [0., previous_open, current_open];
                        let close = [0., previous_close, current_close];
                        let high = [3.; 3];
                        let low = [-3.; 3];
                        let mut expected = [CANARY; 7];
                        let mut actual = expected;
                        let want = core
                            .cdlengulfing(0, 2, &open, &high, &low, &close, &mut expected[2..5])
                            .unwrap();
                        assert_eq!(
                            try_call(0, 2, [&open, &high, &low, &close], &mut actual[2..5]),
                            Some(want)
                        );
                        assert_eq!(actual, expected);
                        let slot = [-100, -80, 0, 80, 100]
                            .iter()
                            .position(|v| *v == actual[2])
                            .unwrap();
                        hits[slot] += 1;
                    }
                }
            }
        }
        assert!(
            hits.iter().all(|n| *n > 0),
            "all signed pattern values: {hits:?}"
        );
    }

    #[test]
    fn partial_and_empty_ranges_preserve_offset_outputs_and_tails() {
        let open: Vec<_> = (0..137)
            .map(|i| [3., 1., -0., 2., f64::INFINITY][i % 5])
            .collect();
        let close: Vec<_> = (0..137)
            .map(|i| [1., 4., 0., f64::NAN, -1., 2.][i % 6])
            .collect();
        let high = vec![8.; 137];
        let low = vec![-8.; 137];
        let input = [&open[3..], &high[3..], &low[3..], &close[3..]];
        for start in [0usize, 1, 2, 3, 17, 99] {
            for end in [start, start + 1, 130] {
                for capacity in [1, end.saturating_sub(start.max(2)) + 1, 140] {
                    compare(start, end, input, capacity);
                }
            }
        }
        compare(0, 0, input, 1);
        compare(0, 1, input, 1);
    }

    #[test]
    fn validation_failure_never_writes_and_declines_to_native() {
        let data = [1.; 5];
        for short in 0..4 {
            let mut input = [&data[..]; 4];
            input[short] = &data[..4];
            compare(0, 4, input, 5);
        }
        for (start, end) in [
            (3, 2),
            (usize::MAX, usize::MAX),
            (0, usize::MAX),
            (Core::INDEX_MAX + 1, 4),
            (0, Core::INDEX_MAX + 1),
        ] {
            compare(start, end, [&data; 4], 5);
        }
        compare(0, 4, [&data; 4], 2);
        compare(0, 1, [&data; 4], 0);
        let mut output = [CANARY; 3];
        assert_eq!(
            Core::new().cdlengulfing(0, 4, &data, &data[..4], &data, &data, &mut output),
            Err(RetCode::BadParam)
        );
        assert_eq!(
            try_call(0, 4, [&data, &data[..4], &data, &data], &mut output),
            None
        );
        assert_eq!(output, [CANARY; 3]);
    }

    #[test]
    fn compat_route_keeps_integer_origin_and_disables_unneeded_prefix_restore() {
        use crate::native::{Output, Params};
        let open = [1., 3., 1., 4., 2.];
        let high = [8.; 5];
        let low = [-8.; 5];
        let close = [2., 1., 4., 2., 5.];
        let mut outputs = [Output::Integer(vec![0; 5])];
        let call = crate::compat::call(
            FuncId::CDLENGULFING,
            &[&open, &high, &low, &close],
            &Params::new(),
            &mut outputs,
            2,
        )
        .unwrap();
        assert_eq!(
            call.result,
            Ok(OutRange {
                beg_idx: 2,
                count: 3
            })
        );
        assert!(!call.restore_native_prefix);
        let mut expected = vec![0; 5];
        Core::new()
            .cdlengulfing(0, 4, &open, &high, &low, &close, &mut expected[2..])
            .unwrap();
        let Output::Integer(actual) = &outputs[0] else {
            panic!("integer output")
        };
        assert_eq!(actual, &expected);
        assert!(crate::compat::call(
            FuncId::CDLENGULFING,
            &[&open, &high[..4], &low, &close],
            &Params::new(),
            &mut outputs,
            2
        )
        .is_none());
        let Output::Integer(actual) = &outputs[0] else {
            panic!("integer output")
        };
        assert_eq!(actual, &expected);
    }

    #[test]
    fn long_inputs_and_unused_ieee_high_low_match() {
        for len in [3, 100, 10000, 1000000] {
            let open: Vec<_> = (0..len)
                .map(|i| [1., 2., -0., f64::NAN, f64::INFINITY][i % 5])
                .collect();
            let close: Vec<_> = (0..len)
                .map(|i| [2., 1., 0., f64::NEG_INFINITY, 3., -1.][i % 6])
                .collect();
            let high = vec![f64::NAN; len];
            let low = vec![f64::NEG_INFINITY; len];
            compare(0, len - 1, [&open, &high, &low, &close], len + 7);
        }
    }
}
