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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (maxindex).
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
    pub fn maxindex_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        return Ok((optInTimePeriod - 1) as usize);
    }
    pub(crate) fn maxindex_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outInteger: &mut [i32],
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
            .maxindex_lookback(optInTimePeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outInteger.len());
        let mut startIdx = startIdx;
        let mut highest: f64 = 0.0_f64;
        let mut tmp: f64 = 0.0_f64;
        let mut outIdx: usize = 0_usize;
        let mut nbInitialElementNeeded: usize = 0_usize;
        let mut trailingIdx: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut highestIdx: i32 = 0_i32;
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
        // (The integer output can never share the real input's buffer —
        // different element type; issue #130.)
        outIdx = 0;
        today = startIdx;
        trailingIdx = startIdx - nbInitialElementNeeded;
        highestIdx = 0 - 1;
        highest = 0.0;
        while today <= endIdx {
            tmp = inReal[today];
            if highestIdx < ((trailingIdx) as i32) {
                highestIdx = (trailingIdx) as i32;
                highest = inReal[(highestIdx) as usize];
                i = (highestIdx) as usize;
                while {
                    i += 1;
                    i
                } <= today
                {
                    tmp = inReal[i];
                    if tmp > highest {
                        highestIdx = (i) as i32;
                        highest = tmp;
                    }
                }
            } else if tmp >= highest {
                highestIdx = (today) as i32;
                highest = tmp;
            }
            outInteger[outIdx] = (highestIdx) as i32;
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
    pub fn maxindex(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        outInteger: &mut [i32],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.maxindex_lookback(optInTimePeriod)?;
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
        if outInteger.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.maxindex_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            &mut outBegIdx,
            &mut outNBElement,
            outInteger,
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
