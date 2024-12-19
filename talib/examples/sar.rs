use talib::common::{ta_initialize, ta_shutdown};
use talib::overlap::{ta_sar, SarKwargsBuilder};

fn main() {
    let _ = ta_initialize();

    let high_prices: Vec<f64> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630,
    ];
    let low_prices: Vec<f64> = vec![
        1.087010, 1.087120, 1.087080, 1.087170, 1.087110, 1.087010, 1.087100, 1.087120, 1.087110,
        1.087080, 1.087000, 1.086630, 1.086630, 1.086610, 1.086630, 1.086640, 1.086650, 1.086650,
        1.086670, 1.086630,
    ];

    let kwargs = SarKwargsBuilder::default()
        .acceleration(0.02)
        .maximum(0.2)
        .build()
        .unwrap();

    let res = ta_sar(high_prices.as_ptr(), low_prices.as_ptr(), high_prices.len(), &kwargs);

    match res {
        Ok(sar_values) => {
            println!("SAR values: {:?}", sar_values);
        }
        Err(e) => {
            println!("Error: {:?}", e);
        }
    }

    let _ = ta_shutdown();
}
