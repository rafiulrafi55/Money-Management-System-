import tkinter as tk
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
        if not all([first_name.get(), last_name.get(), email.get(), username.get(), password.get(), confirm_pw.get()]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return False
        if password.get() != confirm_pw.get():
            messagebox.showerror("Error", "Passwords do not match.")
            return False
        return True

    def check_duplicate(username_input):
        data = {}
        if os.path.exists(users_file_path):
            try:
                with open(users_file_path, "rb") as file:
                    data = decrypt_json(file.read())
            except Exception:
                messagebox.showwarning("Warning", "Users file is empty or corrupted. Starting fresh.")
                data = {}

        if username_input in data:
            messagebox.showerror("Error", "Username already exists. Choose another one.")
            return False
        return True

    def saving_data():
        password_hash = hash_password(password.get())
        data = {}
        if os.path.exists(users_file_path):
            try:
                with open(users_file_path, "rb") as file:
                    data = decrypt_json(file.read())
            except Exception:
                data = {}

        data[username.get()] = {
            "firstname": first_name.get(),
            "lastname": last_name.get(),
            "email": email.get(),
            "username": username.get(),
            "password": password_hash
        }

        try:
            with open(users_file_path, "wb") as file:
                file.write(encrypt_json(data))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {e}")
            return False

        return True

    def signup():
        if not check_entries():
            return
        if not check_duplicate(username.get()):
            return
        try:
            saving_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {e}")
            return
        root.destroy()
        # launch signin window
        messagebox.showinfo("Success", "Signup successful! Launch signin window here.")

    root = tk.Tk()
    root.title("Create an account")
    root.geometry("600x500")
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


if __name__ == "__main__":
    signup_ui()