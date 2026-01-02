
import tkinter as tk
from tkinter import messagebox
import logging
import os
import subprocess
from security_utils import verify_password, decrypt_json, encrypt_json
import sys

log_dir = os.path.join(os.getenv("APPDATA"), "Money-Management-System", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "login.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("login application started")

appdata_path = os.getenv("APPDATA")
folder_name = "Money-Management-System"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)



users_json_path = os.path.join(folder_path, "users.json")
current_user_json_path = os.path.join(folder_path, "current_user.json")



def login():
    logging.info("login module started")

    try:
        with open(users_json_path, "rb") as file:
            data = decrypt_json(file.read())
            logging.info("encrypted users.json loaded")
    except FileNotFoundError:
        messagebox.showerror("Error", "Login failed. No accounts found. Please sign up first.")
        logging.error("users.json not found")
        return
    except Exception as e:
        messagebox.showerror("Error", "User data corrupted.")
        logging.error(f"failed to decrypt users.json: {e}")
        return

    input_username = username_entry.get()
    input_password = password_entry.get()
    logging.info("user input taken")

    for user_id, user in data.items():
        if user["username"] == input_username:
            if verify_password(input_password, user["password"]):
                post_login(input_username)
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)

                logging.info(f"user {user_id} logged in successfully")


                root.destroy()
                subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "core.py")])
                return
            else:
                messagebox.showwarning("Error", "Incorrect password.")
                logging.warning("incorrect password attempt")
                return

    messagebox.showwarning("Error", "Login failed. Check your username and password.")
    logging.error("login failed. no matching user found")

def post_login(username):
    logging.info("post login module started")

    login_data = {
        "username": username
    }

    with open(current_user_json_path, "wb") as file:
        file.write(encrypt_json(login_data))
        logging.info("encrypted current_user.json saved")

def signup_clicked(event):
    logging.info("signup clicked")
    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "signup.py")])

def forgot_password_clicked(event):
    logging.info("forgot password clicked")
    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "Forgot_Password.py")])


root = tk.Tk()
root.tk_setPalette(background='white')
root.title("Login Page")
root.geometry("300x300")

title_label = tk.Label(root, text="Log In", font=("Ariel",20,"bold"), anchor="center", background="white")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

username_label = tk.Label(root, text="Username:")
username_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
username_entry = tk.Entry(root)
username_entry.grid(row=1, column=1, padx=10, pady=5)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5)

login_button = tk.Button(
    root, text="Login", command=login,
    bg='red', fg='white',
    activebackground='darkred',
    activeforeground='white',
    cursor="hand2"
)
login_button.grid(row=3, column=1, columnspan=2, pady=10)

signup_text = tk.Label(root, text="Don't have an account?")
signup_text.grid(row=4, column=0, columnspan=2, sticky="ew")
signup_binder = tk.Label(root, text="Sign Up", cursor="hand2", fg='blue')
signup_binder.grid(row=4, column=1, sticky="e")
signup_binder.bind("<Button-1>", signup_clicked)

forgotPassword_binder = tk.Label(root, text="Forgot Password?", cursor="hand2", fg='blue')
forgotPassword_binder.grid(row=5, column=1, pady=20, sticky="w")
forgotPassword_binder.bind("<Button-1>", forgot_password_clicked)

root.mainloop()
