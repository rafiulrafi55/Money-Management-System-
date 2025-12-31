import tkinter as tk
from tkinter import messagebox
import logging
import os
import subprocess
from security_utils import decrypt_json

appdata_path = os.getenv("APPDATA")
folder_name = "Money-Management-System"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)


users_file_path = os.path.join(folder_path, "users.json")

log_dir = os.path.join(folder_path, "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "forgot_password.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Forgot Password application started")

def login():
    logging.info("Login button clicked")
    path = os.path.join(folder_path, "login.py")
    root.destroy()
    subprocess.run(["python", path])

def signup():
    logging.info("Sign Up button clicked")
    path = os.path.join(folder_path, "signup.py")
    root.destroy()
    subprocess.run(["python", path])

def authenticate():
    logging.info("Password recovery started")

    try:
        with open(users_file_path, "rb") as file:
            data = decrypt_json(file.read())
            logging.info("users.json decrypted successfully")
    except FileNotFoundError:
        messagebox.showerror("Error", "No accounts found. Please sign up first.")
        logging.error("users.json not found")
        return
    except Exception as e:
        messagebox.showerror("Error", "User data corrupted.")
        logging.error(f"decryption failed: {e}")
        return

    email_input = email_entry.get()
    key_input = key_entry.get()

    for user_id, user in data.items():
        if user["email"] == email_input:
            if user["key"] == key_input:
                messagebox.showinfo(
                    "Verified",
                    "Your identity has been verified.\n\n"
                    "For security reasons, passwords cannot be retrieved.\n"
                    "Please log in and reset your password."
                )
                logging.info(f"identity verified for {email_input}")
                email_entry.delete(0, tk.END)
                key_entry.delete(0, tk.END)
                return
            else:
                messagebox.showerror("Error", "The security key is incorrect.")
                logging.warning(f"incorrect key for {email_input}")
                return

    messagebox.showerror("Error", "Account not found.")
    logging.error(f"no account found for {email_input}")

root = tk.Tk()
root.tk_setPalette(background='white')
root.title("Forgot Password")
root.geometry("400x400")

email_label = tk.Label(root, text="Email:")
email_label.grid(row=1, column=0, padx=10, pady=30, sticky="e")
email_entry = tk.Entry(root, width=40)
email_entry.grid(row=1, column=1, padx=10, pady=5)

key_label = tk.Label(root, text="Key:")
key_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
key_entry = tk.Entry(root, width=40)
key_entry.grid(row=2, column=1, padx=10, pady=5)

get_password_button = tk.Button(
    root, text="Get Password", command=authenticate,
    bg='red', fg='white', activebackground='darkred',
    activeforeground='white', cursor="hand2"
)
get_password_button.grid(row=3, column=1, pady=50, sticky=tk.N)

login_button = tk.Button(
    root, text="Login", command=login,
    bg='green', fg='white', activebackground='darkred',
    activeforeground='white', cursor="hand2"
)
login_button.grid(row=3, column=1, pady=5, sticky=tk.W)

signup_button = tk.Button(
    root, text="Sign Up", command=signup,
    bg='blue', fg='white', activebackground='darkred',
    activeforeground='white', cursor="hand2"
)
signup_button.grid(row=3, column=1, pady=5, sticky=tk.E)

root.mainloop()
