import logging
import tkinter as tk
import json
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import subprocess
import os
import sys


from security_utils import decrypt_json, encrypt_json, hash_password


appdata_path = os.getenv("APPDATA")
folder_name = "Money-Management-System"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)


fig = None
ax = None
canvas = None
transaction_history = []


def load_profile_image(parent_frame, size=(50, 50)):
    appdata_path = os.getenv("APPDATA")
    profile_pic_path = os.path.join(appdata_path, "Money-Management-System", "profile_pic.png")

    if os.path.exists(profile_pic_path):
        try:
            img = Image.open(profile_pic_path)
            img = img.resize(size, Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(parent_frame, image=photo, bg="white")
            label.image = photo
            label.grid(row=0, column=0, padx=5, pady=10)
        except Exception as e:
            print("Error loading profile image:", e)
    else:

        label = tk.Label(parent_frame, text="No Image", bg="white")
        label.grid(row=0, column=0, padx=5, pady=10)


current_user_file = os.path.join(folder_path, "current_user.json")

try:
    with open(current_user_file, "rb") as f:
        current_user = decrypt_json(f.read())
        CURRENT_USERNAME = current_user.get("username", "")
        CURRENT_PASSWORD_HASH = current_user.get("password", "")
except FileNotFoundError:
    messagebox.showerror("Error", "No current user found. Please login first.")
    CURRENT_USERNAME = ""
    CURRENT_PASSWORD_HASH = ""

    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "login.py")])


users_file = os.path.join(folder_path, "users.json")
try:
    with open(users_file, "rb") as f:
        Data = decrypt_json(f.read())
except FileNotFoundError:
    Data = {}

FIRSTNAME = LASTNAME = EMAIL = PASSWORD_HASH = USERNAME = KEY = ""

for key in Data:
    user = Data[key]
    if user["username"] == CURRENT_USERNAME:
        FIRSTNAME = user["firstname"]
        LASTNAME = user["lastname"]
        EMAIL = user["email"]
        PASSWORD_HASH = user["password"]
        USERNAME = user["username"]
        KEY = user["key"]
        break


user_data_file = os.path.join(
    folder_path,
    f"{USERNAME}_data.json" if USERNAME else "guest_data.json"
)

try:
    with open(user_data_file, "r") as f:
        user_data = json.load(f)
        current_balance = user_data.get("current_balance")
        total_transaction = user_data.get("total_transaction")
        transaction_history = user_data.get("transaction_history")
        recents = user_data.get("recents", [])
except FileNotFoundError:
    current_balance = 0.0
    total_transaction = 0.0
    transaction_history = []
    recents = []


def save_user_data():
    user_data = {
        "current_balance": current_balance,
        "total_transaction": total_transaction,
        "transaction_history": transaction_history,
        "recents": recents
    }
    with open(user_data_file, "w") as f:
        json.dump(user_data, f, indent=4)


def logout():
    save_user_data()
    current_user_file = os.path.join(folder_path, "current_user.json")
    if os.path.exists(current_user_file):
        try:
            os.remove(current_user_file)
            logging.info("current_user.json deleted successfully on logout")
        except Exception as e:
            logging.error(f"Failed to delete current_user.json: {e}")

    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "login.py")])


def add_recents(text):
    recents.append(text)

def get_recents():
    return recents[-1] if recents else "No recent transactions"


def init_graph(parent):
    global fig, ax, canvas
    fig = Figure(figsize=(3, 2), dpi=80)
    ax = fig.add_subplot(111)
    ax.set_title("Transaction History")
    ax.set_xlabel("Transaction")
    ax.set_ylabel("Amount")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def update_graph():
    if ax is None or canvas is None:
        return
    ax.clear()
    ax.plot(transaction_history, marker="o")
    ax.set_title("Transaction History")
    ax.set_xlabel("Transaction")
    ax.set_ylabel("Amount")
    canvas.draw()

def get_current_balance():
    return current_balance




def add_money_popup():

    def add_balance():
        if not add_money_entry.get().strip() or not transactioninfo_entry.get().strip():
            messagebox.showerror("Error", "Please enter amount and transaction info.")
            return

        global current_balance, total_transaction

        try:
            amount = float(add_money_entry.get())
            info = transactioninfo_entry.get().strip()

            if amount <= 0:
                messagebox.showerror("Invalid Amount", "Enter positive amount.")
                return

            current_balance += amount
            total_transaction += amount

            current_balance_amount_label.config(text=f"{current_balance:.2f}")
            total_transaction_amount_label.config(text=f"{total_transaction:.2f}")

            total_transaction_amount_label.config(text=f"{total_transaction:.2f}")
            current_balance_amount_label.config(text=f"{current_balance:.2f}")

            popup_balance_label.config(text=f"{current_balance:.2f}")

            transaction_history.append(total_transaction)
            update_graph()

            add_recents(f"{info} : +{amount}")
            recentstext_label.config(text=get_recents())

            add_money_entry.delete(0, tk.END)
            transactioninfo_entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Money added successfully!")

        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number.")

    def remove_balance():
        if not add_money_entry.get().strip() or not transactioninfo_entry.get().strip():
            messagebox.showerror("Error", "Please enter amount and transaction info.")
            return

        global current_balance, total_transaction

        try:
            amount = float(add_money_entry.get())
            info = transactioninfo_entry.get().strip()

            if amount <= 0 or amount > current_balance:
                messagebox.showerror("Invalid Amount", "Insufficient balance.")
                return

            current_balance -= amount
            total_transaction += amount

            current_balance_amount_label.config(text=f"{current_balance:.2f}")
            total_transaction_amount_label.config(text=f"{total_transaction:.2f}")

            total_transaction_amount_label.config(text=f"{total_transaction:.2f}")
            current_balance_amount_label.config(text=f"{current_balance:.2f}")

            transaction_history.append(total_transaction)
            update_graph()

            popup_balance_label.config(text=f"{current_balance:.2f}")

            add_recents(f"({info} : -{amount}")
            recentstext_label.config(text=get_recents())

            add_money_entry.delete(0, tk.END)
            transactioninfo_entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Money removed successfully!")

        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number.")

    popup = tk.Toplevel()
    popup.geometry("300x300")
    popup.title("Transaction")
    popup.grab_set()

    frame = tk.Frame(popup, bg="white", padx=10, pady=10)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text="Money :").pack()
    add_money_entry = tk.Entry(frame, width=40)
    add_money_entry.pack(pady=5)

    tk.Label(frame, text="Transaction Info :").pack()
    transactioninfo_entry = tk.Entry(frame, width=40)
    transactioninfo_entry.pack(pady=5)

    tk.Button(frame, text="Add Money", command=add_balance, bg="green", fg="white").pack(pady=10)
    tk.Button(frame, text="Remove Money", command=remove_balance, bg="red", fg="white").pack(pady=10)

    tk.Label(frame, text="Current Balance:").pack(pady=5)
    popup_balance_label = tk.Label(frame, text=f"{current_balance:.2f}", font=("Helvetica", 14, "bold"))
    popup_balance_label.pack(pady=5)




def quick_add(amount):
    global current_balance, total_transaction

    if amount < 0 and abs(amount) > current_balance:
        messagebox.showerror("Insufficient Balance", "Not enough balance.")
        return

    current_balance += amount
    total_transaction += abs(amount)

    current_balance_amount_label.config(text=f"{current_balance:.2f}")
    total_transaction_amount_label.config(text=f"{total_transaction:.2f}")

    transaction_history.append(total_transaction)
    update_graph()

    add_recents(f"Quick {'Add' if amount > 0 else 'Remove'}: {abs(amount)}")
    recentstext_label.config(text=get_recents())

def on_closing():
    save_user_data()

    root.destroy()


root = tk.Tk()
root.title("Money Management System")
root.geometry("350x700")
root.tk_setPalette(background='white')

top_frame = tk.Frame(root, bg="white", width=350, height=60)  # full window width
top_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=10, sticky="ew")
top_frame.grid_propagate(False)

# Profile picture (on the left)
profile_pic_path = os.path.join(folder_path, f"{USERNAME}_pic.png")
if os.path.exists(profile_pic_path):
    try:
        from PIL import Image, ImageTk
        img = Image.open(profile_pic_path)
        img = img.resize((50, 50), Image.Resampling.LANCZOS)
        profile_img = ImageTk.PhotoImage(img)
        profile_pic_label = tk.Label(top_frame, image=profile_img, bg="white")
        profile_pic_label.image = profile_img  # keep reference
        profile_pic_label.pack(side=tk.LEFT, padx=10, pady=5)
    except Exception as e:
        print("Error loading profile image:", e)

# Welcome Label (right next to profile picture)
welcome_label = tk.Label(top_frame, text=f"Welcome {FIRSTNAME}!", font=("Helvetica", 16), bg="white")
welcome_label.pack(side=tk.LEFT, padx=10, pady=5)

current_balance_frame = tk.Frame(root, bg="white", bd=4, relief="raised", width=150, height=100)
current_balance_frame.grid(row=1, column=0, padx=5, pady=10, )
current_balance_frame.grid_propagate(False)
current_balance_label = tk.Label(current_balance_frame, text=f"Current Balance :", font=("Helvetica", 12,"bold"))
current_balance_label.grid(row=0, column=1, padx=5, pady=10)
current_balance_amount_label = tk.Label(current_balance_frame, text=f"{current_balance:.2f}", font=("Helvetica", 14))
current_balance_amount_label.grid(row=1, column=1, padx=5, pady=5)


total_transaction_frame = tk.Frame(root, bg="white", bd=4, relief="raised",width=150, height=100)
total_transaction_frame.grid(row=1, column=1, padx=5, pady=10)
total_transaction_frame.grid_propagate(False)
total_transaction_label = tk.Label(total_transaction_frame, text="Total Transactions :", font=("Helvetica", 10,"bold"))
total_transaction_label.grid(row=0, column=1, padx=5, pady=10)
total_transaction_amount_label = tk.Label(total_transaction_frame, text=f"{total_transaction:.2f}", font=("Helvetica", 14))
total_transaction_amount_label.grid(row=1, column=1, padx=5, pady=5)

recents_frame = tk.Frame(root, bg="white", bd=4, relief="groove", width=300, height=70)
recents_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NS)
recents_frame.grid_propagate(False)
recents_label = tk.Label(recents_frame, text="Recents:", font=("Helvetica", 10,"bold"))
recents_label.grid(row=0, column=0, padx=0, pady=5, sticky=tk.W)
recentstext_label = tk.Label(recents_frame, text=get_recents(), font=("Helvetica", 8))
recentstext_label.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)

square_button_frame = tk.Frame(root, width=100, height=100, bg="white")
square_button_frame.grid(row=2, column=1, padx=(5,10), pady=10, sticky=tk.N)
square_button_frame.grid_propagate(False)
square_button = tk.Button(square_button_frame, command=add_money_popup, text="Make Transaction", bg="green", fg="white",
                          activebackground="darkgreen", activeforeground="white",
                          cursor="hand2", borderwidth=1)
square_button.pack(expand=True, fill="both")



quick_add_frame = tk.Frame(root, bg="white", bd=4, relief="groove", width=320, height=120)
quick_add_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
quick_add_frame.grid_propagate(False)

quick_add_label = tk.Label(quick_add_frame, text="Quick Add:", font=("Helvetica", 10,"bold"))
quick_add_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
quick_add_buttons = [
    ("+ 10", 10),
    ("+ 50", 50),
    ("+ 100", 100),
    ("- 10", -10),
    ("- 50", -50),
    ("- 100", -100),
]
for i, (text, amount) in enumerate(quick_add_buttons):
    button = tk.Button(quick_add_frame, text=text, command=lambda amt=amount: quick_add(amt),
                       bg="blue" if amount > 0 else "red", fg="white",
                       activebackground="darkblue" if amount > 0 else "darkred",
                       activeforeground="white", cursor="hand2", width=12)
    button.grid(row=1 + i // 3, column=i % 3, padx=5, pady=5)

graph_frame = tk.Frame(root, bg="white", bd=4, relief="groove", width=320, height=400)
graph_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW)
graph_frame.grid_propagate(False)



for i in range(2):
    root.grid_columnconfigure(i, weight=1)

recents_button = tk.Button(
    root, text="Recents",
    bg='blue', fg='white',
    activebackground='darkblue',
    activeforeground='white',
    cursor="hand2"
)
recents_button.grid(row=5, column=0, padx=5, pady=5, sticky=tk.EW)

settings_button = tk.Button(
    root, text="Settings",
    bg='green', fg='white',
    activebackground='darkgreen',
    activeforeground='white',
    cursor="hand2"
)
settings_button.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)


logout_button = tk.Button(
    root, text="Logout",
    command=logout,
    bg='red', fg='white',
    activebackground='darkred',
    activeforeground='white',
    cursor="hand2"
)
logout_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)

init_graph(graph_frame)
update_graph()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
