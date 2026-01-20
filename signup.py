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
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
icon = resource_path("app_icon.ico")


def signup_ui():

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
        if not agree_var.get():
            messagebox.showerror("Error", "You must agree to the Privacy Policy to create an account.")
            return
        try:
            saving_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {e}")
            return
        messagebox.showinfo("Success","Account created successfully")
        root.destroy()
        main.launch_signin()

    def center_window(window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    root = tk.Tk()
    root.title("Create an account")
    window_width = 600
    window_height = 550
    center_window(root, window_width, window_height)

    root.configure(bg="white")

    root.iconbitmap(icon)



    style = ttk.Style()
    style.configure("TLabel", background="white", foreground="#333", font=("Arial", 10))
    style.configure("Header.TLabel", font=("Arial", 16, "bold"))
    style.configure("Link.TLabel", foreground="blue", font=("Arial", 10, "underline"))


    main_frame = tk.Frame(root, bg="white", padx=40, pady=30)
    main_frame.pack(fill="both", expand=True)


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
        bg="#66BB6A",
        fg="white",
        font=("Arial", 12, "bold"),
        bd=0,
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

    agree_var = tk.IntVar()


    agree_frame = tk.Frame(main_frame, bg="white")
    agree_frame.grid(row=12, column=0, columnspan=2, sticky="w", pady=(10, 0))


    agree_check = tk.Checkbutton(
        agree_frame,
        variable=agree_var,
        bg="white",
        activebackground="white",
        highlightthickness=0
    )
    agree_check.pack(side="left")


    agree_label_text = tk.Label(
        agree_frame,
        text="I agree to the ",
        bg="white",
        fg="#333",
        font=("Arial", 10)
    )
    agree_label_text.pack(side="left")


    privacy_link = tk.Label(
        agree_frame,
        text="Privacy Policy",
        fg="blue",
        cursor="hand2",
        font=("Arial", 10, "underline"),
        bg="white"
    )
    privacy_link.pack(side="left")
    privacy_link.bind("<Button-1>", lambda e: show_privacy_policy())

    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)


    def show_privacy_policy():
        policy_window = tk.Toplevel(root)
        policy_window.title("Privacy Policy")
        policy_window.configure(bg="white")
        policy_window.iconbitmap(icon)


        width, height = 600, 500
        policy_window.update_idletasks()
        x = (policy_window.winfo_screenwidth() // 2) - (width // 2)
        y = (policy_window.winfo_screenheight() // 2) - (height // 2)
        policy_window.geometry(f"{width}x{height}+{x}+{y}")


        text_frame = tk.Frame(policy_window, bg="white")
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        policy_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg="white",
            fg="#333",
            font=("Arial", 10),
            bd=0,
            highlightthickness=0
        )
        policy_text.pack(fill="both", expand=True)
        scrollbar.config(command=policy_text.yview)


        privacy_policy_content = """
    Privacy Policy for Monefy

    Effective Date: January 20, 2026

    Monefy (“we”, “our”, or “us”) respects your privacy and is committed to protecting the personal information you share with us. This Privacy Policy explains how we collect, use, and safeguard your information when you use our application.

    1. Information We Collect
    - Personal Information: When you sign up, we collect your first name, last name, email address, username, and password.
    - Usage Data: Information about how you use the app, such as transactions added, categories used, or other in-app interactions.
    - Device Information: Your device type and operating system for app compatibility and troubleshooting.

    2. How We Use Your Information
    - To provide and improve our services.
    - To securely store and manage your account information.
    - To communicate important updates or notifications about your account.
    - To comply with legal obligations.

    3. Data Security
    - We use encryption to protect your personal data and passwords.
    - Your information is stored locally on your device unless otherwise required for backup purposes.
    - We adopt reasonable security measures to prevent unauthorized access or disclosure.

    4. Data Sharing
    - We do not sell or share your personal information with third parties for marketing purposes.
    - We may share your data if required by law or to protect our legal rights.

    5. Your Rights
    - You have the right to access, update, or delete your personal information stored within the app.
    - You can contact us at any time regarding your data privacy concerns.

    6. Changes to this Privacy Policy
    We may update this Privacy Policy from time to time. Any changes will be posted in the app or on our official website.

    7. Contact Us
    Email: rafiulrafi55@gmail.com

    """

        policy_text.insert("1.0", privacy_policy_content)
        policy_text.config(state="disabled")

    root.mainloop()


if __name__ == "__main__":
    signup_ui()