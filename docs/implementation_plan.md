# NJ State Job Scraper Implementation Plan

## Goal Description
Build a modular, Dockerized Python application to scrape the NJ Civil Service Commission job list daily and email subscribers when new jobs matching specific keywords are found.

## User Review Required
> [!IMPORTANT]
> **SMTP Configuration**: The system uses a `Context` object or environment variables/config file for SMTP settings. You must update `config/settings.json` (or `.env`) with your actual credentials.
>
> **Docker**: The application runs in a container. Ensure you have Docker Installed.

## Proposed Changes

### Project Structure
We will adopt a modular structure in `d:/projects/state-scrapper`:

```text
nj_scraper/
├── config/
│   ├── settings.json         # User Config (Keywords, SMTP placeholder)
│   └── __init__.py
├── src/
│   ├── __init__.py
│   ├── scraper.py            # Scraper logic
│   ├── notifier.py           # Email logic
│   ├── storage.py            # History/Persistence logic
│   └── utils.py              # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   └── test_notifier.py
├── main.py                   # Entry point (Scheduling loop)
├── Dockerfile
├── requirements.txt
└── README.md
```

### Modules

#### [NEW] [config/settings.json](file:///d:/projects/state-scrapper/nj_scraper/config/settings.json)
Contains keywords and SMTP config.
```json
{
  "keywords": ["analyst", "developer"],
  "recipients": ["user@example.com"],
  "smtp": {
    "server": "smtp.example.com",
    "port": 587,
    "user": "replace_me",
    "password": "replace_me"
  },
  "schedule_interval_hours": 24
}
```

#### [NEW] [src/scraper.py](file:///d:/projects/state-scrapper/nj_scraper/src/scraper.py)
Class `JobScraper`
- `fetch_jobs()`: Returns list of `Job` data classes/dicts.
- Handles parsing of the HTML table using `BeautifulSoup`.

#### [NEW] [src/notifier.py](file:///d:/projects/state-scrapper/nj_scraper/src/notifier.py)
Class `EmailNotifier`
- `send_notification(jobs)`: Composes HTML email.
- Uses `smtplib`. designed to be loosely coupled (accepts config object).

#### [NEW] [src/storage.py](file:///d:/projects/state-scrapper/nj_scraper/src/storage.py)
Class `JobHistory`
- `load_history()`: Reads processed IDs.
- `save_history(ids)`: Appends new IDs.
- Stores data in `data/history.json` (mounted volume in Docker).

#### [NEW] [main.py](file:///d:/projects/state-scrapper/nj_scraper/main.py)
- Loads config.
- Instantiates Scraper, Notifier, Storage.
- Enters `while True` loop with `sleep` (for Docker daemon mode) OR runs once if flag provided.

#### [NEW] [Dockerfile](file:///d:/projects/state-scrapper/nj_scraper/Dockerfile)
- Python 3.9-slim base.
- Installs requirements.
- CMD `["python", "main.py"]`

#### [NEW] [tests/test_scraper.py](file:///d:/projects/state-scrapper/nj_scraper/tests/test_scraper.py)
- Uses `pytest`.
- Mocks HTML response to verify parsing logic.

## Verification Plan

### Automated Tests
- Run `pytest` via `uv` to verify scraping parsing and logic correctness.
  ```bash
  # Install dependencies into venv
  python -m uv venv
  python -m uv pip install -p .venv -r pyproject.toml
  python -m uv pip install -p .venv pytest
  
  # Run tests
  .\.venv\Scripts\pytest
  ```

### Manual Verification
1. **Build Docker Image**: `docker build -t nj-scraper .`
2. **Run Container**: `docker run -v $(pwd)/data:/app/data nj-scraper`
3. **Check Logs**: Verify it fetches, finds (or doesn't find) jobs, and sleeps.
