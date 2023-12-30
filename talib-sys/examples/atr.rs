extern crate talib_sys;
use talib_sys::{TA_Integer, TA_Real, TA_ATR,  TA_RetCode};


/// Compute ATR(period)
/// This function returns a tuple containing the list of ATR values and the index of the first
/// candle to have an associated ATR value
fn atr(period: u32, high: &Vec<TA_Real>, low: &Vec<TA_Real>,
       close: &Vec<TA_Real>) -> (Vec<TA_Real>, TA_Integer) 
{
    let mut out: Vec<TA_Real> = Vec::with_capacity(close.len());
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    unsafe {
        let ret_code = TA_ATR(
            0,                              // index of the first close to use
            close.len() as i32 - 1,         // index of the last close to use
            high.as_ptr(),                  // pointer to the first element of the high vector
            low.as_ptr(),                   // pointer to the first element of the low vector
            close.as_ptr(),                 // pointer to the first element of the close vector
            period as i32,                  // period of the atr
            &mut out_begin,                 // set to index of the first close to have an atr value
            &mut out_size,                  // set to number of atr values computed
            out.as_mut_ptr()                // pointer to the first element of the output vector
        );
        match ret_code {
            // Indicator was computed correctly, since the vector was filled by TA-lib C library,
            // Rust doesn't know what is the new length of the vector, so we set it manually
            // to the number of values returned by the TA_ATR call
            TA_RetCode::TA_SUCCESS => out.set_len(out_size as usize),        
            // An error occured
            _ => panic!("Could not compute indicator, err: {:?}", ret_code)  
        }
    }

    (out, out_begin)
}

fn main() {
    let high: Vec<TA_Real> = vec![
        1.087130, 1.087120, 1.087220, 1.087230, 1.087180, 1.087160, 1.087210, 1.087150, 1.087200,
        1.087230, 1.087070, 1.087000, 1.086630, 1.086650, 1.086680, 1.086690, 1.086690, 1.086690,
        1.086690, 1.086650
    ];
    let low: Vec<TA_Real> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630
    ];
    let close: Vec<TA_Real> = vec![
        1.087130, 1.087120, 1.087220, 1.087230, 1.087110, 1.087120, 1.087100, 1.087120, 1.087130,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086650, 1.086640, 1.086690, 1.086650, 1.086690,
        1.086670, 1.086640
    ];

    let (atr_values, begin) = atr(7, &high, &low, &close);

    // print values
    for (index, value) in atr_values.iter().enumerate() {
        println!("index {} = {}", begin + index as i32 + 1, value);
    }
}