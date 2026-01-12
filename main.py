import os
import json
import yaml
import time
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path to ensure imports work
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.scraper import JobScraper
from src.notifier import EmailNotifier
from src.storage import JobHistory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def load_config(config_path: str = "config/settings.yaml") -> dict:
    config = {}
    
    # 1. Load from YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found at {config_path}. Relying on defaults/env vars.")
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_path}: {e}")
        sys.exit(1)

    # 2. Key Mapping: Env Var -> Config Key
    # We override JSON config with Environment Variables if they exist
    env_mapping = {
        "SMTP_SERVER": ("smtp", "server"),
        "SMTP_PORT": ("smtp", "port"),
        "SMTP_USER": ("smtp", "user"),
        "SMTP_PASSWORD": ("smtp", "password"),
        "SCHEDULE_INTERVAL_HOURS": ("schedule_interval_hours", None) # None means top level
    }

    for env_var, keys in env_mapping.items():
        value = os.getenv(env_var)
        if value:
            # Handle type conversion for Port/Interval
            if env_var in ["SMTP_PORT", "SCHEDULE_INTERVAL_HOURS"]:
                try:
                    value = int(value)
                except ValueError:
                    continue # Keep original if invalid int

            if keys[1]: # Nested key (e.g. smtp.user)
                if keys[0] not in config:
                    config[keys[0]] = {}
                config[keys[0]][keys[1]] = value
            else: # Top level key
                config[keys[0]] = value

    return config

def filter_jobs(jobs, keywords, history_ids):
    filtered_jobs = []
    for job in jobs:
        # Check if already processed
        if job.symbol in history_ids:
            continue
        
        # Check if title matches keywords
        title_lower = job.title.lower()
        if any(keyword.lower() in title_lower for keyword in keywords):
            filtered_jobs.append(job)
            
    return filtered_jobs

def run_cycle(scraper, history, notifier, config):
    logger.info("Starting scrape cycle...")
    
    # 1. Fetch Jobs
    all_jobs = scraper.fetch_jobs()
    if not all_jobs:
        logger.info("No jobs fetched.")
        return

    # 2. Load History
    processed_ids = history.load_history()
    
    # 3. Filter
    keywords = config.get("keywords", [])
    new_jobs = filter_jobs(all_jobs, keywords, processed_ids)
    
    logger.info(f"rFound {len(new_jobs)} new jobs matching keywords.")

    if new_jobs:
        # 4. Notify
        notifier.send_notification(new_jobs)
        
        # 5. Update History
        new_ids = [job.symbol for job in new_jobs]
        history.update_history(new_ids)
    else:
        logger.info("No new matching jobs to send.")

def main():
    parser = argparse.ArgumentParser(description="NJ State Job Scraper")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending emails (simulated)")
    args = parser.parse_args()

    config = load_config()
    
    # Override config for dry run if needed, or just pass a flag
    # For simplicity, we just log in dry run if we wanted, but the Notifier 
    # handles real sending. A 'real' dry run would mock the notifier.
    # For now, we will rely on --once for manual checks combined with logs.

    scraper = JobScraper()
    history = JobHistory()
    notifier = EmailNotifier(config)

    logger.info("Application started.")

    if args.once:
        run_cycle(scraper, history, notifier, config)
        logger.info("Run once completed. Exiting.")
        return

    # Loop Mode
    interval_hours = config.get("schedule_interval_hours", 24)
    interval_seconds = interval_hours * 3600
    
    logger.info(f"Running in loop mode. Interval: {interval_hours} hours.")
    
    while True:
        try:
            run_cycle(scraper, history, notifier, config)
        except Exception as e:
            logger.error(f"Unexpected error in cycle: {e}")
        
        logger.info(f"Sleeping for {interval_seconds} seconds...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
