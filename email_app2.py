from app_password import password
from app_password import sender
from app_password import receiver

from email.message import EmailMessage
import ssl
import smtplib
import time
from datetime import datetime
import random
import logging

# Set up logging
logging.basicConfig(
    filename='mails.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global variables
email_sender = sender
email_password = password
email_receiver = receiver

# Research parameters
TOTAL_EMAILS = 50
TOTAL_TIME_MINUTES = 10
MIN_DELAY = (TOTAL_TIME_MINUTES * 60) / TOTAL_EMAILS  # Average delay needed between emails


def create_email():
    """Create an email message with timestamp for research tracking"""
    subject = f"Email Test #{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    body = f"""
    Research Email Sent
    Timestamp: {datetime.now().isoformat()}
    Test Number: {datetime.now().strftime('%Y%m%d-%H%M%S')}
    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    return em


def send_email(em):
    """Send a single email with error handling"""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False


def main():
    """Main research execution with rate limiting and monitoring"""
    logging.info(f"Starting email research test - Target: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes")

    successful_sends = 0
    failed_sends = 0
    start_time = time.time()

    for i in range(TOTAL_EMAILS):
        # Add some randomness to delays to appear more natural
        delay = MIN_DELAY * (0.8 + random.random() * 0.4)

        # Create and send email
        em = create_email()
        if send_email(em):
            successful_sends += 1
            logging.info(f"Successfully sent email {i + 1}/{TOTAL_EMAILS}")
        else:
            failed_sends += 1
            logging.warning(f"Failed to send email {i + 1}/{TOTAL_EMAILS}")

        # Check if we're still within our time window
        elapsed_time = time.time() - start_time
        if elapsed_time >= TOTAL_TIME_MINUTES * 60:
            logging.warning("Time window exceeded, stopping email sends")
            break

        # Sleep for the calculated delay if not the last email
        if i < TOTAL_EMAILS - 1:
            time.sleep(delay)

    # Log final statistics
    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"""
    Research Complete:
    Total time: {total_time:.2f} seconds
    Successful sends: {successful_sends}
    Failed sends: {failed_sends}
    Average interval: {total_time / successful_sends:.2f} seconds
    """)


if __name__ == "__main__":
    main()
