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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (mavp).
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
    pub fn mavp_lookback(
        &self,
        mut optInMinPeriod: i32,
        mut optInMaxPeriod: i32,
        mut optInMAType: MAType,
    ) -> Result<usize, RetCode> {
        if ((optInMinPeriod) as i32) == (i32::MIN) {
            optInMinPeriod = 2;
        } else if (((optInMinPeriod) as i32) < 1) || (((optInMinPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInMaxPeriod) as i32) == (i32::MIN) {
            optInMaxPeriod = 30;
        } else if (((optInMaxPeriod) as i32) < 1) || (((optInMaxPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::SMA;
        }
        // The same cross-parameter constraint mavp() rejects on. Each period is in
        // range on its own, so no prologue check can catch it, and without this the
        // lookback answers a usable number for a call that cannot run.
        if optInMinPeriod > optInMaxPeriod {
            return Err(RetCode::BadParam);
        }
        return Ok(self.ma_lookback(optInMaxPeriod, optInMAType)?);
    }
    pub(crate) fn mavp_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        inPeriods: &[f64],
        mut optInMinPeriod: i32,
        mut optInMaxPeriod: i32,
        mut optInMAType: MAType,
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
        if ((optInMinPeriod) as i32) == (i32::MIN) {
            optInMinPeriod = 2;
        } else if (((optInMinPeriod) as i32) < 1) || (((optInMinPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInMaxPeriod) as i32) == (i32::MIN) {
            optInMaxPeriod = 30;
        } else if (((optInMaxPeriod) as i32) < 1) || (((optInMaxPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::SMA;
        }
        let _assertLb = self
            .mavp_lookback(optInMinPeriod, optInMaxPeriod, optInMAType)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx < inPeriods.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut i: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut outputSize: usize = 0_usize;
        let mut firstOut: usize = 0_usize;
        let mut tempInt: i32 = 0_i32;
        let mut curPeriod: usize = 0_usize;
        let mut tempPeriod: f64 = 0.0_f64;
        let mut minPeriodReal: f64 = 0.0_f64;
        let mut maxPeriodReal: f64 = 0.0_f64;
        let mut firstOccurrence: usize = 0_usize;
        let mut lastOccurrence: usize = 0_usize;
        let mut bucketStart: usize = 0_usize;
        let mut bucketEnd: usize = 0_usize;
        let mut minUsed: usize = 0_usize;
        let mut maxUsed: usize = 0_usize;
        let mut localPeriodArray: Vec<i32> = Vec::new();
        let mut sortedIdx: Vec<i32> = Vec::new();
        let mut bucketOfs: Vec<i32> = Vec::new();
        let mut localOutputArray: Vec<f64> = Vec::new();
        let mut localFinalArray: Vec<f64> = Vec::new();
        let mut finalIsAllocated: usize = 0_usize;
        let mut localBegIdx: usize = 0_usize;
        let mut localNbElement: usize = 0_usize;
        let mut retCode: RetCode = RetCode::Success;
        // An inverted period window (min above max) is an invalid parameter
        // combination: the per-bar clamp below would push a period above
        // optInMaxPeriod, exceeding the lookback and reading uninitialized
        // results. Reject it cleanly instead of returning garbage.
        if optInMinPeriod > optInMaxPeriod {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::BadParam;
        }
        // Identify the minimum number of price bar needed
        // to calculate at least one output.
        lookbackTotal = self
            .ma_lookback(optInMaxPeriod, optInMAType)
            .unwrap_or(usize::MAX);
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
        // Calculate exact output size. A dedicated temp: tempInt is the cast-fed
        // period below, which the Rust backend types SIGNED (#160) — reusing it
        // here would drag this index arithmetic into i32.
        if lookbackTotal > startIdx {
            firstOut = lookbackTotal;
        } else {
            firstOut = startIdx;
        }
        if firstOut > endIdx {
            // No output
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        outputSize = endIdx - firstOut + 1;
        // Allocate intermediate local buffer.
        localOutputArray = vec![0.0_f64; (outputSize * 1) as usize];
        localPeriodArray = vec![0_i32; (outputSize * 1) as usize];
        // Output indices grouped by clamped period (counting sort below).
        sortedIdx = vec![0_i32; (outputSize * 1) as usize];
        // In-place defence (issue #130): each ma() pass below re-reads inReal over
        // the full range, so with outReal==inReal the results are staged in a
        // scratch buffer and copied once at the end. A regular call writes
        // straight to outReal and skips both the allocation and the copy.
        finalIsAllocated = 0;
        if outReal.as_ptr() == inReal.as_ptr() {
            finalIsAllocated = 1;
            localFinalArray = vec![0.0_f64; (outputSize * 1) as usize];
        } else {
            localFinalArray = outReal.to_vec();
        }
        // Read the caller array of period, truncate to min/max, and track the
        // range of periods actually used so all later work is sized by the data,
        // not by optInMaxPeriod. The floor at 1 (and on minUsed's start value)
        // keeps a period below 1 from indexing the occurrence tables out of range.
        // mavp.yaml caps both periods at [1, 100000], so it is inert through the
        // API; it is kept because this file is the source of truth for four
        // backends and it makes the shared source safe by construction rather than
        // by trusting each backend's prologue to be identical.
        minUsed = (optInMaxPeriod) as usize;
        if minUsed < 1 {
            minUsed = 1;
        }
        maxUsed = 1;
        // Both bounds widened once, outside the loop. In the C backend, left to the
        // compiler, only the first of the two is hoisted.
        minPeriodReal = ((optInMinPeriod) as f64);
        maxPeriodReal = ((optInMaxPeriod) as f64);
        // for( i = 0; i < outputSize; i += 1 )
        i = 0;
        while i < outputSize {
            // Clamp in the real domain, then narrow -- the order matters in the C
            // backend, and only there. C leaves an out-of-range narrowing undefined
            // and x86 lands EVERY such value on INT_MIN, so clamping afterwards pulls
            // a huge POSITIVE period down to the minimum. Java, C# and Rust saturate
            // to their maximum instead, so they were already right and this form
            // simply keeps them so.
            // `!(x >= min)` rather than `x < min`: both plain comparisons are false
            // for NaN, so only the inverted spelling catches it.
            tempPeriod = inPeriods[startIdx + i];
            if !(tempPeriod >= minPeriodReal) {
                tempInt = optInMinPeriod;
            } else if tempPeriod > maxPeriodReal {
                tempInt = optInMaxPeriod;
            } else {
                tempInt = (tempPeriod) as i32;
            }
            if tempInt < 1 {
                tempInt = 1;
            }
            localPeriodArray[i] = (tempInt) as i32;
            if tempInt < ((minUsed) as i32) {
                minUsed = (tempInt) as usize;
            }
            if tempInt > ((maxUsed) as i32) {
                maxUsed = (tempInt) as usize;
            }
            i += 1;
        }
        // Bound the bucket table before sizing it.
        //
        // Unreachable through the API: mavp.yaml caps both periods at 100000, so
        // the widest spread expressible is 99999. It is kept because it protects a
        // memory-safety property and this file is the source of truth for four
        // backends — without it the size expression below can overflow (signed
        // overflow in C, a wrapped negative in Java, a usize underflow panic in
        // Rust), and the four bodies would rest on each backend's prologue being
        // byte-for-byte equivalent, which nothing here states or checks. One
        // integer comparison per call is a cheap way not to depend on that.
        //
        // Written as a plain integer comparison on purpose — that is the only
        // construct that means the same thing in every backend. A (size_t) cast
        // would NOT help: this dialect's size_t parses to the generic index type
        // and renders back as int in both the C and the Java output (it is a
        // Rust-only annotation).
        //
        // If you delete this, delete the clamps and the comments together.
        if maxUsed < minUsed || maxUsed - minUsed > 100000 {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::BadParam;
        }
        // Per-period bucket cursor for the counting sort. Indexed RELATIVE to
        // minUsed: only [minUsed, maxUsed+1] is ever touched, so sizing from the
        // largest period used allocated up to 400KB for a band of periods that
        // may be a handful wide — and allocated it even on the single-period
        // fast path below.
        bucketOfs = vec![0_i32; ((maxUsed - minUsed + 2) * 1) as usize];
        if minUsed == maxUsed {
            // Single distinct period: one MA pass, written straight into the
            // destination buffer. Nothing to group or copy.
            let _xr0 = match self.ma(
                startIdx,
                endIdx,
                inReal,
                (minUsed) as i32,
                optInMAType,
                &mut localFinalArray[..],
            ) {
                Ok(_r) => _r,
                Err(_e) => return _e,
            };
            localBegIdx = _xr0.beg_idx;
            localNbElement = _xr0.count;
            retCode = RetCode::Success;
        } else {
            // Counting sort: sortedIdx ends up holding the output indices ordered
            // by period, one contiguous ascending slice per distinct period, with
            // bucketOfs[p] the end of period p's slice.
            for curPeriod in (minUsed as usize)..(maxUsed + 1 as usize) + 1 {
                bucketOfs[curPeriod - minUsed] = 0;
            }
            curPeriod = (maxUsed + 1 as usize) + 1;
            // for( i = 0; i < outputSize; i += 1 )
            i = 0;
            while i < outputSize {
                // Staged through tempInt, not indexed inline: the Rust backend only
                // coerces an int-array read to the index type when it is a DIRECT
                // operand, so bucketOfs[localPeriodArray[i]+1-minUsed] would mix
                // i32 with usize and fail to compile.
                tempInt = localPeriodArray[i];
                bucketOfs[(tempInt + 1 - ((minUsed) as i32)) as usize] =
                    (bucketOfs[(tempInt + 1 - ((minUsed) as i32)) as usize] + 1) as i32;
                i += 1;
            }
            for curPeriod in (minUsed as usize)..(maxUsed as usize) + 1 {
                bucketOfs[curPeriod + 1 - minUsed] =
                    (bucketOfs[curPeriod + 1 - minUsed] + bucketOfs[curPeriod - minUsed]) as i32;
            }
            curPeriod = (maxUsed as usize) + 1;
            // for( i = 0; i < outputSize; i += 1 )
            i = 0;
            while i < outputSize {
                tempInt = localPeriodArray[i];
                sortedIdx[(bucketOfs[(tempInt - ((minUsed) as i32)) as usize]) as usize] =
                    (i) as i32;
                bucketOfs[(tempInt - ((minUsed) as i32)) as usize] =
                    (bucketOfs[(tempInt - ((minUsed) as i32)) as usize] + 1) as i32;
                i += 1;
            }
            // One MA pass per period actually requested, ending at the last output
            // that uses it: outputs before that point cannot depend on later input
            // (every MA here fills forward), so the shorter range is bit-identical.
            // The pass must still START at startIdx: the window MAs (SMA, WMA,
            // TRIMA, HMA) slide a running accumulator seeded at startIdx-lookback,
            // so starting at the period's first use would change the rounding path
            // and break bit-identity, as would moving any recursive MA's warm-up.
            // The direct indexing of localOutputArray also relies on ma_lookback
            // being non-decreasing in the period, so the inner call never moves
            // its own start up. Both properties are pinned by the MAVP/GROUPING
            // regression test.
            bucketStart = 0;
            for curPeriod in (minUsed as usize)..(maxUsed as usize) + 1 {
                bucketEnd = (bucketOfs[curPeriod - minUsed]) as usize;
                if bucketEnd > bucketStart {
                    firstOccurrence = (sortedIdx[bucketStart]) as usize;
                    lastOccurrence = (sortedIdx[bucketEnd - 1]) as usize;
                    // Calculation of the MA required.
                    let _xr1 = match self.ma(
                        startIdx,
                        startIdx + lastOccurrence,
                        inReal,
                        (curPeriod) as i32,
                        optInMAType,
                        &mut localOutputArray[..],
                    ) {
                        Ok(_r) => _r,
                        Err(_e) => return _e,
                    };
                    localBegIdx = _xr1.beg_idx;
                    localNbElement = _xr1.count;
                    retCode = RetCode::Success;
                    if lastOccurrence - firstOccurrence == bucketEnd - 1 - bucketStart {
                        // The period's outputs form one contiguous run: block copy.
                        {
                            let _n = ((bucketEnd - bucketStart) * 1) as usize;
                            let _di = (firstOccurrence) as usize;
                            let _si = (firstOccurrence) as usize;
                            localFinalArray[_di.._di + _n]
                                .copy_from_slice(&localOutputArray[_si.._si + _n]);
                        };
                    } else {
                        // for( i = bucketStart; i < bucketEnd; i += 1 )
                        i = bucketStart;
                        while i < bucketEnd {
                            tempInt = sortedIdx[i];
                            localFinalArray[(tempInt) as usize] =
                                localOutputArray[(tempInt) as usize];
                            i += 1;
                        }
                    }
                }
                bucketStart = bucketEnd;
            }
            curPeriod = (maxUsed as usize) + 1;
        }
        // Pointer-inequality guard, not finalIsAllocated: in backends where the
        // scratch election materializes as a copy (Rust), the copy-back must
        // always run; in C/Java the non-aliased self-copy is skipped.
        if localFinalArray.as_ptr() != outReal.as_ptr() {
            {
                let _n = (outputSize * 1) as usize;
                let _di = (0) as usize;
                let _si = (0) as usize;
                outReal[_di.._di + _n].copy_from_slice(&localFinalArray[_si.._si + _n]);
            };
        }
        // Done. Inform the caller of the success.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outputSize;
        return RetCode::Success;
    }
    pub fn mavp(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        inPeriods: &[f64],
        optInMinPeriod: i32,
        optInMaxPeriod: i32,
        optInMAType: MAType,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.mavp_lookback(optInMinPeriod, optInMaxPeriod, optInMAType)?;
        let _guardStart = if startIdx > _guardLb {
            startIdx
        } else {
            _guardLb
        };
        if inReal.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        if inPeriods.len() < endIdx + 1 {
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
        let retCode = self.mavp_impl(
            startIdx,
            endIdx,
            inReal,
            inPeriods,
            optInMinPeriod,
            optInMaxPeriod,
            optInMAType,
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
