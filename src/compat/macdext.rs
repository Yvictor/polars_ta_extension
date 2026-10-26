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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (macdext).
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
    pub fn macdext_lookback(
        &self,
        mut optInFastPeriod: i32,
        mut optInFastMAType: MAType,
        mut optInSlowPeriod: i32,
        mut optInSlowMAType: MAType,
        mut optInSignalPeriod: i32,
        mut optInSignalMAType: MAType,
    ) -> Result<usize, RetCode> {
        if ((optInFastPeriod) as i32) == (i32::MIN) {
            optInFastPeriod = 12;
        } else if (((optInFastPeriod) as i32) < 2) || (((optInFastPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInFastMAType == MAType::DEFAULT {
            optInFastMAType = MAType::SMA;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInSlowMAType == MAType::DEFAULT {
            optInSlowMAType = MAType::SMA;
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 1) || (((optInSignalPeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInSignalMAType == MAType::DEFAULT {
            optInSignalMAType = MAType::SMA;
        }
        let mut tempInteger: usize = 0_usize;
        let mut lookbackLargest: usize = 0_usize;
        // Find the MA with the largest lookback
        lookbackLargest = self.ma_lookback(optInFastPeriod, optInFastMAType)?;
        tempInteger = self.ma_lookback(optInSlowPeriod, optInSlowMAType)?;
        if tempInteger > lookbackLargest {
            lookbackLargest = tempInteger;
        }
        // Add to the largest MA lookback the signal line lookback
        return Ok(
            (lookbackLargest + self.ma_lookback(optInSignalPeriod, optInSignalMAType)?) as usize,
        );
    }
    pub(crate) fn macdext_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInFastPeriod: i32,
        mut optInFastMAType: MAType,
        mut optInSlowPeriod: i32,
        mut optInSlowMAType: MAType,
        mut optInSignalPeriod: i32,
        mut optInSignalMAType: MAType,
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
        if optInFastMAType == MAType::DEFAULT {
            optInFastMAType = MAType::SMA;
        }
        if ((optInSlowPeriod) as i32) == (i32::MIN) {
            optInSlowPeriod = 26;
        } else if (((optInSlowPeriod) as i32) < 2) || (((optInSlowPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInSlowMAType == MAType::DEFAULT {
            optInSlowMAType = MAType::SMA;
        }
        if ((optInSignalPeriod) as i32) == (i32::MIN) {
            optInSignalPeriod = 9;
        } else if (((optInSignalPeriod) as i32) < 1) || (((optInSignalPeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInSignalMAType == MAType::DEFAULT {
            optInSignalMAType = MAType::SMA;
        }
        let _assertLb = self
            .macdext_lookback(
                optInFastPeriod,
                optInFastMAType,
                optInSlowPeriod,
                optInSlowMAType,
                optInSignalPeriod,
                optInSignalMAType,
            )
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
        let mut slowMABuffer: Vec<f64> = Vec::new();
        let mut fastMABuffer: Vec<f64> = Vec::new();
        let mut retCode: RetCode = RetCode::Success;
        let mut tempInteger: usize = 0_usize;
        let mut outBegIdx1: usize = 0_usize;
        let mut outNbElement1: usize = 0_usize;
        let mut outBegIdx2: usize = 0_usize;
        let mut outNbElement2: usize = 0_usize;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackSignal: usize = 0_usize;
        let mut lookbackLargest: usize = 0_usize;
        let mut i: usize = 0_usize;
        let mut tempMAType: MAType;
        if optInFastMAType == MAType::EMA
            && optInSlowMAType == MAType::EMA
            && optInSignalMAType == MAType::EMA
            && optInFastPeriod >= 2
            && optInSlowPeriod >= 2
            && optInSignalPeriod >= 2
        {
            // An all-EMA MACDEXT computes exactly what MACD computes. Delegate
            // to its single-pass implementation. Period 1 stays on the generic
            // path: ma() copies the input for it instead of running an EMA
            // recursion.
            //
            // This block is a batch-only specialization: the generator strips it
            // from the streaming tier, which composes the general three-MA path for
            // every parameter value. The two agreeing bit for bit is not assumed --
            // stream_verify's multi-enum diagonal selects all-EMA and holds this
            // block to the composed path (issue #181). Keep the comment INSIDE the
            // block: above it, the stream inherits it and reads as if it delegated.
            let _xr0 = match self.macd(
                startIdx,
                endIdx,
                inReal,
                optInFastPeriod,
                optInSlowPeriod,
                optInSignalPeriod,
                outMACD,
                outMACDSignal,
                outMACDHist,
            ) {
                Ok(_r) => _r,
                Err(_e) => return _e,
            };
            (*outBegIdx) = _xr0.beg_idx;
            (*outNBElement) = _xr0.count;
            return RetCode::Success;
        }
        // Make sure slow is really slower than
        // the fast period! if not, swap...
        if optInSlowPeriod < optInFastPeriod {
            // swap period
            tempInteger = (optInSlowPeriod) as usize;
            optInSlowPeriod = optInFastPeriod;
            optInFastPeriod = (tempInteger) as i32;
            // swap type
            tempMAType = optInSlowMAType;
            optInSlowMAType = optInFastMAType;
            optInFastMAType = tempMAType;
        }
        // Find the MA with the largest lookback
        lookbackLargest = self
            .ma_lookback(optInFastPeriod, optInFastMAType)
            .unwrap_or(usize::MAX);
        tempInteger = self
            .ma_lookback(optInSlowPeriod, optInSlowMAType)
            .unwrap_or(usize::MAX);
        if tempInteger > lookbackLargest {
            lookbackLargest = tempInteger;
        }
        // Add the lookback needed for the signal line
        lookbackSignal = self
            .ma_lookback(optInSignalPeriod, optInSignalMAType)
            .unwrap_or(usize::MAX);
        lookbackTotal = lookbackSignal + lookbackLargest;
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
        // Allocate intermediate buffer for fast/slow MA.
        tempInteger = endIdx - startIdx + 1 + lookbackSignal;
        fastMABuffer = vec![0.0_f64; (tempInteger * 1) as usize];
        slowMABuffer = vec![0.0_f64; (tempInteger * 1) as usize];
        // Calculate the slow MA.
        //
        // Move back the startIdx to get enough data
        // for the signal period. That way, once the
        // signal calculation is done, all the output
        // will start at the requested 'startIdx'.
        tempInteger = startIdx - lookbackSignal;
        let _xr1 = match self.ma(
            tempInteger,
            endIdx,
            inReal,
            optInSlowPeriod,
            optInSlowMAType,
            &mut slowMABuffer[..],
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        outBegIdx1 = _xr1.beg_idx;
        outNbElement1 = _xr1.count;
        retCode = RetCode::Success;
        // Calculate the fast MA.
        let _xr2 = match self.ma(
            tempInteger,
            endIdx,
            inReal,
            optInFastPeriod,
            optInFastMAType,
            &mut fastMABuffer[..],
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        outBegIdx2 = _xr2.beg_idx;
        outNbElement2 = _xr2.count;
        retCode = RetCode::Success;
        // Parano tests. Will be removed eventually.
        if outBegIdx1 != tempInteger
            || outBegIdx2 != tempInteger
            || outNbElement1 != outNbElement2
            || outNbElement1 != endIdx - startIdx + 1 + lookbackSignal
        {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::BadParam;
        }
        // Calculate (fast MA) - (slow MA).
        // for( i = 0; i < outNbElement1; i += 1 )
        i = 0;
        while i < outNbElement1 {
            fastMABuffer[i] = fastMABuffer[i] - slowMABuffer[i];
            i += 1;
        }
        // Copy the result into the output for the caller.
        // memmove, not memcpy: fastMABuffer aliases outMACD when the caller buffer is
        // reused as scratch, so source and destination overlap (issue #94).
        {
            let _n = ((endIdx - startIdx + 1) * 1) as usize;
            let _di = (0) as usize;
            let _si = (lookbackSignal) as usize;
            outMACD[_di.._di + _n].copy_from_slice(&fastMABuffer[_si.._si + _n]);
        };
        // Calculate the signal/trigger line.
        let _xr3 = match self.ma(
            0,
            outNbElement1 - 1,
            &fastMABuffer,
            optInSignalPeriod,
            optInSignalMAType,
            outMACDSignal,
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        outBegIdx2 = _xr3.beg_idx;
        outNbElement2 = _xr3.count;
        retCode = RetCode::Success;
        // Calculate the histogram.
        // for( i = 0; i < outNbElement2; i += 1 )
        i = 0;
        while i < outNbElement2 {
            outMACDHist[i] = ((outMACD[i] - outMACDSignal[i]) as f64);
            i += 1;
        }
        // All done! Indicate the output limits and return success.
        (*outBegIdx) = startIdx;
        (*outNBElement) = outNbElement2;
        return RetCode::Success;
    }
    pub fn macdext(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInFastPeriod: i32,
        optInFastMAType: MAType,
        optInSlowPeriod: i32,
        optInSlowMAType: MAType,
        optInSignalPeriod: i32,
        optInSignalMAType: MAType,
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
        let _guardLb = self.macdext_lookback(
            optInFastPeriod,
            optInFastMAType,
            optInSlowPeriod,
            optInSlowMAType,
            optInSignalPeriod,
            optInSignalMAType,
        )?;
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
        let retCode = self.macdext_impl(
            startIdx,
            endIdx,
            inReal,
            optInFastPeriod,
            optInFastMAType,
            optInSlowPeriod,
            optInSlowMAType,
            optInSignalPeriod,
            optInSignalMAType,
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
