# Test Suite

This folder contains test scripts for the ML trading platform.

## 📁 Test Files

### `test_3_markets.py`
Tests for the three main market indices (IBEX35, S&P500, NIKKEI).

### `test_backfill_fix.py`
Tests for the historical backfill functionality.

### `test_assets.py`
Tests for symbol resolution and default markets.

### `test_clean_data.py`
Tests for data cleaning and business-day filling.

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_3_markets.py
```

---

For more information, see the main [README.md](../README.md)
