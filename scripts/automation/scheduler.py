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
from datetime import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_server', 'scripts'))

from mcp_server.scripts.fetch_data import fetch_and_store_prices
from mcp_server.scripts.indicators import compute_indicators_for_symbol
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol
from mcp_server.scripts.models import predict_ensemble
from mcp_server.scripts.validate_predictions import validate_predictions_yesterday
from mcp_server.scripts.reporting import generate_daily_report
from mcp_server.scripts.assets import get_symbols

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# SCHEDULED TASKS
# ============================================================================

def task_fetch_data():
    """Task 1: Fetch market data for all symbols."""
    logger.info("=" * 60)
    logger.info("TASK 1: FETCHING MARKET DATA")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}...")
            fetch_and_store_prices(symbol, days_back=7)
            logger.info(f"✅ {symbol} data updated")
        
        logger.info("✅ All market data fetched successfully")
    except Exception as e:
        logger.error(f"❌ Error fetching data: {e}")


def task_compute_indicators():
    """Task 2: Compute technical indicators for all symbols."""
    logger.info("=" * 60)
    logger.info("TASK 2: COMPUTING TECHNICAL INDICATORS")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            logger.info(f"Computing indicators for {symbol}...")
            
            # Basic indicators
            compute_indicators_for_symbol(symbol)
            
            # Advanced indicators
            compute_advanced_indicators_for_symbol(symbol)
            
            logger.info(f"✅ {symbol} indicators updated")
        
        logger.info("✅ All indicators computed successfully")
    except Exception as e:
        logger.error(f"❌ Error computing indicators: {e}")


def task_ml_predictions():
    """Task 3: Run ML predictions for all symbols."""
    logger.info("=" * 60)
    logger.info("TASK 3: RUNNING ML PREDICTIONS")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            logger.info(f"Running predictions for {symbol}...")
            result = predict_ensemble(symbol, force_retrain=False)
            
            if 'error' not in result:
                logger.info(f"✅ {symbol}: {result.get('ensemble_signal')} "
                          f"(confidence: {result.get('ensemble_confidence', 0):.0%})")
            else:
                logger.warning(f"⚠️  {symbol}: {result['error']}")
        
        logger.info("✅ All predictions completed")
    except Exception as e:
        logger.error(f"❌ Error in predictions: {e}")


def task_validate_predictions():
    """Task 4: Validate yesterday's predictions."""
    logger.info("=" * 60)
    logger.info("TASK 4: VALIDATING PREDICTIONS")
    logger.info("=" * 60)
    
    try:
        result = validate_predictions_yesterday()
        logger.info(f"✅ Validated {result.get('total_validated', 0)} predictions")
    except Exception as e:
        logger.error(f"❌ Error validating predictions: {e}")


def task_daily_report():
    """Task 5: Generate daily report."""
    logger.info("=" * 60)
    logger.info("TASK 5: GENERATING DAILY REPORT")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            report = generate_daily_report(symbol)
            logger.info(f"✅ Report generated for {symbol}")
        
        logger.info("✅ All reports generated")
    except Exception as e:
        logger.error(f"❌ Error generating reports: {e}")


def task_weekly_retraining():
    """Task 6: Weekly model retraining."""
    logger.info("=" * 60)
    logger.info("TASK 6: WEEKLY MODEL RETRAINING")
    logger.info("=" * 60)
    
    try:
        symbols = get_symbols()
        for symbol in symbols:
            logger.info(f"Retraining models for {symbol}...")
            result = predict_ensemble(symbol, force_retrain=True, tune_hyperparams=False)
            logger.info(f"✅ {symbol} models retrained")
        
        logger.info("✅ All models retrained")
    except Exception as e:
        logger.error(f"❌ Error retraining models: {e}")


# ============================================================================
# SCHEDULER SETUP
# ============================================================================

def create_scheduler():
    """Create and configure the scheduler."""
    scheduler = BlockingScheduler()
    
    # ===== DAILY TASKS =====
    
    # Task 1: Fetch data at 8:00 AM (after markets open)
    scheduler.add_job(
        task_fetch_data,
        CronTrigger(hour=8, minute=0),
        id='fetch_data',
        name='Fetch Market Data',
        replace_existing=True
    )
    
    # Task 2: Compute indicators at 8:30 AM
    scheduler.add_job(
        task_compute_indicators,
        CronTrigger(hour=8, minute=30),
        id='compute_indicators',
        name='Compute Technical Indicators',
        replace_existing=True
    )
    
    # Task 3: ML predictions at 9:00 AM
    scheduler.add_job(
        task_ml_predictions,
        CronTrigger(hour=9, minute=0),
        id='ml_predictions',
        name='Run ML Predictions',
        replace_existing=True
    )
    
    # Task 4: Validate predictions at 9:30 AM
    scheduler.add_job(
        task_validate_predictions,
        CronTrigger(hour=9, minute=30),
        id='validate_predictions',
        name='Validate Predictions',
        replace_existing=True
    )
    
    # Task 5: Daily report at 10:00 AM
    scheduler.add_job(
        task_daily_report,
        CronTrigger(hour=10, minute=0),
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
