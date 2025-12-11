# 📁 Quick Project Structure Reference

## 🎯 Where to Find Everything

### 🚀 Getting Started
```bash
./scripts/quickstart.sh              # Interactive menu - START HERE!
```

### 📱 Main Applications (Root)
```
streamlit_dashboard.py               # Web dashboard (http://localhost:8501)
telegram_bot.py                      # Telegram bot
docker-compose.yml                   # Infrastructure setup
```

### 🧠 Core ML Code
```
mcp_server/scripts/
├── models.py                        # 7 ML models + ensemble
├── backtesting.py                   # Performance validation
├── advanced_indicators.py           # MACD, Bollinger, ADX, etc.
├── indicators.py                    # SMA, RSI, Volatility
├── fetch_data.py                    # Data ingestion
└── config.py                        # Configuration
```

### 📊 Data & Reports
```
data/db/                             # PostgreSQL data (auto-managed)
data/models/                         # Trained ML models (.pkl)
backtest_reports/                    # Backtesting results (JSON)
reports/                             # General reports
```

### 📚 Documentation
```
docs/NEW_FEATURES.md                 # Latest features guide ⭐
docs/CHECKLIST.md                    # Verification checklist
docs/REQUIREMENTS.md                 # System requirements
README.md                            # Main documentation
```

### 🔧 Utilities
```
scripts/quickstart.sh                # Interactive launcher ⭐
scripts/run_backfill.sh             # Historical backfill
tests/                               # Test suite
```

### ⚙️ Configuration
```
.env                                 # Environment variables
requirements-new-features.txt        # New dependencies
```

---

## 🎯 Common Tasks

| Task | File/Command |
|------|-------------|
| Launch dashboard | `streamlit run streamlit_dashboard.py` |
| Start bot | `python telegram_bot.py` |
| Run backtest | `python -m mcp_server.scripts.backtesting` |
| Calculate indicators | `python -m mcp_server.scripts.advanced_indicators` |
| View docs | `cat docs/NEW_FEATURES.md` |
| Quick start | `./scripts/quickstart.sh` |

---

## 📊 Project Stats

- **15,000+** lines of code
- **25+** Python modules
- **7** ML models
- **13+** technical indicators
- **4** dashboard tabs
- **10+** Telegram commands
- **20+** API endpoints

---

**Need more details?** See full structure in `PROJECT_STRUCTURE.txt`
