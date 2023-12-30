extern crate talib_sys;
use talib_sys::{TA_Integer, TA_Real, TA_MA, TA_MAType, TA_RetCode};


/// Compute SMA(period) on `close_prices`
/// This function returns a tuple containing the list of sma values and the index of the first
/// close to have an associated sma value
fn sma(period: u32, close_prices: &Vec<TA_Real>) -> (Vec<TA_Real>, TA_Integer) {
    let mut out: Vec<TA_Real> = Vec::with_capacity(close_prices.len());
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    unsafe {
        let ret_code = TA_MA(
            0,                              // index of the first close to use
            close_prices.len() as i32 - 1,  // index of the last close to use
            close_prices.as_ptr(),          // pointer to the first element of the vector
            period as i32,                  // period of the sma
            TA_MAType::TA_MAType_SMA,       // type of the MA, here forced to sma
            &mut out_begin,                 // set to index of the first close to have an sma value
            &mut out_size,                  // set to number of sma values computed
            out.as_mut_ptr()                // pointer to the first element of the output vector
        );
        match ret_code {
            // Indicator was computed correctly, since the vector was filled by TA-lib C library,
            // Rust doesn't know what is the new length of the vector, so we set it manually
            // to the number of values returned by the TA_MA call
            TA_RetCode::TA_SUCCESS => out.set_len(out_size as usize),        
            // An error occured
            _ => panic!("Could not compute indicator, err: {:?}", ret_code)  
        }
    }

    (out, out_begin)
}

fn main() {
    let close_prices: Vec<TA_Real> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630
    ];

    // compute sma, since we use a period of 10, the first 10 closes won't have
    // an sma value because there is not enough data, so begin will be set to
    // the index 29
    let (sma_values, begin) = sma(10, &close_prices);

    // print values
    for (index, value) in sma_values.iter().enumerate() {
        println!("Close index {} = {}", begin + index as i32 + 1, value);
    }
}