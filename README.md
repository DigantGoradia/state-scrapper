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
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   # OR on Windows PowerShell
   Copy-Item .env.example .env
   ```
2. Edit `.env` with your details:
   - `SMTP_*`: Your email provider details.
   - `RECIPIENTS`: Comma-separated list of email addresses.
   - `KEYWORDS`: Comma-separated list of job titles to search for.
   - `SCHEDULE_INTERVAL_HOURS`: How often to check for jobs (in hours).

### 2. Docker Usage (Recommended)

**Build the image:**
```bash
docker build -t nj-scraper .
```

**Run the container:**
Mount the `data` directory to persist the job history `json` file.
```bash
docker run -d --name nj-scraper -v $(pwd)/data:/app/data --env-file .env nj-scraper
```

### 3. Manual Usage with uv

**Install uv (globally):**
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

**Install dependencies:**
```bash
uv sync
```

**Run the script:**
```bash
uv run python -m src.main
```

**Run Once (Dry Run):**
Use the convenient alias to run a single check without sending actual emails (emails will be logged to console).
```bash
uv run dry-run
```
Alternatively:
```bash
uv run python -m src.main --once --dry-run
```

## Testing
Run unit tests:
```bash
pytest
```

## Development

### Pre-commit Hooks
This project uses `pre-commit` to enforce code quality before every commit.
1. Install pre-commit:
   ```bash
   pip install pre-commit
   # OR with uv
   uv pip install pre-commit
   ```
2. Install the git hooks:
   ```bash
   pre-commit install
   ```
Now, linting and formatting checks will run automatically on `git commit`.

### Code Quality (Ruff)
We use `ruff` for linting, formatting, and import sorting.
- **Run Linting**: `uv run ruff check .`
- **Run Formatting**: `uv run ruff format .`

## CI/CD
This project uses GitHub Actions to automatically:
- Lint and Check Formatting (using Ruff)
- Verify Docker Build

