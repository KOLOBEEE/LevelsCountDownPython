import threading
import scheduler
import csv
from colorama import Fore, Style
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now get the environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
STOCK_OWNER_EMAIL = os.getenv("STOCK_OWNER_EMAIL")

# Print to verify they're loaded
print("Twilio SID:", TWILIO_ACCOUNT_SID)
print("Email Address:", EMAIL_ADDRESS)


def load_items(filename):
    # ... your existing code unchanged ...
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        items = []
        for row in reader:
            cleaned_row = {k.strip(): v.strip() for k, v in row.items() if k and v}
            items.append(cleaned_row)
        return items

# ... other existing functions unchanged ...


def main():
    # Start the scheduler thread here so it runs alongside your app
    def start_scheduler():
        scheduler.schedule_progress_reports()

    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    filename = "XshopItems.txt"
    items = load_items(filename)
    cart = []

    print("Welcome to X Store!")

    while True:
        # ... your existing main loop code unchanged ...
        print_inventory(items)
        choice = input("What would you like to buy? (Enter item name or number, or 'checkout' to finish, 'exit' to quit): ").strip()
        if choice.lower() == 'exit':
            print("Thanks for visiting X Store. Goodbye!")
            break
        elif choice.lower() == 'checkout':
            if not cart:
                print("Your cart is empty.")
                continue
            print("\n--- Your Receipt ---")
            total = 0.0
            for c in cart:
                line_total = float(c['Price']) * c['Quantity']
                total += line_total
                print(f"{c['Quantity']} x {c['Name']} @ R{c['Price']} each = R{line_total:.2f}")
            print(f"Total: R{total:.2f}")
            print("---------------------\n")
            cart.clear()
            save_items(filename, items)
            continue

        item = find_item(items, choice)
        if not item:
            print("Item not found. Try again.")
            continue

        try:
            quantity = int(input(f"How many {item['Name']}s would you like to buy? "))
            if quantity <= 0:
                print("Quantity must be at least 1.")
                continue
        except ValueError:
            print("Please enter a valid number.")
            continue

        available = int(item['Quantity'])
        if quantity > available:
            print(f"Sorry, only {available} left.")
            continue

        found_in_cart = False
        for c in cart:
            if c['Name'] == item['Name']:
                c['Quantity'] += quantity
                found_in_cart = True
                break
        if not found_in_cart:
            cart.append({'Name': item['Name'], 'Price': item['Price'], 'Quantity': quantity})

        item['Quantity'] = str(available - quantity)
        print(f"Added {quantity} {item['Name']}(s) to your cart.")

        remaining = int(item['Quantity'])
        if remaining <= 2:
            send_low_stock_email(item['Name'], remaining)
            send_low_stock_sms(item['Name'], remaining)

            restock = input(f"{item['Name']} is low. Restock? (yes/no): ").strip().lower()
            if restock == 'yes':
                try:
                    restock_amount = int(input("Enter restock quantity: "))
                    if restock_amount > 0:
                        item['Quantity'] = str(remaining + restock_amount)
                        print(f"{item['Name']} now has {item['Quantity']} in stock.")
                    else:
                        print("Restock amount must be positive. Skipping restock.")
                except ValueError:
                    print("Invalid number. Skipping restock.")

        save_items(filename, items)


if __name__ == "__main__":
    main()
