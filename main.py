import csv
import json
import os
import threading
import scheduler
from colorama import Fore, Style
from twilio.rest import Client
from email.message import EmailMessage
from dotenv import load_dotenv
import smtplib

# Load environment variables
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
STOCK_OWNER_EMAIL = os.getenv("STOCK_OWNER_EMAIL")

# Convert CSV to JSON
def convert_csv_to_json(csv_file, json_file):
    items = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {
                'Name': row['Name'],
                'Price': float(row['Price']),
                'Quantity': int(row['Quantity'])
            }
            items.append(item)

    with open(json_file, 'w') as f:
        json.dump(items, f, indent=4)

# Load items from JSON
def load_items(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

# Save items back to JSON
def save_items(json_file, items):
    with open(json_file, 'w') as f:
        json.dump(items, f, indent=4)

# Find an item by number or name
def find_item(items, choice):
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
    else:
        for item in items:
            if item['Name'].lower() == choice.lower():
                return item
    return None

# Display inventory with color-coded stock levels
def print_inventory(items):
    print("\nAvailable Inventory:")
    for idx, item in enumerate(items, start=1):
        quantity = item['Quantity']
        if quantity > 4:
            color = Fore.GREEN
        elif 2 <= quantity <= 4:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        print(f"{idx}. {item['Name']} - R{item['Price']} ({color}{quantity} in stock{Style.RESET_ALL})")

# Email alert
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

# SMS alert
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

def main():
    # Start scheduler
    def start_scheduler():
        scheduler.schedule_progress_reports()
    threading.Thread(target=start_scheduler, daemon=True).start()

    # File paths
    csv_file = "XshopItems.txt"
    json_file = "XshopItems.json"

    # Convert if JSON doesn't exist yet
    if not os.path.exists(json_file):
        convert_csv_to_json(csv_file, json_file)

    # Load items
    items = load_items(json_file)
    cart = []

    print("Welcome to X Store!")

    while True:
        print_inventory(items)
        choice = input("\nEnter item number or name ('checkout' or 'exit'): ").strip()
        if choice.lower() == 'exit':
            print("Thank you for shopping with us!")
            break
        elif choice.lower() == 'checkout':
            if not cart:
                print("Your cart is empty.")
                continue
            print("\n--- Receipt ---")
            total = 0
            for c in cart:
                line_total = c['Price'] * c['Quantity']
                total += line_total
                print(f"{c['Quantity']} x {c['Name']} @ R{c['Price']} = R{line_total:.2f}")
            print(f"Total: R{total:.2f}\n----------------\n")
            cart.clear()
            save_items(json_file, items)
            continue

        item = find_item(items, choice)
        if not item:
            print("Item not found.")
            continue

        try:
            quantity = int(input(f"How many {item['Name']}s? "))
            if quantity <= 0:
                print("Quantity must be positive.")
                continue
        except ValueError:
            print("Invalid number.")
            continue

        if quantity > item['Quantity']:
            print(f"Sorry, only {item['Quantity']} in stock.")
            continue

        # Update cart
        for c in cart:
            if c['Name'] == item['Name']:
                c['Quantity'] += quantity
                break
        else:
            cart.append({'Name': item['Name'], 'Price': item['Price'], 'Quantity': quantity})

        item['Quantity'] -= quantity
        print(f"Added {quantity} {item['Name']}(s) to cart.")

        if item['Quantity'] <= 2:
            send_low_stock_email(item['Name'], item['Quantity'])
            send_low_stock_sms(item['Name'], item['Quantity'])

            restock = input(f"{item['Name']} is low. Restock? (yes/no): ").strip().lower()
            if restock == 'yes':
                try:
                    restock_amount = int(input("Enter restock amount: "))
                    if restock_amount > 0:
                        item['Quantity'] += restock_amount
                        print(f"{item['Name']} now has {item['Quantity']} in stock.")
                    else:
                        print("Invalid restock quantity.")
                except ValueError:
                    print("Invalid number.")

        save_items(json_file, items)

if __name__ == "__main__":
    main()
