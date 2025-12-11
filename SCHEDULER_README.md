# 🔄 Automated Scheduler - n8n Alternative

## 📋 Summary

Instead of n8n, you can use **APScheduler** - a pure Python scheduling library that's:
- ✅ Lightweight (no Docker containers needed)
- ✅ Easy to setup (one pip install)
- ✅ Python-native (debug easily)
- ✅ Perfect for your use case

---

## 🚀 Quick Start (Recommended)

### Option 1: APScheduler (Python-native) ⭐ RECOMMENDED

```bash
# Install dependencies
pip install apscheduler

# Run scheduler (starts automatically)
python scheduler.py

# Run specific task immediately (for testing)
python scheduler.py --run fetch
python scheduler.py --run indicators
python scheduler.py --run predictions
python scheduler.py --run all

# List scheduled jobs
python scheduler.py --list
```

**Features:**
- ✅ No external dependencies (pure Python)
- ✅ Lightweight and fast
- ✅ Easy to configure
- ✅ Built-in logging
- ✅ Manual task execution for testing

**Schedule:**
- 8:00 AM - Fetch market data
- 8:30 AM - Compute indicators
- 9:00 AM - Run ML predictions
- 9:30 AM - Validate predictions
- 10:00 AM - Generate daily report
- Sundays 2:00 AM - Weekly model retraining

---

### Option 2: Cron Jobs (System-level)

**For Linux/Mac:**

```bash
# Edit crontab
crontab -e

# Add these lines:
0 8 * * * cd /path/to/project && python -c "from scheduler import task_fetch_data; task_fetch_data()"
30 8 * * * cd /path/to/project && python -c "from scheduler import task_compute_indicators; task_compute_indicators()"
0 9 * * * cd /path/to/project && python -c "from scheduler import task_ml_predictions; task_ml_predictions()"
30 9 * * * cd /path/to/project && python -c "from scheduler import task_validate_predictions; task_validate_predictions()"
0 10 * * * cd /path/to/project && python -c "from scheduler import task_daily_report; task_daily_report()"
0 2 * * 0 cd /path/to/project && python -c "from scheduler import task_weekly_retraining; task_weekly_retraining()"
```

---

### Option 3: Docker with Cron

```dockerfile
# Add to docker-compose.yml
scheduler:
  image: python:3.11
  volumes:
    - .:/app
  working_dir: /app
  command: python scheduler.py
  depends_on:
    - postgres
```

---

### Option 4: Systemd Service (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/stock-scheduler.service

# Add:
[Unit]
Description=Stock ML Platform Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable stock-scheduler
sudo systemctl start stock-scheduler
sudo systemctl status stock-scheduler
```

---

## 📊 Comparison: n8n vs Alternatives

| Feature | n8n | APScheduler | Cron | Airflow |
|---------|-----|-------------|------|---------|
| Setup Complexity | Medium | Easy | Very Easy | Hard |
| Dependencies | Docker | Python only | System | Many |
| Visual UI | ✅ | ❌ | ❌ | ✅ |
| Python Integration | Good | Excellent | Good | Excellent |
| Monitoring | ✅ | Manual | Manual | ✅ |
| Lightweight | ❌ | ✅ | ✅ | ❌ |
| **Recommended** | - | ⭐ | ⭐ | - |

---

## 🎯 Recommendation

**For your project:** Use **APScheduler** (`scheduler.py`)

**Why?**
- ✅ No Docker required (simpler)
- ✅ Pure Python (easy to debug)
- ✅ Lightweight (no overhead)
- ✅ All code in one place
- ✅ Easy to test individual tasks
- ✅ Perfect for academic projects

---

## 🔧 Customization

Edit `scheduler.py` to change:
- Task schedules (modify `CronTrigger`)
- Task order
- Add new tasks
- Adjust retry logic

---

## 📝 Logs

Scheduler logs to console. To save to file:

```bash
python scheduler.py >> logs/scheduler.log 2>&1
```

---

## 🆚 When to Use n8n Instead

Use n8n if you need:
- Visual workflow builder
- Non-technical user configuration
- Webhook integrations
- Complex branching logic
- Multiple integrations (email, Slack, etc.)

For simple data updates → **APScheduler is better** ⭐
