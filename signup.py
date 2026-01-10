import tkinter as tk
<<<<<<< HEAD
import os
import logging
import subprocess
from security_utils import hash_password, encrypt_json, decrypt_json
from tkinter import filedialog, messagebox
from shutil import copyfile
import sys


appdata_path = os.getenv("APPDATA")
folder_name = "Money-Management-System"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)


users_file_path = os.path.join(folder_path, "users.json")
current_user_json_path = os.path.join(folder_path, "current_user.json")


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

        if os.path.getsize(file_path) > 2 * 1024 * 1024:
            messagebox.showerror("Error", "Image size must be under 2 MB.")
            return


        appdata_path = os.getenv("APPDATA")
        dest_path = os.path.join(appdata_path, "Money-Management-System", f"{username_entry.get()}_pic.png")
        copyfile(file_path, dest_path)
        profile_pic_path = dest_path


        button.config(text="Picture Selected", bg="green")
=======
from tkinter import ttk


import main
import os
from tkinter import messagebox
from security_utils import hash_password,encrypt_json,decrypt_json

appdata_path = os.getenv("APPDATA")
folder_name = "Monefy"
folder_path = os.path.join(appdata_path, folder_name)
os.makedirs(folder_path, exist_ok=True)
users_file_path = os.path.join(folder_path, "users.json")
>>>>>>> fbfe2d0 (redesigned_ui)





<<<<<<< HEAD

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
    username = username_entry.get()
    login_data = {
        "username": username
    }

    with open(current_user_json_path, "wb") as file:
        file.write(encrypt_json(login_data))
        logging.info("encrypted current_user.json saved")
    root.destroy()

    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "Core.py")])


def signin_clicked(event):

    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "login.py")])


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
=======
def signup_ui():
    entries = []
    def create_entry():
        entries.append(first_name.get())
        entries.append(last_name.get())
        entries.append(email.get())
        entries.append(password.get())
        entries.append(confirm_pw.get())
        entries.append(username.get())


    def check_entries():
        create_entry()
        if "" in entries:
            tk.messagebox.showerror("Error", "Please fill in all fields.")
            entries.clear()
            return False
        if password.get() != confirm_pw.get():
            tk.messagebox.showerror("Error", "Passwords do not match.")
            entries.clear()
            return False
        return True

    def check_duplicate(username_input):

        if not os.path.exists(users_file_path):
            return False

        try:
            with open(users_file_path, "rb") as file:
                data = decrypt_json(file.read())
        except Exception:
            data = {}

        if username_input in data:
            messagebox.showerror("Error", "Username already exists. Choose another one.")
            del data
            return False
        return True

    def saving_data():

        password_hash = hash_password(password.get())

        if os.path.exists(users_file_path):
            try:
                with open(users_file_path, "rb") as file:
                    data = decrypt_json(file.read())
            except Exception as e:

                data = {}

        else:
            data = {}

        user_id = f"{username.get()}"
        data[user_id] = {
              "firstname": first_name.get(),
              "lastname": last_name.get(),
             "email": email.get(),
             "username": username.get(),
             "password": password_hash
         }
        with open(users_file_path, "wb") as file:
            file.write(encrypt_json(data))

        messagebox.showinfo(
            "Success",
            "Registration Successful"
        )
        return True




    def signup():
        if not check_entries():
            return
        if not check_duplicate(username.get()):
            return
        if not saving_data():
            return
        root.destroy()
        main.launch_signin()







    root = tk.Tk()
    root.title("Create an account")
    root.geometry("600x450")
    root.configure(bg="white")

    # Styling
    style = ttk.Style()
    style.configure("TLabel", background="white", foreground="#333", font=("Arial", 10))
    style.configure("Header.TLabel", font=("Arial", 16, "bold"))
    style.configure("Link.TLabel", foreground="blue", font=("Arial", 10, "underline"))

    # Main Container
    main_frame = tk.Frame(root, bg="white", padx=40, pady=30)
    main_frame.pack(fill="both", expand=True)

    # Header Section
    header_label = ttk.Label(main_frame, text="Create an account", style="Header.TLabel")
    header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

    login_frame = tk.Frame(main_frame, bg="white")
    login_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

    ttk.Label(login_frame, text="Already have an account? ").pack(side="left")
    login_label = ttk.Label(login_frame, text="Log in", style="Link.TLabel", cursor="hand2")
    login_label.pack(side="left")

    login_label.bind("<Button-1>", lambda e: open_signin())

    def open_signin():
        root.destroy()
        main.launch_signin()


    def create_field(label_text, row, col, columnspan=1):
        ttk.Label(main_frame, text=label_text).grid(
            row=row, column=col, sticky="w", pady=(10, 2), columnspan=columnspan
        )

        entry = ttk.Entry(main_frame, font=("Arial", 11))
        entry.grid(
            row=row + 1,
            column=col,
            sticky="ew",
            padx=(0, 10) if col == 0 else 0,
            pady=(0, 10),
            columnspan=columnspan
        )


        for c in range(col, col + columnspan):
            main_frame.columnconfigure(c, weight=1)

        return entry


    first_name = create_field("First name", 2, 0)
    last_name = create_field("Last name", 2, 1)

    email = create_field("Email", 4, 0)
    password = create_field("Password", 6, 0)
    confirm_pw = create_field("Confirm your password", 6, 1)
    username = create_field("Username", 8, 0)


    def on_enter(e):
        submit_btn['background'] = '#4CAF50'

    def on_leave(e):
        submit_btn['background'] = '#66BB6A'


    submit_btn = tk.Button(
        main_frame,
        text="Create account",
        bg="#66BB6A",  # green
        fg="white",
        font=("Arial", 12, "bold"),
        bd=0,  # no border
        padx=20,
        pady=10,
        cursor="hand2",
        activebackground="#4CAF50",
        activeforeground="white",
        command=signup
    )
    submit_btn.grid(row=10, column=1, columnspan=2, pady=(20, 0))


    submit_btn.bind("<Enter>", on_enter)
    submit_btn.bind("<Leave>", on_leave)


    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)




    root.mainloop()


>>>>>>> fbfe2d0 (redesigned_ui)
