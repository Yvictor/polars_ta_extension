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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (percentile).
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
    pub fn percentile_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInPercentile: f64,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInPercentile == Self::REAL_DEFAULT {
            optInPercentile = 5e1;
        } else if !((optInPercentile >= 0e0) && (optInPercentile <= 1e2)) {
            return Err(RetCode::BadParam);
        }
        return Ok((optInTimePeriod - 1) as usize);
    }
    pub(crate) fn percentile_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        mut optInPercentile: f64,
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
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInPercentile == Self::REAL_DEFAULT {
            optInPercentile = 5e1;
        } else if !((optInPercentile >= 0e0) && (optInPercentile <= 1e2)) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .percentile_lookback(optInTimePeriod, optInPercentile)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut newValue: f64 = 0.0_f64;
        let mut oldValue: f64 = 0.0_f64;
        let mut result: f64 = 0.0_f64;
        let mut lookbackTotal: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut j: usize = 0_usize;
        let mut pos: usize = 0_usize;
        let mut nbSorted: usize = 0_usize;
        let mut rank: i32 = 0_i32;
        let mut local_ring: [f64; 30] = [0.0_f64; 30];
        let mut heap_ring: Vec<f64> = Vec::new();
        let mut ring: &mut [f64] = &mut [];
        let mut ring_Idx: usize = 0;
        let mut maxIdx_ring: usize = 29;
        let mut local_sorted: [f64; 30] = [0.0_f64; 30];
        let mut heap_sorted: Vec<f64> = Vec::new();
        let mut sorted: &mut [f64] = &mut [];
        let mut sorted_Idx: usize = 0;
        let mut maxIdx_sorted: usize = 29;
        // The window is carried twice: "ring" by age, "sorted" by value.
        lookbackTotal = (optInTimePeriod - 1) as usize;
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        if optInTimePeriod < 1 {
            return RetCode::InternalError;
        }
        if (optInTimePeriod) as usize <= 30usize {
            ring = &mut local_ring;
        } else {
            heap_ring = vec![0.0_f64; (optInTimePeriod) as usize];
            ring = &mut heap_ring;
        }
        maxIdx_ring = ((optInTimePeriod) as usize) - 1;
        ring_Idx = 0;
        if optInTimePeriod < 1 {
            return RetCode::InternalError;
        }
        if (optInTimePeriod) as usize <= 30usize {
            sorted = &mut local_sorted;
        } else {
            heap_sorted = vec![0.0_f64; (optInTimePeriod) as usize];
            sorted = &mut heap_sorted;
        }
        maxIdx_sorted = ((optInTimePeriod) as usize) - 1;
        sorted_Idx = 0;
        // Keep the multiply left of the divide. (P*n)/100 reproduces exact integer
        // arithmetic; P/100 is inexact in binary64 and lands the product just above
        // an integer, one order statistic too high, at exactly the round
        // percentages a caller types.
        rank = ((((optInPercentile) as f64) * (optInTimePeriod as f64) / 100.0).ceil()) as i32;
        if rank < 1 {
            rank = 1;
        }
        if rank > optInTimePeriod {
            rank = optInTimePeriod;
        }
        nbSorted = 0;
        i = startIdx - lookbackTotal;
        while i < startIdx {
            newValue = inReal[i];
            j = nbSorted;
            while j > 0 && sorted[j - 1] > newValue {
                sorted[j] = sorted[j - 1];
                j -= 1;
            }
            sorted[j] = newValue;
            nbSorted += 1;
            ring[ring_Idx] = newValue;
            i += 1;
            ring_Idx += 1;
            if ring_Idx > maxIdx_ring {
                ring_Idx = 0;
            }
        }
        // Both scratch buffers hold copies and inReal is never read below i, so
        // inReal and outReal may be the same buffer.
        //
        // Every buffer store sits BELOW the output store on purpose: deriving the
        // whole answer read-only above it is what lets the streaming peek frame drop
        // the state update rather than shadow a shift loop, which it cannot do.
        outIdx = 0;
        loop {
            newValue = inReal[i];
            pos = 0;
            while pos < lookbackTotal && sorted[pos] <= newValue {
                pos += 1;
            }
            if rank - 1 < ((pos) as i32) {
                result = sorted[(rank - 1) as usize];
            } else if rank - 1 == ((pos) as i32) {
                result = newValue;
            } else {
                result = sorted[(rank - 2) as usize];
            }
            outReal[outIdx] = result;
            outIdx += 1;
            // Shifting only the strictly greater entries leaves equal values in
            // insertion order, which is age order -- that is what lets the delete
            // below evict the oldest of a run by value alone, with no slot array.
            j = lookbackTotal;
            while j > pos {
                sorted[j] = sorted[j - 1];
                j -= 1;
            }
            sorted[pos] = newValue;
            ring[ring_Idx] = newValue;
            ring_Idx += 1;
            if ring_Idx > maxIdx_ring {
                ring_Idx = 0;
            }
            oldValue = ring[ring_Idx];
            j = 0;
            while j < lookbackTotal && sorted[j] < oldValue {
                j += 1;
            }
            while j < lookbackTotal {
                sorted[j] = sorted[j + 1];
                j += 1;
            }
            i += 1;
            if !(i <= endIdx) {
                break;
            }
        }
        (*outNBElement) = outIdx;
        (*outBegIdx) = startIdx;
        return RetCode::Success;
    }
    pub fn percentile(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInPercentile: f64,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.percentile_lookback(optInTimePeriod, optInPercentile)?;
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
        let retCode = self.percentile_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            optInPercentile,
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
