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
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        items = []
        for row in reader:
            cleaned_row = {k.strip(): v.strip() for k, v in row.items() if k and v}
            items.append(cleaned_row)
        return items


def save_items(filename, items):
    with open(filename, 'w', newline='') as file:
        fieldnames = ['Number', 'Name', 'Price', 'Quantity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def print_inventory(items):
    print("\nAvailable Items:")
    for item in items:
        quantity = int(item['Quantity'])
        status = ""
        if quantity <= 2:
            status = Fore.RED + " [LOW - Restock now!]" + Style.RESET_ALL
        elif quantity <= 4:
            status = Fore.YELLOW + " [Warning - Almost Low]" + Style.RESET_ALL
        else:
            status = Fore.GREEN + " [Stock OK]" + Style.RESET_ALL
        print(f"{item['Number']}. {item['Name']} - R{item['Price']} ({item['Quantity']} left){status}")


def find_item(items, choice):
    for item in items:
        if item['Number'] == choice or item['Name'].lower() == choice.lower():
            return item
    return None


def send_low_stock_email(item_name, remaining_stock):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Stock Alert: {item_name} is low"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = STOCK_OWNER_EMAIL
        msg.set_content(f"The stock for {item_name} is low. Only {remaining_stock} items remaining. Please restock soon.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(Fore.CYAN + f"Email sent to stock owner: {item_name} low in stock." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send email: {e}" + Style.RESET_ALL)


def send_low_stock_sms(item_name, remaining_stock):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Stock Alert: {item_name} is low ({remaining_stock} left). Restock soon!",
            from_=TWILIO_PHONE_NUMBER,
            to=OWNER_PHONE_NUMBER
        )
        print(Fore.CYAN + f"SMS sent to stock owner: {item_name} low in stock." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Failed to send SMS: {e}" + Style.RESET_ALL)


def main():
    filename = "XshopItems.txt"
    items = load_items(filename)
    cart = []

    print("Welcome to X Store!")

    while True:
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
