from app_password import password, sender, receiver
from email.message import EmailMessage
import ssl
import smtplib
import time
from datetime import datetime
import random
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configuration
TOTAL_EMAILS = 20
TOTAL_TIME_MINUTES = 5
MIN_DELAY = (TOTAL_TIME_MINUTES * 60) / TOTAL_EMAILS  # Delay in seconds
MAX_CONCURRENT_SENDS = 5  # Limit parallel threads

# Logging setup
logging.basicConfig(
    filename='parrarelMail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

email_sender = sender
email_password = password
email_receiver = receiver

def create_email():
    """Generates a test email with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    subject = f"Test Mail"
    body = f"""
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

def send_email_sync(message):
    """Blocking email send function."""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(message)
        return True
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        return False

async def send_email_async(i, executor):
    """Async wrapper for sending an email with jitter delay."""
    email = create_email()
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, send_email_sync, email)

    if result:
        logging.info(f"✅ Sent {i+1}/{TOTAL_EMAILS}")
        print(f"✅ Sent {i+1}/{TOTAL_EMAILS}")
    else:
        logging.warning(f"❌ Failed {i+1}/{TOTAL_EMAILS}")
        print(f"❌ Failed {i+1}/{TOTAL_EMAILS}")

    # Delay with jitter
    jitter = MIN_DELAY * (0.8 + random.random() * 0.4)
    await asyncio.sleep(jitter)

async def main():
    logging.info(f"📤 Starting async email test: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes.")
    print(f"📤 Starting async email test: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes.")

    start = time.time()
    executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SENDS)

    tasks = [
        asyncio.create_task(send_email_async(i, executor))
        for i in range(TOTAL_EMAILS)
    ]

    await asyncio.gather(*tasks)

    total_time = time.time() - start
    logging.info(f"📊 Completed. Total time: {total_time:.2f}s")
    print(f"📊 Completed. Total time: {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
