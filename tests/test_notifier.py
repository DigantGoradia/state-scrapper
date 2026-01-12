import pytest
from unittest.mock import Mock, patch, ANY
from src.notifier import EmailNotifier, Job

@pytest.fixture
def mock_config():
    return {
        "recipients": ["test@example.com"],
        "smtp": {
            "server": "smtp.test.com",
            "port": 587,
            "user": "user",
            "password": "pass"
        }
    }

@pytest.fixture
def sample_jobs():
    return [
        Job("M1", "Dev", "Loc1", "http://link1", "01/01/2026", "02/01/2026"),
        Job("M2", "Ops", "Loc2", "http://link2", "01/01/2026", "02/01/2026")
    ]

@patch('src.notifier.smtplib.SMTP')
def test_send_notification_success(mock_smtp_class, mock_config, sample_jobs):
    # Setup Mock
    mock_server = Mock()
    mock_smtp_class.return_value = mock_server
    
    notifier = EmailNotifier(mock_config)
    notifier.send_notification(sample_jobs)

    # Verify SMTP interactions
    mock_smtp_class.assert_called_with("smtp.test.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_with("user", "pass")
    mock_server.sendmail.assert_called_once()
    
    # Check email content was sent
    args, _ = mock_server.sendmail.call_args
    sender, recipients, msg = args
    assert sender == "user"
    assert recipients == ["test@example.com"]
    assert "Subject: NJ State Jobs: 2 New Matching Positions Found" in msg

def test_send_notification_no_jobs(mock_config):
    notifier = EmailNotifier(mock_config)
    
    with patch('src.notifier.smtplib.SMTP') as mock_smtp:
        notifier.send_notification([])
        mock_smtp.assert_not_called()

def test_send_notification_bad_config(sample_jobs):
    bad_config = {"recipients": [], "smtp": {}}
    notifier = EmailNotifier(bad_config)
    
    with patch('src.notifier.smtplib.SMTP') as mock_smtp:
        notifier.send_notification(sample_jobs)
        mock_smtp.assert_not_called()
