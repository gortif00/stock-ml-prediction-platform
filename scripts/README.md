# Project Scripts - scripts/README.md

This folder contains all executable scripts organized by category for project management and automation.

## 📁 Folder Structure

### `automation/`
Automated task scheduling and background processes:
- **`scheduler.py`** - APScheduler-based automation (n8n alternative)
  - Daily market data fetches (8:00 AM)
  - Indicator computation (8:30 AM)
  - ML predictions (9:00 AM)
  - Validation & reports (9:30-10:00 AM)
  - Weekly model retraining (Sundays 2:00 AM)

### `ui/`
User interface scripts for visualization and interaction:
- **`streamlit_dashboard.py`** - Interactive web dashboard
  - Multi-tab interface (prices, indicators, backtesting, heatmap)
  - Real-time data visualization
  - Model comparison charts
  - Available at http://localhost:8501

- **`telegram_bot.py`** - Telegram bot for mobile alerts
  - Market queries and predictions
  - Personalized subscriptions
  - Real-time notifications
  - 10+ commands (/mercados, /predicciones, /backtest, etc.)

### `utilities/`
Helper scripts and interactive tools:
- **`quickstart.sh`** - Interactive menu launcher
  - One-stop access to all features
  - Dependency checking
  - Service orchestration
  
- **`run_backfill.sh`** - Historical data backfill
  - Generate past predictions without look-ahead bias
  - Useful for testing and validation

## 🚀 Quick Start

```bash
# Launch interactive menu
./scripts/utilities/quickstart.sh

# Or run specific components
streamlit run scripts/ui/streamlit_dashboard.py
python3 scripts/ui/telegram_bot.py
python3 scripts/automation/scheduler.py
```

## 📋 Requirements

- Python 3.11+
- Dependencies: `requirements-new-features.txt`, `requirements-scheduler.txt`
- PostgreSQL (via Docker)
- Telegram Bot Token (for bot features)

---

For more information, see the main [README.md](../README.md) and [NEW_FEATURES.md](../docs/NEW_FEATURES.md)
