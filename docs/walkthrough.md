# NJ State Job Scraper Walkthrough

I have built a modular, Dockerized application to scrape NJ State jobs and email you when matches are found.

## Features Implemented
- **Scraper**: Fetches and parses the NJ CSC job table.
- **Notifier**: Sends HTML emails via SMTP if keywords match.
- **History**: Tracks seen jobs to prevent duplicate alerts.
- **Docker**: Fully containerized with `uv` for dependency management.
- **Tests**: Validated with `pytest`.

## How to Run

### 1. Configure
Edit `config/settings.json`:
```json
{
  "keywords": ["analyst", "developer"],
  "recipients": ["your_email@example.com"],
  "smtp": { ... }
}
```

### 2. Run with Docker (Recommended)
```bash
docker build -t nj-scraper .
docker run -d -v $(pwd)/data:/app/data nj-scraper
```

### 3. Run Locally with uv
```bash
# Install dependencies
uv venv
uv pip install -r pyproject.toml

# Run
python main.py
```
To run once immediately: `python main.py --once`

## Verification Results
- **Unit Tests**: `pytest` passed for scraper parsing and email logic.
- **Dependency Management**: `uv` successfully resolves and installs packages.

## Next Steps
- Add your real SMTP credentials to `config/settings.json`.
- Schedule the container or script to run if not using the loop mode.
