import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from .scraper import Job


class EmailNotifier:
    """Manages email notifications for new jobs."""

    def __init__(self, config: dict[str, Any]):
        """Initializes the notifier with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

    def send_notification(self, new_jobs: list[Job]):
        """Sends an HTML email with the list of new jobs."""
        if not new_jobs:
            self.logger.info("No new jobs to notify about.")
            return

        sender_email = self.config.get("smtp", {}).get("user")
        sender_password = self.config.get("smtp", {}).get("password")
        smtp_server = self.config.get("smtp", {}).get("server")
        smtp_port = self.config.get("smtp", {}).get("port")
        recipients = self.config.get("recipients", [])

        if not all([sender_email, sender_password, smtp_server, recipients]):
            self.logger.error("Missing SMTP configuration. Cannot send email.")
            return

        subject = f"NJ State Jobs: {len(new_jobs)} New Matching Positions Found"

        # Build HTML Body
        html_body = self._build_html_body(new_jobs)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        try:
            self.logger.info(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
            server.quit()
            self.logger.info(f"Notification sent to {recipients}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")

    def _build_html_body(self, jobs: list[Job]) -> str:
        style = "text-align: left; padding: 8px; border: 1px solid #ddd;"
        rows = ""
        for job in jobs:
            rows += f"""
            <tr>
                <td style="{style}">{job.symbol}</td>
                <td style="{style}">{job.title}</td>
                <td style="{style}">{job.jurisdiction}</td>
                <td style="{style}">{job.closing_date}</td>
                <td style="{style}">
                    <a href="{job.link}">Link</a>
                </td>
            </tr>
            """

        return f"""
        <html>
        <body>
            <h2>New Matching Jobs Found</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="{style}">Symbol</th>
                        <th style="{style}">Title</th>
                        <th style="{style}">
                            Location
                        </th>
                        <th style="{style}">
                            Closing
                        </th>
                        <th style="{style}">
                            Link
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </body>
        </html>
        """
