import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Job:
    """Represents a single job posting."""

    symbol: str  # ID
    title: str
    jurisdiction: str
    link: str
    issue_date: str
    closing_date: str


class JobScraper:
    """Scrapes job listings from the NJ CSC website."""

    BASE_URL = "https://info.csc.nj.gov"
    JOB_LIST_URL = (
        "https://info.csc.nj.gov/jobannouncements/DefaultJobAnnouncement/JobList"
    )

    def __init__(self):
        """Initializes the scraper."""
        self.logger = logging.getLogger(__name__)

    def fetch_jobs(self) -> list[Job]:
        """Fetches job list and parses the results."""
        self.logger.info("Fetching job list...")
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
            response = requests.get(self.JOB_LIST_URL, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch job list: {e}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")

        # The table has ID "RecordsSearched"
        table = soup.find("table", {"id": "RecordsSearched"})
        if not table:
            self.logger.error("Could not find job table with id 'RecordsSearched'")
            return []

        jobs = []
        # Skip header if it exists (usually tbody tr are data, thead has header)
        # We target tbody rows directly
        rows = table.select("tbody tr")

        self.logger.info(f"Found {len(rows)} rows in job table.")

        for row in rows:
            try:
                cols = row.find_all("td")
                if len(cols) < 8:
                    continue

                # Parse columns based on research
                # Col 0: Link (contains <a>)
                # Col 1: Symbol/ID
                # Col 2: Title
                # Col 3: Jurisdiction
                # Col 6: Issue Date
                # Col 7: Closing Date

                link_tag = cols[0].find("a")
                relative_link = link_tag["href"] if link_tag else ""
                full_link = f"{self.BASE_URL}{relative_link}" if relative_link else ""

                symbol = cols[1].get_text(strip=True)
                title = cols[2].get_text(strip=True)
                jurisdiction = cols[3].get_text(strip=True)
                issue_date = cols[6].get_text(strip=True)
                closing_date = cols[7].get_text(strip=True)

                job = Job(
                    symbol=symbol,
                    title=title,
                    jurisdiction=jurisdiction,
                    link=full_link,
                    issue_date=issue_date,
                    closing_date=closing_date,
                )
                jobs.append(job)

            except Exception as e:
                self.logger.warning(f"Error parsing row: {e}")
                continue

        self.logger.info(f"Successfully parsed {len(jobs)} jobs.")
        return jobs
