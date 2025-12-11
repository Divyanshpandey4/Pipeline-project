# streamlit_app/emailer.py
import os
import logging
from typing import List

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  # or any email API
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")

logging.basicConfig(level=logging.INFO)

def send_email(to_emails: List[str], subject: str, content: str):
    api_key = SENDGRID_API_KEY
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY not set")
    # Example using requests to SendGrid v3
    import requests
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
      "personalizations": [{"to": [{"email": e} for e in to_emails], "subject": subject}],
      "from": {"email": FROM_EMAIL},
      "content": [{"type": "text/plain", "value": content}]
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    logging.info("Email sent to %s", to_emails)
