import argparse
import logging
import os
import sys
import time

from dotenv import load_dotenv

from .notifier import EmailNotifier

# Relative imports for package execution
from .scraper import JobScraper
from .storage import JobHistory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def load_config() -> dict:
    """Loads configuration from environment variables."""
    config = {}

    # SMTP Configuration
    config["smtp"] = {
        "server": os.getenv("SMTP_SERVER"),
        "port": int(os.getenv("SMTP_PORT", 587)),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
    }

    # Application Settings
    config["schedule_interval_hours"] = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 24))

    recipients_str = os.getenv("RECIPIENTS", "")
    config["recipients"] = [
        email.strip() for email in recipients_str.split(",") if email.strip()
    ]

    keywords_str = os.getenv("KEYWORDS", "analyst,developer,engineer")
    config["keywords"] = [kw.strip() for kw in keywords_str.split(",") if kw.strip()]

    return config


def filter_jobs(jobs, keywords, history_ids):
    """Filters jobs based on keywords and processing history."""
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
    """Runs a single scraping and notification cycle."""
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

    logger.info(f"Found {len(new_jobs)} new jobs matching keywords.")

    if new_jobs:
        # 4. Notify
        notifier.send_notification(new_jobs)

        # 5. Update History
        new_ids = [job.symbol for job in new_jobs]
        history.update_history(new_ids)
    else:
        logger.info("No new matching jobs to send.")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="NJ State Job Scraper")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without sending emails (simulated)"
    )
    args = parser.parse_args()

    config = load_config()

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


def dry_run():
    """Entry point for `uv run dry-run`.

    Simulates: python main.py --once --dry-run
    """
    # Simulate arguments
    sys.argv = ["main.py", "--once", "--dry-run"]
    main()


if __name__ == "__main__":
    main()
