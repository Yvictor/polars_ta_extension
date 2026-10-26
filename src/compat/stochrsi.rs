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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (stochrsi).
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
    pub fn stochrsi_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInFastK_Period: i32,
        mut optInFastD_Period: i32,
        mut optInFastD_MAType: MAType,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 14;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInFastK_Period) as i32) == (i32::MIN) {
            optInFastK_Period = 5;
        } else if (((optInFastK_Period) as i32) < 1) || (((optInFastK_Period) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if ((optInFastD_Period) as i32) == (i32::MIN) {
            optInFastD_Period = 3;
        } else if (((optInFastD_Period) as i32) < 1) || (((optInFastD_Period) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInFastD_MAType == MAType::DEFAULT {
            optInFastD_MAType = MAType::SMA;
        }
        let mut retValue: usize = 0_usize;
        retValue = self.rsi_lookback(optInTimePeriod)?
            + self.stochf_lookback(optInFastK_Period, optInFastD_Period, optInFastD_MAType)?;
        return Ok(retValue);
    }
    pub(crate) fn stochrsi_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
        mut optInFastK_Period: i32,
        mut optInFastD_Period: i32,
        mut optInFastD_MAType: MAType,
        outBegIdx: &mut usize,
        outNBElement: &mut usize,
        outFastK: &mut [f64],
        outFastD: &mut [f64],
    ) -> RetCode {
        if startIdx > Core::INDEX_MAX {
            return RetCode::OutOfRangeStartIndex;
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return RetCode::OutOfRangeEndIndex;
        }
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 14;
        } else if (((optInTimePeriod) as i32) < 2) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInFastK_Period) as i32) == (i32::MIN) {
            optInFastK_Period = 5;
        } else if (((optInFastK_Period) as i32) < 1) || (((optInFastK_Period) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if ((optInFastD_Period) as i32) == (i32::MIN) {
            optInFastD_Period = 3;
        } else if (((optInFastD_Period) as i32) < 1) || (((optInFastD_Period) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInFastD_MAType == MAType::DEFAULT {
            optInFastD_MAType = MAType::SMA;
        }
        let _assertLb = self
            .stochrsi_lookback(
                optInTimePeriod,
                optInFastK_Period,
                optInFastD_Period,
                optInFastD_MAType,
            )
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outFastK.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outFastD.len());
        if (!outFastK.is_empty() && !outFastD.is_empty() && outFastK.as_ptr() == outFastD.as_ptr())
        {
            return RetCode::BadParam;
        }
        let mut startIdx = startIdx;
        let mut tempRSIBuffer: Vec<f64> = Vec::new();
        let mut retCode: RetCode = RetCode::Success;
        let mut lookbackTotal: usize = 0_usize;
        let mut lookbackSTOCHF: usize = 0_usize;
        let mut tempArraySize: usize = 0_usize;
        let mut outBegIdx1: usize = 0_usize;
        let mut outBegIdx2: usize = 0_usize;
        let mut outNbElement1: usize = 0_usize;
        // Stochastic RSI
        //
        // Reference: "Stochastic RSI and Dynamic Momentum Index"
        //            by Tushar Chande and Stanley Kroll
        //            Stock&Commodities V.11:5 (189-199)
        //
        // The TA-Lib version offer flexibility beyond what is explain
        // in the Stock&Commodities article.
        //
        // To calculate the "Unsmoothed stochastic RSI" with symetry like
        // explain in the article, keep the optInTimePeriod and optInFastK_Period
        // equal. Example:
        //
        //    unsmoothed stoch RSI 14 : optInTimePeriod   = 14
        //                              optInFastK_Period = 14
        //                              optInFastD_Period = 'x'
        //
        // The outFastK is the unsmoothed RSI discuss in the article.
        //
        // You can set the optInFastD_Period to smooth the RSI. The smooth
        // version will be found in outFastD. The outFastK will still contain
        // the unsmoothed stoch RSI. If you do not care about the smoothing of
        // the StochRSI, just leave optInFastD_Period to 1 and ignore outFastD.
        (*outBegIdx) = 0;
        (*outNBElement) = 0;
        // Adjust startIdx to account for the lookback period.
        lookbackSTOCHF = self
            .stochf_lookback(optInFastK_Period, optInFastD_Period, optInFastD_MAType)
            .unwrap_or(usize::MAX);
        lookbackTotal = self.rsi_lookback(optInTimePeriod).unwrap_or(usize::MAX) + lookbackSTOCHF;
        if startIdx < lookbackTotal {
            startIdx = lookbackTotal;
        }
        // Make sure there is still something to evaluate.
        if startIdx > endIdx {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        (*outBegIdx) = startIdx;
        tempArraySize = endIdx - startIdx + 1 + lookbackSTOCHF;
        tempRSIBuffer = vec![0.0_f64; (tempArraySize * 1) as usize];
        let _xr0 = match self.rsi(
            startIdx - lookbackSTOCHF,
            endIdx,
            inReal,
            optInTimePeriod,
            &mut tempRSIBuffer[..],
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        outBegIdx1 = _xr0.beg_idx;
        outNbElement1 = _xr0.count;
        retCode = RetCode::Success;
        if outNbElement1 == 0 {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return retCode;
        }
        let _xr1 = match self.stochf(
            0,
            tempArraySize - 1,
            &tempRSIBuffer,
            &tempRSIBuffer,
            &tempRSIBuffer,
            optInFastK_Period,
            optInFastD_Period,
            optInFastD_MAType,
            outFastK,
            outFastD,
        ) {
            Ok(_r) => _r,
            Err(_e) => return _e,
        };
        outBegIdx2 = _xr1.beg_idx;
        (*outNBElement) = _xr1.count;
        retCode = RetCode::Success;
        if ((*outNBElement) as usize) == 0 {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return retCode;
        }
        return RetCode::Success;
    }
    pub fn stochrsi(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInFastK_Period: i32,
        optInFastD_Period: i32,
        optInFastD_MAType: MAType,
        outFastK: &mut [f64],
        outFastD: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.stochrsi_lookback(
            optInTimePeriod,
            optInFastK_Period,
            optInFastD_Period,
            optInFastD_MAType,
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
        if outFastK.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        if outFastD.len() < _guardOutLen {
            return Err(RetCode::BadParam);
        }
        let mut outBegIdx: usize = 0;
        let mut outNBElement: usize = 0;
        let retCode = self.stochrsi_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
            optInFastK_Period,
            optInFastD_Period,
            optInFastD_MAType,
            &mut outBegIdx,
            &mut outNBElement,
            outFastK,
            outFastD,
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
