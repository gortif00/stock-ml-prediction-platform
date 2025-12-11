# Automation Scripts

This folder contains automated task scheduling and background processes.

## 📄 Files

### `scheduler.py`
APScheduler-based task automation system (alternative to n8n).

**Features:**
- Daily market data fetching (8:00 AM)
- Technical indicator computation (8:30 AM)
- ML predictions generation (9:00 AM)
- Prediction validation (9:30 AM)
- Daily report generation (10:00 AM)
- Weekly model retraining (Sundays 2:00 AM)

**Usage:**
```bash
# Run scheduler continuously
python3 scripts/automation/scheduler.py

# Test specific task
python3 scripts/automation/scheduler.py --run fetch
python3 scripts/automation/scheduler.py --run indicators
python3 scripts/automation/scheduler.py --run predictions
python3 scripts/automation/scheduler.py --run all
```

**Configuration:**
- Modify task times in the scheduler code
- Configure markets in `mcp_server/scripts/config.py`
- Set database connection in `.env`

**Advantages over n8n:**
- Lightweight (50MB vs 500MB memory)
- Pure Python (no Docker overhead)
- Integrated with existing codebase
- Easy to debug and extend

---

See [SCHEDULER_README.md](../../SCHEDULER_README.md) for detailed documentation.
