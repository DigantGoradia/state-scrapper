# Software Requirements Specification (SRS)
## NJ State Job Scraper

### 1. Introduction
#### 1.1 Purpose
The purpose of this document is to define the requirements, architecture, and development guidelines for the NJ State Job Scraper application. This system automates the process of monitoring job postings on the NJ Civil Service Commission website and notifying users of relevant opportunities.

#### 1.2 Scope
The application fetches job listings from a public government URL, filters them based on user-defined keywords, and delivers email notifications. It is designed to run in a containerized environment (Docker) on a schedule.

### 2. Functional Requirements
#### 2.1 Scraping Module
- **FRL-01**: The system MUST fetch HTML content from `https://info.csc.nj.gov/jobannouncements/DefaultJobAnnouncement/JobList`.
- **FRL-02**: It MUST extract the following fields for each job: Symbol (ID), Title, Jurisdiction, Issue Date, Closing Date, and Link.
- **FRL-03**: It MUST handle network timeouts and HTTP errors gracefully (logging the error without crashing).

#### 2.2 Filtering Logic
- **FRL-04**: The system MUST accept a list of keywords (e.g., "Analyst") from a configuration source.
- **FRL-05**: It MUST match these keywords case-insensitively against the Job Title.
- **FRL-06**: It MUST define a "Match" as a job that contains at least one configured keyword.

#### 2.3 Notification Module
- **FRL-07**: The system MUST send an email summary of newly identified matches.
- **FRL-08**: It MUST NOT send email notifications if no new matches are found.
- **FRL-09**: It MUST support SMTP configuration (Server, Port, User, Password, TLS).

#### 2.4 Persistence & History
- **FRL-10**: The system MUST maintain a history of processed Job Symbols to prevent duplicate notifications for the same job.
- **FRL-11**: This history MUST be persisted to a JSON file (`data/history.json`) to survive container restarts.

### 3. Non-Functional Requirements
- **NFR-01 (Reliability)**: The system should operate continuously in a Docker container with an uptime goal of 99%.
- **NFR-02 (Maintainability)**: The code must be modular, separating concerns (Scraping, Notification, Storage) into distinct classes.
- **NFR-03 (Configurability)**: All secrets and user preferences must be decoupled from the source code (handled via `config/settings.json`).
- **NFR-04 (Performance)**: The scraping process should be efficient and respectful of the target server (e.g., avoiding rapid-fire requests).

### 4. System Architecture
#### 4.1 High-Level Design
The system follows a modular "Pipeline" architecture:
`Scheduler (Main Loop) -> Scraper -> Filter -> History Check -> Notifier -> Storage Update`

#### 4.2 Component Design
- **`src.scraper.JobScraper`**: Responsible for HTTP requests and HTML parsing. Returns domain objects (`Job`).
- **`src.notifier.EmailNotifier`**: Responsible for formatting HTML emails and managing SMTP connections.
- **`src.storage.JobHistory`**: Responsible for reading/writing the processed ID set.

### 5. Development Guidelines for Future Changes
#### 5.1 Adding New Filters
To add more complex filtering (e.g., by Location):
1. Update `Job` dataclass in `src/scraper.py` to include the new field.
2. Update `filter_jobs` function in `main.py`.
3. Add configuration test cases in `tests/`.

#### 5.2 Supporting New Notification Channels
To add Slack/Discord support:
1. Create a new class (e.g., `SlackNotifier`) in a new file `src/slack_notifier.py`.
2. Ensure it implements a `send_notification(jobs)` method similar to `EmailNotifier`.
3. Update `main.py` to instantiate the new notifier based on config.

#### 5.3 Database Migration
If `history.json` becomes insufficient:
1. Create a new implementation of `JobHistory` (e.g., `SqliteHistory`) in `src/storage.py`.
2. Ensure it implements `load_history` and `update_history`.
3. Swap the class usage in `main.py`.

### 6. Dependency Management
- The project uses **`uv`** for fast package management.
- All dependencies are defined in `pyproject.toml`.
- To add a package: `uv pip install <package>` and update `pyproject.toml`.

