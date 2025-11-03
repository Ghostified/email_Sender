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
import uuid
import os
import email.utils

# Configuration
TOTAL_EMAILS = 15
TOTAL_TIME_MINUTES = 1
MIN_DELAY = (TOTAL_TIME_MINUTES * 60) / TOTAL_EMAILS  # Delay in seconds
MAX_CONCURRENT_SENDS = 5  # Limit parallel threads

# Email Config
email_sender = sender
email_password = password
email_receiver = receiver
email_cc = ["bransontechnologies@outlook.com"]  # Optional: set to [] to disable CC

# Attachments (paths to files relative to script)
original_attachments = ["Email Attachments/600-kb.jpg"]  # Add paths like ["file1.pdf", "image.png"]
reply_attachments = ["Email Attachments/file_example_PPT_250kB.ppt"]  # Attachments for replies

# Track sent message IDs for later reply
sent_messages = []

# Logging setup
logging.basicConfig(
    filename='parrarelMail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_unique_subject():
    """Generate a unique subject for each test email."""
    rand_id = uuid.uuid4().hex[:6].upper()
    return f"Test Mail [{rand_id}] - {datetime.now().strftime('%H:%M:%S')}"


def create_email_with_attachment(subject=None, body=None, attachments=None):
    """Create an email with unique Message-ID and optional attachments."""
    if subject is None:
        subject = generate_unique_subject()
    if body is None:
        body = f"""
        Test Email for Search Bar Evaluation
        Timestamp: {datetime.now().isoformat()}
        Subject ID: {subject}
        """
    if attachments is None:
        attachments = []

    msg = EmailMessage()
    
    # ✅ Manually set Message-ID before sending
    msg_id = email.utils.make_msgid(domain="gmail.com")  # e.g. <uuid@domain>
    msg['Message-ID'] = msg_id

    msg['From'] = email_sender
    msg['To'] = email_receiver
    if email_cc:
        msg['Cc'] = ", ".join(email_cc)
    msg['Subject'] = subject
    msg.set_content(body)

    # Add attachments
    for path in attachments:
        if not os.path.isfile(path):
            logging.warning(f"Attachment not found: {path}")
            print(f"⚠️ Attachment not found: {path}")
            continue
        with open(path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(path)
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
            logging.info(f"📎 Attached: {file_name}")

    return msg, subject, msg_id  # <-- Return the generated msg_id

def send_email_sync(message):
    """Blocking send function. Returns True on success."""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(message)
        return True  # We already set Message-ID, so success = trust it
    except Exception as e:
        logging.error(f"Email send failed: {e}")
        return False

async def send_email_async(i, executor):
    """Send one email with jitter delay and track our own Message-ID."""
    try:
        # Now we get the pre-generated msg_id
        email_msg, subject, msg_id = create_email_with_attachment(attachments=original_attachments)
        loop = asyncio.get_running_loop()
        
        # Send the message
        result = await loop.run_in_executor(executor, send_email_sync, email_msg)

        # ✅ If send was successful, use our pre-generated msg_id to track
        if result is not False:  # i.e., no exception
            logging.info(f"✅ Sent {i+1}/{TOTAL_EMAILS} | Subject: {subject} | Msg-ID: {msg_id}")
            print(f"✅ Sent {i+1}/{TOTAL_EMAILS}")
            sent_messages.append({'msg_id': msg_id, 'subject': subject})
        else:
            logging.warning(f"❌ Failed to send {i+1}/{TOTAL_EMAILS} | Subject: {subject}")
            print(f"❌ Failed {i+1}/{TOTAL_EMAILS}")

    except Exception as e:
        logging.error(f"❌ Exception during send {i+1}: {e}")
        print(f"❌ Error sending {i+1}: {e}")

    # Jitter delay
    jitter = MIN_DELAY * (0.8 + random.random() * 0.4)
    await asyncio.sleep(jitter)

def create_reply_email(original_msg_id, original_subject, attachments=None):
    """Create a reply with In-Reply-To and optional attachments."""
    if not original_subject.startswith("Re:"):
        reply_subject = f"Re: {original_subject}"
    else:
        reply_subject = original_subject

    body = f"""
    This is an automated bulk reply to your test email.

    Original Subject: {original_subject}
    Auto-reply Timestamp: {datetime.now().isoformat()}

    Best regards,
    Auto-Responder
    """

    msg = EmailMessage()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    if email_cc:
        msg['Cc'] = ", ".join(email_cc)
    msg['Subject'] = reply_subject
    msg['In-Reply-To'] = original_msg_id
    msg['References'] = original_msg_id
    msg.set_content(body)

    # Add reply attachments
    if attachments:
        for path in attachments:
            if not os.path.isfile(path):
                logging.warning(f"Reply attachment not found: {path}")
                continue
            with open(path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
                logging.info(f"📎 Reply attached: {file_name}")

    return msg

async def send_bulk_replies(executor):
    """After sending originals, prompt user and send bulk replies."""
    if not sent_messages:
        print("📭 No successful emails to reply to.")
        logging.info("📭 No emails sent successfully. Skipping replies.")
        return

    print("\n" + "="*50)
    print("📬 All emails sent! Do you want to send bulk replies? (y/n): ", end="")
    choice = input().strip().lower()

    if choice not in ['y', 'yes']:
        print("⏭️ Skipping replies.")
        logging.info("⏭️ User skipped bulk reply.")
        return

    print("📤 Sending bulk replies...")
    logging.info(f"📤 Sending bulk replies to {len(sent_messages)} emails...")

    reply_tasks = []
    for i, msg_info in enumerate(sent_messages):
        reply_msg = create_reply_email(msg_info['msg_id'], msg_info['subject'], reply_attachments)
        task = asyncio.get_running_loop().run_in_executor(executor, send_email_sync, reply_msg)
        reply_tasks.append(task)

        # Optional: small delay between replies
        if i % 5 == 0:
            await asyncio.sleep(0.5)

    results = await asyncio.gather(*reply_tasks, return_exceptions=True)

    replied = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f"❌ Reply failed for {sent_messages[i]['subject']}: {result}")
        else:
            logging.info(f"📨 Replied to {sent_messages[i]['subject']} | Msg-ID: {result}")
            replied += 1

    print(f"📨 Bulk replies completed. {replied}/{len(sent_messages)} replies sent.")
    logging.info(f"📨 Bulk replies completed: {replied}/{len(sent_messages)}")

async def main():
    logging.info(f"📤 Starting email test: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes.")
    print(f"📤 Starting email test: {TOTAL_EMAILS} emails over {TOTAL_TIME_MINUTES} minutes.")

    start = time.time()
    executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SENDS)

    # Step 1: Send original emails
    tasks = [send_email_async(i, executor) for i in range(TOTAL_EMAILS)]
    await asyncio.gather(*tasks)

    total_send_time = time.time() - start
    logging.info(f"📧 Sent {len(sent_messages)} out of {TOTAL_EMAILS} emails in {total_send_time:.2f}s")
    print(f"📧 Sent {len(sent_messages)}/{TOTAL_EMAILS} emails in {total_send_time:.2f}s")

    # Step 2: Prompt for bulk reply
    await send_bulk_replies(executor)

    executor.shutdown(wait=True)
    total_time = time.time() - start
    logging.info(f"✅ Full process completed in {total_time:.2f}s")
    print(f"✅ Done in {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())