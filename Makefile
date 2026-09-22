dev:
	maturin develop

dev-release:
	maturin develop --release

sync:
	uv sync

test:
	uv run --no-sync pytest --benchmark-disable

bench:
	uv run --no-sync pytest tests/test_bench.py --benchmark-only --benchmark-columns=min,mean,ops --benchmark-sort=name

regen-bindings:
	cd talib-sys && cargo build --features bindgen

gen-functions:
	uv run --no-sync python scripts/gen_talib_functions.py --apply
