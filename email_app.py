from app_password import password
from email.message import EmailMessage
import ssl
import smtplib


#Global variables
email_sender = 'bransonallan@gmail.com'

email_password = password
# nprint(email_password)

email_receiver = 'dtb.cards@calltronix.com'

subject = "This is a test Email"
body = """
The Script Worked!!
"""

#Create anm instance of the email liblary
em = EmailMessage()
em['FROM'] = email_sender
em['To'] = email_receiver
em['subject'] = subject
em.set_content(body)

try:
    #Set Context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
    print('Email was sent')
except Exception as e:
    print('Could not send email: ', e)




