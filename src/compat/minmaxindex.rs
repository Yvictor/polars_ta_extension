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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (minmaxindex).
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
    pub fn minmaxindex_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        return Ok((optInTimePeriod - 1) as usize);
    }
    pub(crate) fn minmaxindex_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outMinIdx: &mut [i32],
        outMaxIdx: &mut [i32],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .minmaxindex_lookback(optInTimePeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outMinIdx.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outMaxIdx.len());
        if (!outMinIdx.is_empty()
            && !outMaxIdx.is_empty()
            && outMinIdx.as_ptr() == outMaxIdx.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut highest: f64 = 0.0_f64;
        let mut lowest: f64 = 0.0_f64;
        let mut tmpHigh: f64 = 0.0_f64;
        let mut tmpLow: f64 = 0.0_f64;
        let mut outIdx: usize = 0_usize;
        let mut nbInitialElementNeeded: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut highestIdx: i32 = 0_i32;
        let mut lowestIdx: i32 = 0_i32;
        // Identify the minimum number of price bar needed
        // to identify at least one output over the specified
        // period.
        nbInitialElementNeeded = (optInTimePeriod - 1) as usize;
        // Move up the start index if there is not
        // enough initial data.
        if startIdx < nbInitialElementNeeded {
            startIdx = nbInitialElementNeeded;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // Proceed with the calculation for the requested range.
        // (The integer outputs can never share the real input's buffer —
        // different element type; issue #130.)
        outIdx = 0;
        today = startIdx;
        trailingIdx = startIdx - nbInitialElementNeeded;
        highestIdx = 0 - 1;
        highest = 0.0;
        lowestIdx = 0 - 1;
        lowest = 0.0;
        let output_count = endIdx - startIdx + 1;
        let inReal = &inReal[..=endIdx];
        let outMinIdx = &mut outMinIdx[..output_count];
        let outMaxIdx = &mut outMaxIdx[..output_count];
        for (output_index, max_slot) in outMaxIdx.iter_mut().enumerate() {
            outIdx = output_index;
            tmpHigh = inReal[today];
            tmpLow = tmpHigh;
            if highestIdx < ((trailingIdx) as i32) {
                highestIdx = (trailingIdx) as i32;
                highest = inReal[(highestIdx) as usize];
                i = (highestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmpHigh = inReal[i];
                    if tmpHigh > highest {
                        highestIdx = (i) as i32;
                        highest = tmpHigh;
                    }
                }
            } else if tmpHigh >= highest {
                highestIdx = (today) as i32;
                highest = tmpHigh;
            }
            if lowestIdx < ((trailingIdx) as i32) {
                lowestIdx = (trailingIdx) as i32;
                lowest = inReal[(lowestIdx) as usize];
                i = (lowestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmpLow = inReal[i];
                    if tmpLow < lowest {
                        lowestIdx = (i) as i32;
                        lowest = tmpLow;
                    }
                }
            } else if tmpLow <= lowest {
                lowestIdx = (today) as i32;
                lowest = tmpLow;
            }
            *max_slot = highestIdx;
            outMinIdx[outIdx] = (lowestIdx) as i32;
            outIdx += 1;
            trailingIdx += 1;
            today += 1;
        }
        // Keep the outBegIdx relative to the
        // caller input before returning.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn minmaxindex(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        outMinIdx: &mut [i32],
        outMaxIdx: &mut [i32],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.minmaxindex_lookback(optInTimePeriod)?;
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
        if outMinIdx.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outMaxIdx.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.minmaxindex_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            &mut outBegIdx,
            &mut outNBElement,
            outMinIdx,
            outMaxIdx,
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

    #[test]
    fn rescans_keep_oldest_ties_and_incremental_updates_take_newest_ties() {
        let values = [0., 5., 5., 1., 1., 1., 7., 7., 0.];
        let mut min = [-99; 9];
        let mut max = [-99; 9];
        let range = CompatCore
            .minmaxindex(0, 8, &values, 3, &mut min, &mut max)
            .unwrap();
        assert_eq!((range.beg_idx, range.count), (2, 7));
        assert_eq!(&min[..7], &[0, 3, 4, 5, 5, 5, 8]);
        assert_eq!(&max[..7], &[1, 1, 2, 3, 6, 7, 7]);
        assert_eq!(&min[7..], &[-99; 2]);
        assert_eq!(&max[7..], &[-99; 2]);

        let range = CompatCore
            .minmaxindex(4, 8, &values, 3, &mut min, &mut max)
            .unwrap();
        assert_eq!((range.beg_idx, range.count), (4, 5));
        assert_eq!(&min[..5], &[3, 5, 5, 5, 8]);
        assert_eq!(&max[..5], &[2, 3, 6, 7, 7]);
    }

    #[test]
    fn nan_rescan_seeds_and_signed_zero_ties_keep_the_legacy_indices() {
        let values = [f64::NAN, 3., 2., f64::NAN, 1., 4.];
        let mut min = [0; 5];
        let mut max = [0; 5];
        CompatCore
            .minmaxindex(0, 5, &values, 2, &mut min, &mut max)
            .unwrap();
        assert_eq!(min, [0, 2, 2, 3, 4]);
        assert_eq!(max, [0, 1, 2, 3, 5]);

        CompatCore
            .minmaxindex(0, 3, &[-0., 0., -0., 0.], 2, &mut min, &mut max)
            .unwrap();
        assert_eq!(&min[..3], &[0, 1, 2]);
        assert_eq!(&max[..3], &[0, 1, 2]);
    }

    #[test]
    fn output_capacity_and_no_output_ranges_preserve_the_public_contract() {
        let values = [1.; 5];
        let mut min = [0; 3];
        let mut max = [0; 3];
        assert!(CompatCore
            .minmaxindex(0, 4, &values, 3, &mut min, &mut max)
            .is_ok());
        assert_eq!(
            CompatCore.minmaxindex(0, 4, &values, 3, &mut min[..2], &mut max),
            Err(RetCode::BadParam)
        );
        let range = CompatCore
            .minmaxindex(0, 4, &values, 30, &mut [], &mut [])
            .unwrap();
        assert_eq!((range.beg_idx, range.count), (0, 0));
    }
}
