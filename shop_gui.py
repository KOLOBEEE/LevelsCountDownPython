import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from inventory_manager import load_inventory, save_inventory, send_low_stock_email, send_low_stock_sms



INVENTORY_FILE = "inventory.json"

class ShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop GUI")

        self.inventory = load_inventory(INVENTORY_FILE)

        self.inventory_list = tk.Listbox(root, width=60, height=15)
        self.inventory_list.pack(pady=10)

        self.qty_label = tk.Label(root, text="Quantity to Buy:")
        self.qty_label.pack()

        self.qty_entry = tk.Entry(root)
        self.qty_entry.pack()

        self.buy_button = tk.Button(root, text="Buy", command=self.buy_item)
        self.buy_button.pack(pady=10)

        self.cart = []
        self.display_inventory()

    def display_inventory(self):
        self.inventory_list.delete(0, tk.END)
        for idx, item in enumerate(self.inventory):
            self.inventory_list.insert(tk.END, 
                f"{idx + 1}. {item['Name']} - R{item['Price']} ({item['Quantity']} left)")

    def buy_item(self):
        selected_indices = self.inventory_list.curselection()
        if not selected_indices:
            messagebox.showwarning("No selection", "Please select an item to buy.")
            return

        idx = selected_indices[0]
        item = self.inventory[idx]

        qty_str = self.qty_entry.get()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showerror("Invalid quantity", "Enter a positive number.")
            return
        qty = int(qty_str)

        if qty > int(item['Quantity']):
            messagebox.showerror("Stock Error", f"Only {item['Quantity']} available.")
            return

        # Update stock and cart
        item['Quantity'] -= qty
        self.cart.append({'Name': item['Name'], 'Price': item['Price'], 'Quantity': qty})

        messagebox.showinfo("Purchase", f"Added {qty} x {item['Name']} to cart.")

        # Clear quantity input and refresh list
        self.qty_entry.delete(0, tk.END)
        self.display_inventory()

        # Check for low stock and notify
        if item['Quantity'] <= 2:
            send_low_stock_email(item['Name'], item['Quantity'])
            send_low_stock_sms(item['Name'], item['Quantity'])

            if messagebox.askyesno("Low Stock", f"{item['Name']} is low on stock. Restock?"):
                restock_qty = simpledialog.askinteger("Restock", "Enter restock quantity:", minvalue=1)
                if restock_qty:
                    item['Quantity'] += restock_qty
                    messagebox.showinfo("Restocked", f"{item['Name']} now has {item['Quantity']} in stock.")
                    self.display_inventory()

        save_inventory(INVENTORY_FILE, self.inventory)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()
