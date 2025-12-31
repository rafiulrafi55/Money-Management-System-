import tkinter as tk
import json
from tkinter import messagebox
import os
import logging
import subprocess
from security_utils import hash_password, encrypt_json, decrypt_json
from tkinter import filedialog, messagebox
import shutil
from shutil import copyfile


appdata_path = os.getenv("APPDATA")
folder_name = "Money-Management-System"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)


users_file_path = os.path.join(folder_path, "users.json")


log_dir = os.path.join(folder_path, "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "signup.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("signup application started")


entries = []

profile_pic_path = None  # Global variable to store the selected path

def select_profile_picture(button):
    global profile_pic_path
    file_path = filedialog.askopenfilename(
        title="Select your profile picture",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        # Optional: size limit 2 MB
        if os.path.getsize(file_path) > 2 * 1024 * 1024:
            messagebox.showerror("Error", "Image size must be under 2 MB.")
            return

        # Save a copy in AppData
        appdata_path = os.getenv("APPDATA")
        dest_path = os.path.join(appdata_path, "Money-Management-System", f"{username_entry.get()}_pic.png")
        copyfile(file_path, dest_path)
        profile_pic_path = dest_path

        # Update button to show selection
        button.config(text="Picture Selected", bg="green")






def check_entries():
    is_empty = False
    for entry in entries:
        if not entry.get().strip():
            entry.config(bg="red")
            is_empty = True
        else:
            entry.config(bg="white")
    if is_empty:
        messagebox.showwarning("Error", "Please fill all fields")
        logging.error("empty fields found")
        return False
    return True

def passwords_check():
    if passwd_entry.get() != confirm_passwd_entry.get():
        messagebox.showerror("Error", "Passwords do not match")
        passwd_entry.config(bg="red")
        confirm_passwd_entry.config(bg="red")
        logging.error("passwords mismatch found")
        return False
    return True

def saving_data():
    firstname = firstName_entry.get()
    lastname = lastName_entry.get()
    email = email_entry.get()
    username = username_entry.get()
    key = key_entry.get()


    password_hash = hash_password(passwd_entry.get())

    if os.path.exists(users_file_path):
        try:
            with open(users_file_path, "rb") as file:
                data = decrypt_json(file.read())
                logging.info("encrypted users.json loaded")
        except Exception as e:
            logging.error(f"failed to decrypt users.json: {e}")
            data = {}
    else:
        data = {}

    user_id = f"user{len(data) + 1}"

    data[user_id] = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "username": username,
        "password": password_hash,
        "key": key,
        "profile_image": profile_pic_path if profile_pic_path else ""
    }


    with open(users_file_path, "wb") as file:
        file.write(encrypt_json(data))
        logging.info("encrypted users.json saved")

    messagebox.showinfo(
        "Success",
        f"Registration Successful\nYour key is: {key}\nPlease save this key securely"
    )
    return True

def clear_entries():
    firstName_entry.delete(0, tk.END)
    lastName_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    passwd_entry.delete(0, tk.END)
    confirm_passwd_entry.delete(0, tk.END)
    key_entry.delete(0, tk.END)
    return True

def begin_signup():
    if not check_entries():
        return
    if not passwords_check():
        return
    if not saving_data():
        return
    clear_entries()

def signin_clicked(event):
    path = os.path.join(folder_path, "login.py")
    root.destroy()
    subprocess.run(["python", path])


root = tk.Tk()
root.tk_setPalette(background='white')
root.title("Sign Up Frame")
root.geometry("400x450")

title_label = tk.Label(root, text="Sign Up", font=("Ariel",20,"bold"), anchor="center")
title_label.grid(row=0, column=0)

def create_entry(label_text, row, width=40):
    label = tk.Label(root, text=label_text)
    label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root, width=width)
    entry.grid(row=row, column=1, padx=10, pady=5)
    entries.append(entry)
    return entry

firstName_entry = create_entry("First Name:", 1)
lastName_entry = create_entry("Last Name:", 2)
email_entry = create_entry("Email:", 3)
username_entry = create_entry("Username:", 4)
key_entry = create_entry("Security Key:", 5)
passwd_entry = create_entry("Password:", 6)
confirm_passwd_entry = create_entry("Confirm Password:", 7)

signup_button = tk.Button(
    root, command=begin_signup, text="Sign Up",
    bg='red', fg='white',
    activebackground='darkred',
    activeforeground='white',
    cursor="hand2", width=20
)
signup_button.grid(row=9, column=0, columnspan=2, pady=10)

signin_text = tk.Label(root, text="Already have an account?")
signin_text.grid(row=10, column=0,columnspan=2, sticky="ew")

signin_binder = tk.Label(root, text="Sign In", cursor="hand2", fg='blue')
signin_binder.grid(row=11, column=0, columnspan=2, sticky="ew")
signin_binder.bind("<Button-1>", signin_clicked)

profile_pic_button = tk.Button(root, text="Select Profile Pic",
                               command=lambda: select_profile_picture(profile_pic_button),
                               bg="white", fg="black", cursor="hand2", width=20)
profile_pic_button.grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()
