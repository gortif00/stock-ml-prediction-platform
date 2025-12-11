# Utility Scripts

This folder contains helper scripts and interactive tools for development and operations.

## 📄 Files

### `quickstart.sh`
Interactive menu launcher providing one-stop access to all project features.

**Features:**
- Dependency verification (Python, Docker, PostgreSQL)
- Package installation automation
- Interactive menu with 7 options:
  1. Launch Streamlit Dashboard
  2. Start Telegram Bot
  3. Run Backtesting
  4. Calculate Advanced Indicators
  5. Launch Everything (Dashboard + Bot)
  6. Start Scheduler
  7. View Documentation

**Usage:**
```bash
# Make executable (first time only)
chmod +x scripts/utilities/quickstart.sh

# Run interactive menu
./scripts/utilities/quickstart.sh
```

**Requirements:**
- Python 3.11+
- Docker (for PostgreSQL)
- Dependencies auto-installed from requirements files

---

### `run_backfill.sh`
Historical data backfill script for generating past predictions.

**Purpose:**
Generate ML predictions for historical dates without look-ahead bias. Useful for:
- Model validation
- Performance testing
- Historical analysis
- Filling data gaps

**Usage:**
```bash
# Make executable (first time only)
chmod +x scripts/utilities/run_backfill.sh

# Run backfill
./scripts/utilities/run_backfill.sh
```

**Configuration:**
Edit script to set:
- Start date
- End date
- Market symbols
- Prediction parameters

**Note:** Backfilling is computationally intensive. Use date ranges wisely.

---

See [BACKFILL_README.md](../../docs/BACKFILL_README.md) for backfill details.
