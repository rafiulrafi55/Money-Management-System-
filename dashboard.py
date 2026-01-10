import tkinter as tk
from tkinter import font, messagebox
from ctypes import windll  # For DPI fix on Windows
import os
import json
from security_utils import decrypt_json,hash_password
# ---------------- ROOT ----------------
try:
    windll.shcore.SetProcessDpiAwareness(1)  # Fix blurry window on Windows
except:
    pass

appdata_path = os.getenv("APPDATA")
folder_name = "Monefy"
folder_path = os.path.join(appdata_path, folder_name)
current_user_path = os.path.join(folder_path, "current_user.json")
users_path = os.path.join(folder_path, "users.json")
user_data_file = os.path.join(folder_path, "user_data.json")

def dashboard_ui():
    with open(current_user_path, "r") as f:
        data = json.load(f)
    username = data["username"]
    del data
    with open(users_path, "rb") as file:
        data = decrypt_json(file.read())
    for user_id,user_data in data.items():
        if user_id == username:
            first_name = user_data["firstname"]
            last_name = user_data["lastname"]
            email = user_data["email"]
            password = user_data["password"]
    del data
    # ---------------- VARIABLES ----------------
    # Default numeric values
    balance_value = 0.00
    remaining_value = 0.00
    transactions_value = 0
    transactions_change_value = 0.00

    # Try to load user data
    try:
        with open(user_data_file, "r") as f:
            data = json.load(f)
            for user_id, user_data in data.items():
                if user_id == username:
                    balance_value = float(user_data.get("balance_value"))
                    remaining_value = float(user_data.get("remaining_value"))
                    transactions_value = int(user_data.get("transactions_value"))
                    transactions_change_value = float(user_data.get("transactions_change_value"))
    except FileNotFoundError:
        pass  # keep defaults

    def saving_data(balance,remaining,transactions_value,transactions_change):
        if os.path.exists(user_data_file):
            with open(user_data_file, "r") as f:
                data = json.load(f)
        else:
            data = {}
        user_id = f"{username}"
        data[user_id] = {
            "balance_value" : balance,
            "remaining_value" : remaining,
            "transactions_value" : transactions_value,
            "transactions_change_value" : transactions_change
        }
        with open(user_data_file, "w") as f:
            json.dump(data, f)
        return

    def on_closing():
        saving_data(balance_value,remaining_value,transactions_value,transactions_change_value)
        root.destroy()



    root = tk.Tk()
    root.title("Monefy Dashboard")
    root.geometry("1100x650")
    root.configure(bg="#F3F4F6")
    root.resizable(False, False)

    # ---------------- FONTS ----------------
    TITLE_FONT = font.Font(family="Segoe UI", size=18, weight="bold")
    CARD_TITLE = font.Font(family="Segoe UI", size=11, weight="bold")
    CARD_VALUE = font.Font(family="Segoe UI", size=20, weight="bold")
    CARD_SUB = font.Font(family="Segoe UI", size=9)

    # ---------------- HEADER ----------------
    header = tk.Frame(root, bg="white", height=60)  # No border
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Dashboard", bg="white", font=TITLE_FONT).pack(side="left", padx=25)

    # ---------------- CONTENT ----------------
    content = tk.Frame(root, bg="#F3F4F6")
    content.pack(fill="both", expand=True, padx=25, pady=20)
    content.columnconfigure((0, 1, 2), weight=1)
    content.rowconfigure((1, 2, 3), weight=1)

    # ---------------- CARD FACTORY ----------------
    def create_card(parent, row, col, w, h, colspan=1, rowspan=1):
        frame = tk.Frame(parent, bg="white", width=w, height=h, bd=2, relief="ridge")
        frame.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, padx=12, pady=12, sticky="nsew")
        frame.pack_propagate(False)
        return frame

    # ===================== TOP CARDS =====================
    balance_card = create_card(content, 1, 0, 260, 120)
    transactions_card = create_card(content, 1, 1, 260, 120)
    chart_card = create_card(content, 1, 2, 420, 400, rowspan=2)

    # ---------------- VARIABLES ----------------
    # Numeric values for calculations


    # StringVars for display
    balance_var = tk.StringVar(value=f"${balance_value:,.2f}")
    remaining_var = tk.StringVar(value=f"Remaining ${remaining_value:,.2f}")
    transactions_var = tk.StringVar(value=f"{transactions_value:,}")
    transactions_change_var = tk.StringVar(value=f"+${transactions_change_value:,.2f} From Previous Month")

    # ---------------- BALANCE CARD ----------------
    tk.Label(balance_card, text="Current Balance", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12, 4))
    tk.Label(balance_card, textvariable=balance_var, bg="white", font=CARD_VALUE).pack(anchor="w", padx=15)
    tk.Label(balance_card, textvariable=remaining_var, bg="white", fg="#6B7280", font=CARD_SUB).pack(anchor="w", padx=15)

    # ---------------- TRANSACTIONS CARD ----------------
    tk.Label(transactions_card, text="Total Transactions", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12, 4))
    tk.Label(transactions_card, textvariable=transactions_var, bg="white", font=CARD_VALUE).pack(anchor="w", padx=15)
    tk.Label(transactions_card, textvariable=transactions_change_var, bg="white", fg="#10B981", font=CARD_SUB).pack(anchor="w", padx=15)

    # ---------------- CHART PLACEHOLDER ----------------
    tk.Label(chart_card, text="Analytics", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=12)
    tk.Label(chart_card, text="Chart will appear here", bg="white", fg="#9CA3AF").pack(expand=True)

    # ===================== QUICK ADD =====================
    quick_card = create_card(content, 2, 0, 560, 120, colspan=2)
    tk.Label(quick_card, text="Transactions", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12, 10))

    # Frame for buttons
    btns = tk.Frame(quick_card, bg="white")
    btns.pack(fill="x", padx=15, pady=(0, 10))

    # ---------------- POPUP FUNCTIONS ----------------
    def add_money_popup(is_add=True):
        """Popup for Add or Remove Money"""

        popup_width = 500
        popup_height = 350
        popup = tk.Toplevel()
        popup.title("Add Money" if is_add else "Remove Money")
        popup.configure(bg="white")
        popup.transient(root)
        popup.grab_set()

        # Center popup
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        container = tk.Frame(popup, bg="white", padx=30, pady=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Amount", bg="white", fg="#333333", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        amount_entry = tk.Entry(container, font=("Arial", 12), relief="flat", highlightthickness=1, highlightbackground="#D3D3D3")
        amount_entry.grid(row=1, column=0, sticky="ew", pady=(0,15))

        tk.Label(container, text="Description", bg="white", fg="#333333", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", pady=(0,5))
        desc_entry = tk.Text(container, font=("Arial", 12), height=5, relief="flat", highlightthickness=1, highlightbackground="#D3D3D3")
        desc_entry.grid(row=3, column=0, sticky="ew", pady=(0,20))

        def submit_amount():
            nonlocal balance_value, transactions_value, transactions_change_value
            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
                return
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be positive")
                return

            if is_add:
                balance_value += amount
                transactions_change_value += amount
            else:
                if amount > balance_value:
                    messagebox.showerror("Error", "Not enough balance")
                    return
                balance_value -= amount
                transactions_change_value -= amount

            transactions_value += 1

            # Update display
            balance_var.set(f"${balance_value:,.2f}")
            transactions_var.set(f"{transactions_value:,}")
            transactions_change_var.set(f"+${transactions_change_value:,.2f} From Previous Month")

            popup.destroy()

        # Buttons
        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=4, column=0, sticky="ew")

        next_btn = tk.Button(btn_frame, text="Submit", bg="#333333", fg="white",
                             font=("Arial", 12, "bold"), width=10, pady=10,
                             relief="raised", cursor="hand2",
                             command=submit_amount)
        next_btn.pack(side="left", expand=True, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", bg="#EE2D24", fg="white",
                               font=("Arial", 12, "bold"), width=10, pady=10,
                               relief="raised", cursor="hand2",
                               command=popup.destroy)
        cancel_btn.pack(side="right", expand=True, padx=10)

        container.columnconfigure(0, weight=1)

    # ---------------- QUICK ADD BUTTONS ----------------
    buttons = [
        ("Add Money", "#10B981", lambda: add_money_popup(True)),
        ("Remove Money", "#EF4444", lambda: add_money_popup(False)),
        ("Transfer", "#6366F1", lambda: messagebox.showinfo("Info", "Transfer clicked")),
        ("Budget", "#111827", lambda: messagebox.showinfo("Info", "Budget clicked"))
    ]

    for i, (txt, clr, fn) in enumerate(buttons):
        btn = tk.Button(
            btns,
            text=txt,
            bg=clr,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            height=2,
            bd=4,
            relief="raised",
            activebackground=clr,
            activeforeground="white",
            cursor="hand2",
            command=fn
        )
        btn.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)

    for i in range(len(buttons)):
        btns.columnconfigure(i, weight=1)

    # ===================== LOWER CARDS =====================
    recent_card = create_card(content, 3, 0, 360, 170)
    top_spend_card = create_card(content, 3, 1, 360, 170)

    tk.Label(recent_card, text="Recent Transactions", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=12)
    for item in ["Grocery - $120", "Internet - $60", "Rent - $500"]:
        tk.Label(recent_card, text=item, bg="white", fg="#374151", font=CARD_SUB).pack(anchor="w", padx=15, pady=3)

    tk.Label(top_spend_card, text="Top Spends", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=12)
    for item in ["Rent - $500", "Food - $300", "Travel - $220"]:
        tk.Label(top_spend_card, text=item, bg="white", fg="#374151", font=CARD_SUB).pack(anchor="w", padx=15, pady=3)

    # ---------------- RUN ----------------
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    dashboard_ui()
