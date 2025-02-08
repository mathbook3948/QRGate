import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os

load_dotenv()

def send_email(title, message, target):
    msg = MIMEText(message)
    msg["Subject"] = title
    msg["From"] = os.getenv("sender_email")
    msg["To"] = target

    with smtplib.SMTP_SSL(os.getenv("smtp_server"), int(os.getenv("smtp_port"))) as server:
        server.login("mathbook3948", os.getenv("sender_password"))
        server.sendmail(os.getenv("sender_email"), target, msg.as_string())
