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

// Adapted batch-only compatibility kernel from TA-Lib v0.8.1 (ma).
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
    pub fn ma_lookback(
        &self,
        mut optInTimePeriod: i32,
        mut optInMAType: MAType,
    ) -> Result<usize, RetCode> {
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return Err(RetCode::BadParam);
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::SMA;
        }
        let mut retValue: usize = 0_usize;
        if optInTimePeriod <= 1 || optInMAType == MAType::DISABLED {
            return Ok((0) as usize);
        }
        match optInMAType {
            MAType::SMA => {
                retValue = self.sma_lookback(optInTimePeriod)?;
            }
            MAType::EMA => {
                retValue = self.ema_lookback(optInTimePeriod)?;
            }
            MAType::WMA => {
                retValue = self.wma_lookback(optInTimePeriod)?;
            }
            MAType::DEMA => {
                retValue = self.dema_lookback(optInTimePeriod)?;
            }
            MAType::TEMA => {
                retValue = self.tema_lookback(optInTimePeriod)?;
            }
            MAType::TRIMA => {
                retValue = self.trima_lookback(optInTimePeriod)?;
            }
            MAType::KAMA => {
                retValue = self.kama_lookback(optInTimePeriod)?;
            }
            MAType::MAMA => {
                retValue = self.mama_lookback(0.5, 0.05)?;
            }
            MAType::T3 => {
                retValue = self.t3_lookback(optInTimePeriod, 0.7)?;
            }
            MAType::HMA => {
                retValue = self.hma_lookback(optInTimePeriod)?;
            }
            MAType::ZLEMA => {
                retValue = self.zlema_lookback(optInTimePeriod)?;
            }
            MAType::RMA => {
                retValue = self.rma_lookback(optInTimePeriod)?;
            }
            _ => {
                retValue = 0;
            }
        }
        return Ok(retValue);
    }
    pub(crate) fn ma_impl(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        mut optInTimePeriod: i32,
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
        if ((optInTimePeriod) as i32) == (i32::MIN) {
            optInTimePeriod = 30;
        } else if (((optInTimePeriod) as i32) < 1) || (((optInTimePeriod) as i32) > 100000) {
            return RetCode::BadParam;
        }
        if optInMAType == MAType::DEFAULT {
            optInMAType = MAType::SMA;
        }
        let _assertLb = self
            .ma_lookback(optInTimePeriod, optInMAType)
            .unwrap_or(usize::MAX);
        let _assertStart = if startIdx > _assertLb {
            startIdx
        } else {
            _assertLb
        };
        assert!(_assertStart > endIdx || endIdx < inReal.len());
        assert!(_assertStart > endIdx || endIdx - _assertStart < outReal.len());
        let mut startIdx = startIdx;
        let mut retCode: RetCode = RetCode::Success;
        let mut nbElement: usize = 0_usize;
        let mut outIdx: usize = 0_usize;
        let mut todayIdx: usize = 0_usize;
        // Nothing to produce: the range is shorter than the lookback. Answer here
        // rather than forwarding.
        //
        // The VALUE is the same either way: ma_lookback returns exactly the lookback
        // the arm's callee computes for itself, from the same arguments the arm
        // passes it, and every callee clamps startIdx to that lookback and yields
        // 0,0 without reading. What changes is whose frame answers, and that is
        // visible to one caller only - the zero-length no-I/O probe. It hands the
        // body empty arrays on this range to check that nothing is read; forwarding
        // makes the callee's PUBLIC input bound (endIdx + 1 elements, no
        // sub-lookback escape) answer TA_BAD_PARAM before any array is reached, so
        // the probe cannot tell "read nothing" from "never ran". ma was the last
        // core withheld from that sweep for exactly this reason; apo, bbands, ppo,
        // pvo and stddev already carried this guard. No legitimate caller is
        // affected: ma's own public tier already requires endIdx + 1 input elements,
        // and on this range the callee's OUTPUT bound is 0, so a caller sizing by
        // the published formula was never rejected by it.
        //
        // It cannot mask a TA_BAD_PARAM. An optInMAType outside the enum is refused
        // by the generated entry point above this guard. An in-range member with no
        // arm here would reach ma_lookback's own default and get 0, and 0 > endIdx
        // is false for every endIdx the entry point admits, so control still reaches
        // the switch and still answers TA_BAD_PARAM. The identity path below is out
        // of the guard's reach for the same reason - its lookback is 0.
        if self
            .ma_lookback(optInTimePeriod, optInMAType)
            .unwrap_or(usize::MAX)
            > endIdx
        {
            (*outBegIdx) = 0;
            (*outNBElement) = 0;
            return RetCode::Success;
        }
        // No-smoothing identity: period 1 (every MA type) or the explicit
        // TA_MAType_DISABLED (any period, issue #93). One copy path, lookback 0.
        if optInTimePeriod == 1 || optInMAType == MAType::DISABLED {
            nbElement = endIdx - startIdx + 1;
            (*outNBElement) = nbElement;
            // for( todayIdx = startIdx, outIdx = 0; outIdx < nbElement; outIdx += 1, todayIdx += 1 )
            todayIdx = startIdx;
            outIdx = 0;
            while outIdx < nbElement {
                outReal[outIdx] = ((inReal[todayIdx]) as f64);
                outIdx += 1;
                todayIdx += 1;
            }
            (*outBegIdx) = startIdx;
            return RetCode::Success;
        }
        // Simply forward the job to the corresponding TA function.
        match optInMAType {
            MAType::SMA => {
                let _xr0 = match self.sma(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr0.beg_idx;
                (*outNBElement) = _xr0.count;
                retCode = RetCode::Success;
            }
            MAType::EMA => {
                let _xr1 = match self.ema(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr1.beg_idx;
                (*outNBElement) = _xr1.count;
                retCode = RetCode::Success;
            }
            MAType::WMA => {
                let _xr2 = match self.wma(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr2.beg_idx;
                (*outNBElement) = _xr2.count;
                retCode = RetCode::Success;
            }
            MAType::DEMA => {
                let _xr3 = match self.dema(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr3.beg_idx;
                (*outNBElement) = _xr3.count;
                retCode = RetCode::Success;
            }
            MAType::TEMA => {
                let _xr4 = match self.tema(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr4.beg_idx;
                (*outNBElement) = _xr4.count;
                retCode = RetCode::Success;
            }
            MAType::TRIMA => {
                let _xr5 = match self.trima(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr5.beg_idx;
                (*outNBElement) = _xr5.count;
                retCode = RetCode::Success;
            }
            MAType::KAMA => {
                let _xr6 = match self.kama(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr6.beg_idx;
                (*outNBElement) = _xr6.count;
                retCode = RetCode::Success;
            }
            MAType::MAMA => {
                // The optInTimePeriod is ignored. FAMA is a nullable output
                // (issue #125): pass NULL to compute only the MAMA line into outReal.
                let _xr7 = match self.mama(
                    startIdx,
                    endIdx,
                    inReal,
                    0.5,
                    0.05,
                    outReal,
                    &mut vec![0.; endIdx + 1],
                ) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr7.beg_idx;
                (*outNBElement) = _xr7.count;
                retCode = RetCode::Success;
            }
            MAType::T3 => {
                let _xr8 = match self.t3(startIdx, endIdx, inReal, optInTimePeriod, 0.7, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr8.beg_idx;
                (*outNBElement) = _xr8.count;
                retCode = RetCode::Success;
            }
            MAType::HMA => {
                let _xr9 = match self.hma(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr9.beg_idx;
                (*outNBElement) = _xr9.count;
                retCode = RetCode::Success;
            }
            MAType::ZLEMA => {
                let _xr10 = match self.zlema(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr10.beg_idx;
                (*outNBElement) = _xr10.count;
                retCode = RetCode::Success;
            }
            MAType::RMA => {
                let _xr11 = match self.rma(startIdx, endIdx, inReal, optInTimePeriod, outReal) {
                    Ok(_r) => _r,
                    Err(_e) => return _e,
                };
                (*outBegIdx) = _xr11.beg_idx;
                (*outNBElement) = _xr11.count;
                retCode = RetCode::Success;
            }
            _ => {
                retCode = RetCode::BadParam;
            }
        }
        return retCode;
    }
    pub fn ma(
        &self,
        startIdx: usize,
        endIdx: usize,
        inReal: &[f64],
        optInTimePeriod: i32,
        optInMAType: MAType,
        outReal: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        if startIdx > Core::INDEX_MAX {
            return Err(RetCode::OutOfRangeStartIndex);
        }
        if endIdx > Core::INDEX_MAX || endIdx < startIdx {
            return Err(RetCode::OutOfRangeEndIndex);
        }
        let _guardLb = self.ma_lookback(optInTimePeriod, optInMAType)?;
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
        let retCode = self.ma_impl(
            startIdx,
            endIdx,
            inReal,
            optInTimePeriod,
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
