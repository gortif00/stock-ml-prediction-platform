# User Interface Scripts

This folder contains user-facing interface scripts for visualization and interaction.

## 📄 Files

### `streamlit_dashboard.py`
Interactive web dashboard for data visualization and analysis.

**Features:**
- **Tab 1: Prices & Predictions** - Candlestick charts with ML predictions overlay
- **Tab 2: Technical Indicators** - Multi-panel indicator visualization (SMA, RSI, MACD, Bollinger, etc.)
- **Tab 3: Backtesting** - Run historical validation and view metrics
- **Tab 4: Correlation Heatmap** - Asset correlation analysis

**Usage:**
```bash
streamlit run scripts/ui/streamlit_dashboard.py
```

Access at: http://localhost:8501

**Dependencies:**
- Streamlit 1.28.0+
- Plotly 5.17.0+
- pandas, numpy

---

### `telegram_bot.py`
Telegram bot for mobile alerts and real-time market queries.

**Features:**
- Real-time market price queries
- ML prediction alerts
- Personalized market subscriptions
- Backtesting on demand
- Daily summary reports

**Commands:**
- `/start` - Welcome and help
- `/mercados` - List all available markets
- `/seguir <symbol>` - Subscribe to market updates
- `/dejar <symbol>` - Unsubscribe from market
- `/predicciones` - View latest predictions
- `/resumen` - Daily market summary
- `/backtest <symbol>` - Run backtesting
- `/ayuda` - Show all commands

**Setup:**
1. Get bot token from [@BotFather](https://t.me/BotFather)
2. Set environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN='your_token_here'
   ```
3. Run bot:
   ```bash
   python3 scripts/ui/telegram_bot.py
   ```

**Dependencies:**
- python-telegram-bot 20.6+
- PostgreSQL connection

---

See [NEW_FEATURES.md](../../docs/NEW_FEATURES.md) for detailed feature documentation.
