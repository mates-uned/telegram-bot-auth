import random
import hashlib
import os
import logging
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def send_email(to, subject, message):
    logger.info("Sending email to %s...", to)
    server = "smtp.gmail.com"
    port = 587
    username = os.getenv("FROM_EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PWD")

    if not username or not password:
        logger.error("Email credentials are not set.")
        return

    try:
        # Create the email message
        my_message = EmailMessage()
        my_message["From"] = username
        my_message["To"] = to
        my_message["Subject"] = subject
        my_message.set_content(message)

        # Connect to the SMTP server
        with smtplib.SMTP(server, port) as smtp:
            smtp.ehlo()  # Identify with the server
            smtp.starttls()  # Upgrade connection to secure
            smtp.login(username, password)  # Authenticate
            logger.info("Sending email to %s", to)
            smtp.send_message(my_message)  # Send email
            logger.info("Email sent successfully.")
    except smtplib.SMTPException as e:
        logger.error("Failed to send email: %s", e)

def create_access_token():
    access_token = str(random.randint(100000, 999999))
    access_token = hashlib.sha256(access_token.encode('utf-8')).hexdigest()

    return access_token

async def generate_code():
    code = str(random.randint(100000, 999999))
    code_expires_at = datetime.now() + timedelta(minutes=15)
    return code, code_expires_at

def validate_email(email):
    white_list = ["mates.uned.auth@proton.me"]
    if email in white_list:
        return True
    if "@alumno.uned.es" not in email:
        return False
    return True

def codes_match(telegram_id, stored_code, user_input_code):
    user_input_encoding = str(telegram_id) + str(user_input_code)
    stored_code_encoding = str(telegram_id) + str(stored_code)
    user_input_hash = hashlib.sha256(user_input_encoding.encode('utf-8')).hexdigest()
    stored_code_hash = hashlib.sha256(stored_code_encoding.encode('utf-8')).hexdigest()
    if stored_code is None:
        return False
    if user_input_hash == stored_code_hash:
        return True
    return False