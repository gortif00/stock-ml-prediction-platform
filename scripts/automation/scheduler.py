"""
Automated Scheduler for Stock ML Platform - Alternative to n8n

This script replaces n8n workflows with Python-native scheduling using APScheduler.
Runs automated tasks for data updates, indicators, predictions, and validation.

Features:
- Fetch market data daily
- Calculate indicators
- Run ML predictions
- Validate predictions
- Generate reports
- No external workflow engine needed
"""

import sys
import os
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Add project root to path for imports (robust to cwd)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables from .env if present
load_dotenv()

from mcp_server.scripts.fetch_data import update_prices_for_symbol
from mcp_server.scripts.indicators import compute_indicators_for_symbol
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol
from mcp_server.scripts.models import predict_ensemble
from mcp_server.scripts.validate_predictions import validate_predictions_yesterday
from mcp_server.scripts.reporting import generate_daily_report
from mcp_server.scripts.assets import get_symbols
from mcp_server.scripts.config import close_db_pool

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "0") == "1"


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("scheduler")
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    if not logger.handlers:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

        if LOG_TO_FILE:
            os.makedirs(LOG_DIR, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(LOG_DIR, "scheduler.log"),
                maxBytes=5_000_000,
                backupCount=5,
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    logger.propagate = False
    return logger


logger = _setup_logging()

# Scheduler settings
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Europe/Madrid")
FETCH_PERIOD = os.getenv("SCHEDULER_FETCH_PERIOD", "1mo")
JOB_DEFAULTS = {
    "coalesce": True,
    "max_instances": 1,
    "misfire_grace_time": 900,  # 15 minutes
}
try:
    SCHEDULER_TZ = ZoneInfo(SCHEDULER_TIMEZONE)
except Exception:
    logger.warning(
        "Invalid SCHEDULER_TIMEZONE=%s, using UTC",
        SCHEDULER_TIMEZONE,
    )
    SCHEDULER_TZ = ZoneInfo("UTC")


# ============================================================================
# SCHEDULED TASKS
# ============================================================================

def task_fetch_data():
    """Task 1: Fetch market data for all symbols."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 1: FETCHING MARKET DATA")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        total_rows = 0
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}...")
            rows = update_prices_for_symbol(symbol, period=FETCH_PERIOD)
            total_rows += rows
            logger.info(f"✅ {symbol} data updated")
        
        duration = time.time() - start
        logger.info(
            "✅ All market data fetched successfully (symbols=%d, rows=%d, duration=%.1fs)",
            len(symbols),
            total_rows,
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error fetching data: {e}")


def task_compute_indicators():
    """Task 2: Compute technical indicators for all symbols."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 2: COMPUTING TECHNICAL INDICATORS")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        total_basic = 0
        total_advanced = 0
        for symbol in symbols:
            logger.info(f"Computing indicators for {symbol}...")
            
            # Basic indicators
            total_basic += compute_indicators_for_symbol(symbol)
            
            # Advanced indicators
            total_advanced += compute_advanced_indicators_for_symbol(symbol)
            
            logger.info(f"✅ {symbol} indicators updated")
        
        duration = time.time() - start
        logger.info(
            "✅ All indicators computed successfully (symbols=%d, basic_rows=%d, advanced_rows=%d, duration=%.1fs)",
            len(symbols),
            total_basic,
            total_advanced,
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error computing indicators: {e}")


def task_ml_predictions():
    """Task 3: Run ML predictions for all symbols."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 3: RUNNING ML PREDICTIONS")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        ok = 0
        for symbol in symbols:
            logger.info(f"Running predictions for {symbol}...")
            result = predict_ensemble(symbol, force_retrain=False)
            
            if 'error' not in result:
                ok += 1
                ml_signals = result.get("ml_signals", [])
                if ml_signals:
                    count_buy = ml_signals.count(1)
                    count_sell = ml_signals.count(-1)
                    count_neutral = ml_signals.count(0)
                    consensus = max(count_buy, count_sell, count_neutral) / len(ml_signals)
                else:
                    consensus = 0
                logger.info(
                    f"✅ {symbol}: {result.get('signal_ensemble')} "
                    f"(confidence: {consensus:.0%})"
                )
            else:
                logger.warning(f"⚠️  {symbol}: {result['error']}")
        
        duration = time.time() - start
        logger.info(
            "✅ All predictions completed (symbols=%d, ok=%d, duration=%.1fs)",
            len(symbols),
            ok,
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error in predictions: {e}")


def task_validate_predictions():
    """Task 4: Validate yesterday's predictions."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 4: VALIDATING PREDICTIONS")
    logger.info("=" * 60)
    
    try:
        result = validate_predictions_yesterday()
        duration = time.time() - start
        logger.info(
            "✅ Validated %d predictions (duration=%.1fs)",
            result.get("total_validated", 0),
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error validating predictions: {e}")


def task_daily_report():
    """Task 5: Generate daily report."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 5: GENERATING DAILY REPORT")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        total_reports = 0
        for symbol in symbols:
            report = generate_daily_report(symbol)
            logger.info(f"✅ Report generated for {symbol}")
            if report:
                total_reports += 1
        
        duration = time.time() - start
        logger.info(
            "✅ All reports generated (symbols=%d, reports=%d, duration=%.1fs)",
            len(symbols),
            total_reports,
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")


def task_weekly_retraining():
    """Task 6: Weekly model retraining."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("TASK 6: WEEKLY MODEL RETRAINING")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            logger.info(f"Retraining models for {symbol}...")
            result = predict_ensemble(symbol, force_retrain=True, tune_hyperparams=False)
            logger.info(f"✅ {symbol} models retrained")
        
        duration = time.time() - start
        logger.info(
            "✅ All models retrained (symbols=%d, duration=%.1fs)",
            len(symbols),
            duration,
        )
    except Exception as e:
        logger.error(f"❌ Error retraining models: {e}")


# ============================================================================
# SCHEDULER SETUP
# ============================================================================

def create_scheduler():
    """Create and configure the scheduler."""
    scheduler = BlockingScheduler(timezone=SCHEDULER_TZ, job_defaults=JOB_DEFAULTS)
    
    # ===== DAILY TASKS =====
    
    # Task 1: Fetch data at 8:00 AM (after markets open)
    scheduler.add_job(
        task_fetch_data,
        CronTrigger(day_of_week="mon-fri", hour=8, minute=0),
        id='fetch_data',
        name='Fetch Market Data',
        replace_existing=True
    )
    
    # Task 2: Compute indicators at 8:30 AM
    scheduler.add_job(
        task_compute_indicators,
        CronTrigger(day_of_week="mon-fri", hour=8, minute=30),
        id='compute_indicators',
        name='Compute Technical Indicators',
        replace_existing=True
    )
    
    # Task 3: ML predictions at 9:00 AM
    scheduler.add_job(
        task_ml_predictions,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=0),
        id='ml_predictions',
        name='Run ML Predictions',
        replace_existing=True
    )
    
    # Task 4: Validate predictions at 9:30 AM
    scheduler.add_job(
        task_validate_predictions,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=30),
        id='validate_predictions',
        name='Validate Predictions',
        replace_existing=True
    )
    
    # Task 5: Daily report at 10:00 AM
    scheduler.add_job(
        task_daily_report,
        CronTrigger(day_of_week="mon-fri", hour=10, minute=0),
        id='daily_report',
        name='Generate Daily Report',
        replace_existing=True
    )
    
    # ===== WEEKLY TASKS =====
    
    # Task 6: Weekly retraining on Sundays at 2:00 AM
    scheduler.add_job(
        task_weekly_retraining,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='weekly_retraining',
        name='Weekly Model Retraining',
        replace_existing=True
    )
    
    return scheduler


# ============================================================================
# MANUAL EXECUTION (for testing)
# ============================================================================

def run_task_now(task_name):
    """Run a specific task immediately for testing."""
    tasks = {
        'fetch': task_fetch_data,
        'indicators': task_compute_indicators,
        'predictions': task_ml_predictions,
        'validate': task_validate_predictions,
        'report': task_daily_report,
        'retrain': task_weekly_retraining,
        'all': lambda: [task_fetch_data(), task_compute_indicators(), 
                       task_ml_predictions(), task_validate_predictions(), 
                       task_daily_report()]
    }
    
    if task_name in tasks:
        logger.info(f"\n🚀 Running task: {task_name}\n")
        tasks[task_name]()
    else:
        logger.error(f"Unknown task: {task_name}")
        logger.info(f"Available tasks: {', '.join(tasks.keys())}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock ML Platform Scheduler')
    parser.add_argument('--run', type=str, help='Run specific task immediately')
    parser.add_argument('--list', action='store_true', help='List all scheduled jobs')
    
    args = parser.parse_args()
    
    if args.run:
        # Run task immediately
        run_task_now(args.run)
    elif args.list:
        # List scheduled jobs
        scheduler = create_scheduler()
        print("\n📅 SCHEDULED JOBS:")
        print("=" * 60)
        for job in scheduler.get_jobs():
            print(f"  {job.id:20} - {job.name}")
            print(f"  {'':20}   Next run: {job.next_run_time}")
        print("=" * 60)
    else:
        # Start scheduler
        logger.info("=" * 60)
        logger.info("🚀 STARTING AUTOMATED SCHEDULER")
        logger.info("=" * 60)
        
        scheduler = create_scheduler()
        
        # Print scheduled jobs
        logger.info("\n📅 Scheduled Jobs:")
        for job in scheduler.get_jobs():
            logger.info(f"  • {job.name} - Next run: {job.next_run_time}")
        
        logger.info("\n✅ Scheduler started. Press Ctrl+C to stop.\n")
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n⏹️  Scheduler stopped by user")
            close_db_pool()
