# progress_report.py

from twilio.rest import Client
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

# Environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")        
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")   

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
STOCK_OWNER_EMAIL = os.getenv("STOCK_OWNER_EMAIL")

def send_progress_report():
    # Customize your progress report message here
    subject = "Your Scheduled Progress Report"
    body = "Hello! Here's your breathing app progress update for today."

    # Send Email
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS  # or whoever should get it
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(Fore.CYAN + "Progress report email sent successfully." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send progress report email: {e}" + Style.RESET_ALL)

    # Send SMS
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=OWNER_PHONE_NUMBER
        )
        print(Fore.CYAN + "Progress report SMS sent successfully." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send progress report SMS: {e}" + Style.RESET_ALL)
