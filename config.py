import os
from dotenv import load_dotenv

load_dotenv()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")

# Gmail config
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
STOCK_OWNER_EMAIL = os.getenv("STOCK_OWNER_EMAIL")
