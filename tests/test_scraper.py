from unittest.mock import Mock, patch

import pytest
import requests

from src.scraper import JobScraper


@pytest.fixture
def mock_html():
    """Returns sample HTML content for testing."""
    return """
    <html>
        <body>
            <table id="RecordsSearched">
                <tbody>
                    <tr>
                        <td><a href="/ViewJob?id=123">View</a></td>
                        <td>M1234</td>
                        <td>Software Developer</td>
                        <td>Trenton</td>
                        <td>Dept of Tech</td>
                        <td>Residents</td>
                        <td>01/01/2026</td>
                        <td>01/31/2026</td>
                    </tr>
                    <tr>
                        <td><a href="/ViewJob?id=456">View</a></td>
                        <td>P5678</td>
                        <td>Systems Analyst</td>
                        <td>Newark</td>
                        <td>Dept of Labor</td>
                        <td>Residents</td>
                        <td>01/05/2026</td>
                        <td>02/15/2026</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """


@patch("src.scraper.requests.get")
def test_fetch_jobs_success(mock_get, mock_html):
    """Tests successful job fetching and parsing."""
    # Setup mock
    mock_response = Mock()
    mock_response.content = mock_html
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Execute
    scraper = JobScraper()
    jobs = scraper.fetch_jobs()

    # Verify
    assert len(jobs) == 2

    job1 = jobs[0]
    assert job1.symbol == "M1234"
    assert job1.title == "Software Developer"
    assert job1.jurisdiction == "Trenton"
    assert job1.closing_date == "01/31/2026"
    assert "ViewJob?id=123" in job1.link

    job2 = jobs[1]
    assert job2.symbol == "P5678"
    assert job2.title == "Systems Analyst"


@patch("src.scraper.requests.get")
def test_fetch_jobs_failure(mock_get):
    """Tests handling of request exceptions."""
    # Setup mock to raise error
    mock_get.side_effect = requests.RequestException("Connection Error")

    # Execute
    scraper = JobScraper()
    jobs = scraper.fetch_jobs()

    # Verify handles error gracefully
    assert jobs == []


@patch("src.scraper.requests.get")
def test_fetch_jobs_no_table(mock_get):
    """Tests handling of pages with no job table."""
    # Setup mock with empty HTML
    mock_response = Mock()
    mock_response.content = "<html><body></body></html>"
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Execute
    scraper = JobScraper()
    jobs = scraper.fetch_jobs()

    # Verify
    assert jobs == []
