import json
import os
from twilio.rest import Client
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
STOCK_OWNER_EMAIL = os.getenv("STOCK_OWNER_EMAIL")

def load_inventory(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_inventory(file_path, inventory):
    with open(file_path, 'w') as f:
        json.dump(inventory, f, indent=4)

def send_low_stock_email(name, quantity):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Low Stock Alert: {name}"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = STOCK_OWNER_EMAIL
        msg.set_content(f"Stock Alert: Only {quantity} {name}(s) left in store.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(Fore.CYAN + "Low stock email sent." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send email: {e}" + Style.RESET_ALL)

def send_low_stock_sms(name, quantity):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        body = f"Stock Alert: Only {quantity} {name}(s) left."
        client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=OWNER_PHONE_NUMBER
        )
        print(Fore.CYAN + "Low stock SMS sent." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send SMS: {e}" + Style.RESET_ALL)
