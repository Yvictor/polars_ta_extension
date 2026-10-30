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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (efi).
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
    pub fn efi_lookback(&self, mut optInTimePeriod: i32) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        // One bar is consumed forming the first close-to-close change, then the
        // EMA's own warm-up on top:
        //    1 + ema_lookback(optInTimePeriod)
        //  = 1 + (optInTimePeriod - 1) + TA_GetUnstablePeriod(TA_FUNC_UNST_EMA)
        return Ok((optInTimePeriod + 0) as usize);
    }
    fn efi_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inClose: &[f64],
        inVolume: &[f64],
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
            optInTimePeriod = 13;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self.efi_lookback(optInTimePeriod).unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inClose.len());
        assert!(_assertStart > endIdx || endIdx < inVolume.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut optInK_1: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut prevMA: f64 = 0.0_f64;
        let mut prevClose: f64 = 0.0_f64;
        let mut force: f64 = 0.0_f64;
        let mut i: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        optInK_1 = 2.0 / ((optInTimePeriod + 1) as f64);
        // Alexander Elder's Force Index (Trading for a Living, 1993): the one-bar
        // close-to-close move weighted by that bar's volume, then smoothed with an
        // EMA. Elder's 2-period reading is the short-term form and 13 the
        // intermediate-term one -- that is the parameter, not a second formula.
        //
        //    force[t] = ( close[t] - close[t-1] ) * volume[t]
        //    EFI      = EMA( force, optInTimePeriod )
        //
        // The arithmetic below is ema.c's with inReal[t] replaced by force[t], kept
        // in exactly that shape on purpose: the seed accumulates from 0.0 in the
        // same order, and the recurrence is (x - prevMA)*k + prevMA rather than the
        // algebraically equal k*x + (1-k)*prevMA. That order IS the bit-exactness
        // contract against the composed reference in test_composite.c -- MOM, then
        // MULT, then EMA -- so do not tidy it. TRIX carries the same warning.
        //
        // Nothing on the data path divides by an input, so issue #112 is satisfied
        // structurally: a flat close gives force exactly 0.0 and output exactly
        // 0.0, and zero volume likewise. The only division is by the period, a
        // positive integer parameter.
        //
        // prevClose is carried in a scalar rather than re-read from inClose[t-1]
        // because the C API allows outReal to alias an input: at bar t the slot
        // holding close[t-1] may already have been overwritten by the output
        // written a bar earlier. cmou.c carries its trailing value for the same
        // reason.
        // Identify the minimum number of price bar needed
        // to calculate at least one output.
        lookbackTotal = self.efi_lookback(optInTimePeriod).unwrap_or(usize::MAX);
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
        // No smoothing at a period of 1: the output is the raw Force Index.
        // Explicit for the reason spelled out in ema.c -- at period 1 optInK_1 is
        // exactly 1.0, so the recursion reduces to (x-prev)+prev, which returns x
        // only while consecutive values stay within a factor of two of each other.
        // Force values swing by orders of magnitude, far more than the prices EMA
        // warns about.
        if optInTimePeriod == 1 {
            (*outBegIdx) = startIdx;
            outIdx = 0;
            today = startIdx;
            prevClose = inClose[today - 1];
            while today <= endIdx {
                force = (inClose[today] - prevClose) * inVolume[today];
                prevClose = inClose[today];
                outReal[outIdx] = force;
                outIdx = outIdx + 1;
                today = today + 1;
            }
            (*outNBElement) = outIdx;
            return RetCode::Success;
        }
        (*outBegIdx) = startIdx;
        // The first EMA value is a simple average of the first 'period' force
        // values; it then seeds the recursion. This is ema.c's seeding applied
        // to the force series rather than to the input array.
        today = startIdx - lookbackTotal + 1;
        prevClose = inClose[today - 1];
        i = (optInTimePeriod) as usize;
        tempReal = 0.0;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            force = (inClose[today] - prevClose) * inVolume[today];
            prevClose = inClose[today];
            tempReal += force;
            today = today + 1;
        }
        prevMA = tempReal / ((optInTimePeriod) as f64);
        while today <= startIdx {
            force = (inClose[today] - prevClose) * inVolume[today];
            prevClose = inClose[today];
            prevMA = (force - prevMA as f64).mul_add(optInK_1, prevMA);
            today = today + 1;
        }
        outReal[0] = prevMA;
        outIdx = 1;
        while today <= endIdx {
            force = (inClose[today] - prevClose) * inVolume[today];
            prevClose = inClose[today];
            prevMA = (force - prevMA as f64).mul_add(optInK_1, prevMA);
            outReal[outIdx] = prevMA;
            outIdx = outIdx + 1;
            today = today + 1;
        }
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn efi(
        &self,
        startIdx: usize,
        endIdx: usize,
        inClose: &[f64],
        inVolume: &[f64],
        optInTimePeriod: i32,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.efi_lookback(optInTimePeriod)?;
        let _guardStart = if startIdx > _guardLb {
            startIdx
        } else {
            _guardLb
        };
        if inClose.len() < endIdx + 1 {
            return Err(RetCode::BadParam);
        }
        if inVolume.len() < endIdx + 1 {
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
        let retCode = self.efi_impl(
            startIdx,
            endIdx,
            inClose,
            inVolume,
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
