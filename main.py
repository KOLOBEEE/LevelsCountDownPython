
import csv
from colorama import Fore, Style

def load_items(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

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

def main():
    filename = "XshopItems.csv"
    items = load_items(filename)
    
    print("Welcome to X Store!")
    
    while True:
        print_inventory(items)
        choice = input("What would you like to buy? (Enter item name or number, or 'exit' to quit): ").strip()
        if choice.lower() == 'exit':
            break

        item = find_item(items, choice)
        if not item:
            print("Item not found. Try again.")
            continue

        try:
            quantity = int(input(f"How many {item['Name']}s would you like to buy? "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        available = int(item['Quantity'])
        if quantity > available:
            print(f"Sorry, only {available} left.")
            continue

        item['Quantity'] = str(available - quantity)
        print(f"You bought {quantity} {item['Name']}(s) for R{float(item['Price']) * quantity:.2f}")

        # Show restock prompt if stock is low
        if int(item['Quantity']) <= 2:
            restock = input(f"{item['Name']} is low in stock. Would you like to restock? (yes/no): ").strip().lower()
            if restock == 'yes':
                try:
                    restock_amount = int(input("Enter how many items to restock: "))
                    item['Quantity'] = str(int(item['Quantity']) + restock_amount)
                    print(f"{item['Name']} now has {item['Quantity']} in stock.")
                except ValueError:
                    print("Invalid number. Skipping restock.")

        save_items(filename, items)

if __name__ == "__main__":
    main()
