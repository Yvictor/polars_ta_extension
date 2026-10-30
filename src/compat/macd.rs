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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (macd).
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
    pub fn macd_lookback(
        &self,
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInSignalPeriod: i32,
    ) -> Result<usize, RetCode> {
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 12;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 1) || (((optInSignalPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        let mut tempInteger: usize = 0_usize;
        // The lookback is driven by the signal line output.
        //
        // (must also account for the initial data consume
        //  by the slow period).
        // Make sure slow is really slower than
        // the fast period! if not, swap...
        if optInSlowPeriod < optInFastPeriod {
            // swap
            tempInteger = (optInSlowPeriod) as usize;
            optInSlowPeriod = optInFastPeriod;
            optInFastPeriod = (tempInteger) as i32;
        }
        return Ok(
            (self.ema_lookback(optInSlowPeriod)? + self.ema_lookback(optInSignalPeriod)?) as usize,
        );
    }
    fn macd_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInFastPeriod: i32,
        mut optInSlowPeriod: i32,
        mut optInSignalPeriod: i32,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outMACD: &mut [f64],
        outMACDSignal: &mut [f64],
        outMACDHist: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 12;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 1) || (((optInSignalPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        let _assertLb = self
            .macd_lookback(optInFastPeriod, optInSlowPeriod, optInSignalPeriod)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outMACD.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outMACDSignal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outMACDHist.len());
        if (!outMACD.is_empty()
            && !outMACDSignal.is_empty()
            && outMACD.as_ptr() == outMACDSignal.as_ptr())
            || (!outMACD.is_empty()
                && !outMACDHist.is_empty()
                && outMACD.as_ptr() == outMACDHist.as_ptr())
            || (!outMACDSignal.is_empty()
                && !outMACDHist.is_empty()
                && outMACDSignal.as_ptr() == outMACDHist.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut prevFast: f64 = 0.0_f64;
        let mut prevSlow: f64 = 0.0_f64;
        let mut prevSignal: f64 = 0.0_f64;
        let mut macdValue: f64 = 0.0_f64;
        let mut tempReal: f64 = 0.0_f64;
        let mut slowK: f64 = 0.0_f64;
        let mut fastK: f64 = 0.0_f64;
        let mut signalK: f64 = 0.0_f64;
        let mut i: usize = 0_usize;
        let mut today: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut tempInteger: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackSignal: usize = 0_usize;
        // Make sure slow is really slower than
        // the fast period! if not, swap...
        if optInSlowPeriod < optInFastPeriod {
            // swap
            tempInteger = (optInSlowPeriod) as usize;
            optInSlowPeriod = optInFastPeriod;
            optInFastPeriod = (tempInteger) as i32;
        }
        // Catch special case for fix 26/12 MACD.
        // Use hardcoded k values matching the original algorithm.
        if optInSlowPeriod == 0 {
            // Fix 26
            optInSlowPeriod = 26;
            slowK = 0.075;
        } else {
            slowK = 2.0 / ((optInSlowPeriod + 1) as f64);
        }
        if optInFastPeriod == 0 {
            // Fix 12
            optInFastPeriod = 12;
            fastK = 0.15;
        } else {
            fastK = 2.0 / ((optInFastPeriod + 1) as f64);
        }
        // A signal period of 1 disables signal-line smoothing: the signal IS the
        // MACD line and the histogram is exactly zero. signalK is then exactly
        // 1.0, so the recursion below reduces to (x-prev)+prev -- which returns x
        // only while consecutive MACD-line values stay within a factor of two of
        // each other. The MACD line oscillates through zero, so it leaves that
        // window on ordinary data; hence the explicit arm at each step.
        signalK = 2.0 / ((optInSignalPeriod + 1) as f64);
        lookbackSignal = self.ema_lookback(optInSignalPeriod).unwrap_or(usize::MAX);
        // Move up the start index if there is not
        // enough initial data.
        lookbackTotal = lookbackSignal;
        lookbackTotal += self.ema_lookback(optInSlowPeriod).unwrap_or(usize::MAX);
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // Everything is computed in a single lockstep pass: each bar
        // advances the fast and slow EMA (two independent recursions),
        // their difference is the MACD line, and each MACD-line value
        // is immediately fed into the signal EMA. No temporary buffers.
        //
        // The arithmetic order below is the bit-exactness contract
        // (do not reorder or fuse operations):
        //  - EMA recursion: ((x-prev)*k)+prev.
        //  - Each EMA is seeded with the sum of its first 'period'
        //    inputs, accumulated from 0.0 in input order, divided by
        //    the period. The fast and slow seed windows end on the
        //    same bar. The signal EMA is seeded the same way from the
        //    first 'signal period' MACD-line values.
        //
        // In-place (an output == inReal) is supported: outputs at
        // [outIdx] are written only after inReal[startIdx+outIdx] was
        // read.
        // Seed each price EMA with a simple average of its first
        // 'period' price bars. The fast window is the tail of the
        // slow window: consume the leading slow-only bars first,
        // then accumulate both over the shared bars.
        today = startIdx - lookbackTotal;
        tempReal = 0.0;
        i = (optInSlowPeriod - optInFastPeriod) as usize;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            tempReal += inReal[{
                let _v = today;
                today += 1;
                _v
            }];
        }
        prevFast = 0.0;
        i = (optInFastPeriod) as usize;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            prevFast += inReal[today];
            tempReal += inReal[{
                let _v = today;
                today += 1;
                _v
            }];
        }
        prevSlow = tempReal / ((optInSlowPeriod) as f64);
        prevFast = prevFast / ((optInFastPeriod) as f64);
        // Advance both EMA through their unstable period, up to the
        // first MACD-line bar.
        while today <= startIdx - lookbackSignal {
            tempReal = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            prevFast = (tempReal - prevFast as f64).mul_add(fastK, prevFast);
            prevSlow = (tempReal - prevSlow as f64).mul_add(slowK, prevSlow);
        }
        macdValue = prevFast - prevSlow;
        // Seed the signal EMA with a simple average of the first
        // 'signal period' MACD-line values, accumulated as they are
        // produced.
        prevSignal = 0.0;
        prevSignal += macdValue;
        i = (optInSignalPeriod - 1) as usize;
        while {
            let _v = i;
            i = i.wrapping_sub(1);
            _v
        } > 0
        {
            tempReal = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            prevFast = (tempReal - prevFast as f64).mul_add(fastK, prevFast);
            prevSlow = (tempReal - prevSlow as f64).mul_add(slowK, prevSlow);
            macdValue = prevFast - prevSlow;
            prevSignal += macdValue;
        }
        prevSignal = prevSignal / ((optInSignalPeriod) as f64);
        // Advance everything in lockstep through the unstable period
        // of the signal EMA, up to the first output bar.
        while today <= startIdx {
            tempReal = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            prevFast = (tempReal - prevFast as f64).mul_add(fastK, prevFast);
            prevSlow = (tempReal - prevSlow as f64).mul_add(slowK, prevSlow);
            macdValue = prevFast - prevSlow;
            if optInSignalPeriod == 1 {
                prevSignal = macdValue;
            } else {
                prevSignal = (macdValue - prevSignal as f64).mul_add(signalK, prevSignal);
            }
        }
        // Stable zone: keep advancing in lockstep and write the three
        // outputs.
        outMACD[0] = macdValue;
        outMACDSignal[0] = prevSignal;
        outMACDHist[0] = macdValue - prevSignal;
        outIdx = 1;
        while today <= endIdx {
            tempReal = inReal[{
                let _v = today;
                today += 1;
                _v
            }];
            prevFast = (tempReal - prevFast as f64).mul_add(fastK, prevFast);
            prevSlow = (tempReal - prevSlow as f64).mul_add(slowK, prevSlow);
            macdValue = prevFast - prevSlow;
            if optInSignalPeriod == 1 {
                prevSignal = macdValue;
            } else {
                prevSignal = (macdValue - prevSignal as f64).mul_add(signalK, prevSignal);
            }
            outMACD[outIdx] = macdValue;
            outMACDSignal[outIdx] = prevSignal;
            outMACDHist[outIdx] = macdValue - prevSignal;
            outIdx += 1;
        }
        // All done! Indicate the output limits and return success.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outIdx;
        return RetCode::Success;
    }
    pub fn macd(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInFastPeriod: i32,
        optInSlowPeriod: i32,
        optInSignalPeriod: i32,
        outMACD: &mut [f64],
        outMACDSignal: &mut [f64],
        outMACDHist: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.macd_lookback(optInFastPeriod, optInSlowPeriod, optInSignalPeriod)?;
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
        if outMACD.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outMACDSignal.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outMACDHist.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.macd_impl(
            startIdx,
            endIdx,
            inReal,
            optInFastPeriod,
            optInSlowPeriod,
            optInSignalPeriod,
            &mut outBegIdx,
            &mut outNBElement,
            outMACD,
            outMACDSignal,
            outMACDHist,
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
