# talib

## Ta-Lib Safe Wrapper for Rust
This is a safe Rust wrapper for the Ta-Lib (Technical Analysis Library)


## Installation
``` bash
cargo add talib
```

## Example
``` rust
use talib::common::{TimePeriodKwargs, ta_initialize, ta_shutdown};
use talib::momentum::ta_rsi;

fn main() {
    // Initialize Ta-Lib
    let _ = ta_initialize();

    // Sample close prices
    let close_prices: Vec<f64> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630,
    ];

    // Specify the RSI calculation parameters
    let kwargs = TimePeriodKwargs { timeperiod: 5 };
    // or with builder
    let kwargs = TimePeriodKwargsBuilder::default()
        .timeperiod(5)
        .build()
        .unwrap();

    // Calculate RSI
    let res = ta_rsi(close_prices.as_ptr(), close_prices.len(), &kwargs);

    // Process the result
    match res {
        Ok(rsi_values) => {
            for (index, value) in rsi_values.iter().enumerate() {
                println!("RSI at index {}: {}", index, value);
            }
        }
        Err(e) => {
            println!("Error: {:?}", e);
        }
    }

    // Shutdown Ta-Lib
    let _ = ta_shutdown();
}

```




