from app_password import password, sender, receiver
from email.message import EmailMessage
import ssl
import smtplib
import time
from datetime import datetime
import random
import logging

# Configuration
TOTAL_EMAILS = 50
TOTAL_TIME_MINUTES = 10
MIN_DELAY = (TOTAL_TIME_MINUTES * 60) / TOTAL_EMAILS  # Average delay between sends

# Logging setup
logging.basicConfig(
    filename='mails.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

email_sender = sender
email_password = password
email_receiver = receiver


def create_email():
    """Generates a complex test email for search-bar or ticketing system testing."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    subject = subject = f"""[Ticket: DTB001070] Category: IT Support | Status: Open | Created: 2025-01-01 | By: user@example.com | Notes: System crash at 3AM - error_code=502 | Assigned To: John O'Neil | Priority: High | Tags: [urgent, prod, server] | SLA < 5min | TestID: {datetime.now().strftime('%Y%m%d-%H%M%S')}"""


    body = f"""\
Test Email for Search Bar Evaluation
Timestamp: {datetime.now().isoformat()}
Test ID: {timestamp}
"""

    msg = EmailMessage()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.set_content(body)

    return msg


def send_email(message):
    """Sends an email using SMTP over SSL with error handling."""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(message)
        return True
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        return False


def main():
    """Main routine to send multiple emails over a time window with logging and throttling."""
    logging.info(f"📤 Starting email test: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes.")
    
    successful = 0
    failed = 0
    start = time.time()

    for i in range(TOTAL_EMAILS):
        email = create_email()
        result = send_email(email)

        if result:
            successful += 1
            logging.info(f"✅ Sent {i+1}/{TOTAL_EMAILS}")
        else:
            failed += 1
            logging.warning(f"❌ Failed {i+1}/{TOTAL_EMAILS}")

        # Check if time is up
        elapsed = time.time() - start
        if elapsed >= TOTAL_TIME_MINUTES * 60:
            logging.warning("⏱️ Time limit reached. Stopping early.")
            break

        # Sleep if not last iteration
        if i < TOTAL_EMAILS - 1:
            jitter = MIN_DELAY * (0.8 + random.random() * 0.4)
            time.sleep(jitter)

    total_time = time.time() - start
    avg = total_time / successful if successful > 0 else 0

    logging.info(f"""
📊 Email Test Summary:
Total runtime: {total_time:.2f}s
Emails Sent: {successful}
Failures: {failed}
Average Interval: {avg:.2f}s
""")


if __name__ == "__main__":
    main()
