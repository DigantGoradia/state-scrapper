# NJ State Job Scraper

A modular, Dockerized Python application to scrape the NJ Civil Service Commission job list daily and email subscribers when new jobs matching specific keywords are found.

## Features
- **Daily Scraping**: Checks for new job postings every 24 hours (configurable).
- **Keyword Filtering**: Only alerts for jobs matching your interests.
- **Email Notifications**: Sends an HTML summary of new jobs.
- **Docker Support**: Runs in a lightweight container.
- **History Tracking**: Avoids sending duplicate alerts for the same job.

## Setup

### 1. Configuration
Edit `config/settings.json` with your details:
- `keywords`: List of job titles to search for.
- `recipients`: List of email addresses to notify.
- `smtp`: Your email provider details (e.g., Gmail App Password).

### 2. Docker Usage (Recommended)

**Build the image:**
```bash
docker build -t nj-scraper .
```

**Run the container:**
Mount the `data` directory to persist the job history `json` file.
```bash
docker run -d --name nj-scraper -v $(pwd)/data:/app/data nj-scraper
```

### 3. Manual Usage with uv

**Install uv (if not installed):**
```bash
pip install uv
```

**Install dependencies:**
```bash
uv pip install -r pyproject.toml
# OR if you want to create a venv and sync
uv venv
uv pip install -r pyproject.toml
```

**Run the script:**
```bash
python main.py
```
To run once (no loop):
```bash
python main.py --once
```

## Testing
Run unit tests:
```bash
pytest
```
