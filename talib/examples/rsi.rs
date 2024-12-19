use talib::common::{TimePeriodKwargs, TimePeriodKwargsBuilder, ta_initialize, ta_shutdown};
use talib::momentum::ta_rsi;

fn main() {
    let _ = ta_initialize();
    let close_prices: Vec<f64> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630,
    ];
    let _kwargs = TimePeriodKwargs { timeperiod: 5 };
    // or 
    let kwargs = TimePeriodKwargsBuilder::default().timeperiod(5).build().unwrap();
    let res = ta_rsi(close_prices.as_ptr(), close_prices.len(), &kwargs);

    match res {
        Ok(rsi_values) => {
            for (index, value) in rsi_values.iter().enumerate() {
                println!("Close index {} = {}", index, value);
            }
        }
        Err(e) => {
            println!("Error: {:?}", e);
        }
    }
    let _ = ta_shutdown();
}
