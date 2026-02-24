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
pip install -r requirements.txt

# Run scheduler (starts automatically)
python scripts/automation/scheduler.py

# Run specific task immediately (for testing)
python scripts/automation/scheduler.py --run fetch
python scripts/automation/scheduler.py --run indicators
python scripts/automation/scheduler.py --run predictions
python scripts/automation/scheduler.py --run all

# List scheduled jobs
python scripts/automation/scheduler.py --list
```

**Features:**
- ✅ No external dependencies (pure Python)
- ✅ Lightweight and fast
- ✅ Easy to configure
- ✅ Built-in logging
- ✅ Manual task execution for testing

**Schedule (Mon-Fri):**
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
0 8 * * 1-5 cd /path/to/project && python scripts/automation/scheduler.py --run fetch
30 8 * * 1-5 cd /path/to/project && python scripts/automation/scheduler.py --run indicators
0 9 * * 1-5 cd /path/to/project && python scripts/automation/scheduler.py --run predictions
30 9 * * 1-5 cd /path/to/project && python scripts/automation/scheduler.py --run validate
0 10 * * 1-5 cd /path/to/project && python scripts/automation/scheduler.py --run report
0 2 * * 0 cd /path/to/project && python scripts/automation/scheduler.py --run retrain
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
  command: python scripts/automation/scheduler.py
  depends_on:
    - db
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
ExecStart=/usr/bin/python3 /path/to/project/scripts/automation/scheduler.py
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

**For your project:** Use **APScheduler** (`scripts/automation/scheduler.py`)

**Why?**
- ✅ No Docker required (simpler)
- ✅ Pure Python (easy to debug)
- ✅ Lightweight (no overhead)
- ✅ All code in one place
- ✅ Easy to test individual tasks
- ✅ Perfect for academic projects

---

## 🔧 Customization

Edit `scripts/automation/scheduler.py` to change:
- Task schedules (modify `CronTrigger`)
- Task order
- Add new tasks
- Adjust retry logic

Env vars (optional):
- `SCHEDULER_TIMEZONE` (default: Europe/Madrid)
- `SCHEDULER_FETCH_PERIOD` (default: 1mo)
- `LOG_LEVEL`, `LOG_TO_FILE`, `LOG_DIR`

---

## 📝 Logs

Scheduler logs to console. To save to file:

```bash
python scripts/automation/scheduler.py >> logs/scheduler.log 2>&1
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
