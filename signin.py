import tkinter as tk
from tkinter import font, messagebox
import main
import os
from security_utils import decrypt_json,verify_password,encrypt_json,hash_password
import json


def signin_ui():
    def forgot_password_ui():
        fp_window = tk.Toplevel(root)
        fp_window.title("Reset Password")
        fp_window.geometry("350x360")
        fp_window.configure(bg="#F4F6F8")
        fp_window.resizable(False, False)
        win_width = 350
        win_height = 360
        screen_width = fp_window.winfo_screenwidth()
        screen_height = fp_window.winfo_screenheight()
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)
        fp_window.geometry(f"{win_width}x{win_height}+{x}+{y}")


        tk.Label(fp_window, text="Username:", bg="#F4F6F8").place(x=20, y=20)
        fp_username = tk.Entry(fp_window)
        fp_username.place(x=20, y=45, width=300, height=30)

        tk.Label(fp_window, text="Email:", bg="#F4F6F8").place(x=20, y=80)
        fp_email = tk.Entry(fp_window)
        fp_email.place(x=20, y=105, width=300, height=30)

        tk.Label(fp_window, text="New Password:", bg="#F4F6F8").place(x=20, y=140)
        fp_new_pass = tk.Entry(fp_window, show="*")
        fp_new_pass.place(x=20, y=165, width=300, height=30)

        tk.Label(fp_window, text="Confirm Password:", bg="#F4F6F8").place(x=20, y=200)
        fp_confirm_pass = tk.Entry(fp_window, show="*")
        fp_confirm_pass.place(x=20, y=225, width=300, height=30)

        def reset_password():
            uname = fp_username.get()
            email = fp_email.get()
            new_pass = fp_new_pass.get()
            confirm_pass = fp_confirm_pass.get()

            if not uname or not email or not new_pass or not confirm_pass:
                messagebox.showerror("Error", "All fields are required")
                return

            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords do not match")
                return

            appdata_path = os.getenv("APPDATA")
            folder_name = "Monefy"
            folder_path = os.path.join(appdata_path, folder_name)
            users_file_path = os.path.join(folder_path, "users.json")

            if not os.path.exists(users_file_path):
                messagebox.showerror("Error", "No users registered yet.")
                return

            try:
                with open(users_file_path, "rb") as file:
                    data = decrypt_json(file.read())
            except Exception:
                messagebox.showerror("Error", "Failed to read user data.")
                return

            user_data = data.get(uname)
            if user_data and user_data.get("email") == email:
                hashed_password = hash_password(new_pass)
                data[uname]["password"] = hashed_password

                try:
                    with open(users_file_path, "wb") as file:
                        file.write(encrypt_json(data))
                    messagebox.showinfo("Success", "Password reset successfully!")
                    fp_window.destroy()
                except Exception:
                    messagebox.showerror("Error", "Failed to save new password")
            else:
                messagebox.showerror("Error", "Username and email do not match")
                fp_window.destroy()
                forgot_password_ui()

        tk.Button(fp_window, text="Reset Password", bg="#6C4AF2", fg="white", command=reset_password).place(x=20, y=280, width=300, height=40)

    def check_entries():
        if username.get() == "" or password.get() == "":
            messagebox.showerror("Error","Entries cannot be empty")
            return False
        else:
            return True

    def check_credentials(username_input, password_input):
        appdata_path = os.getenv("APPDATA")
        folder_name = "Monefy"
        folder_path = os.path.join(appdata_path, folder_name)
        users_file_path = os.path.join(folder_path, "users.json")

        if not os.path.exists(users_file_path):
            messagebox.showerror("Error", "No users registered yet.")
            return

        try:
            with open(users_file_path, "rb") as file:
                data = decrypt_json(file.read())
        except Exception:
            messagebox.showerror("Error", "Failed to read user data.")
            return

        user_data = data.get(username_input)
        if user_data:
            if verify_password(password_input, user_data["password"]):

                login_data = {
                    "username": username_input
                }
                currentuser_path = os.path.join(folder_path, "current_user.json")
                with open(currentuser_path, "w") as file:
                    json.dump(login_data, file)
                root.destroy()
                main.launch_dashboard()

            else:
                messagebox.showerror("Error", "Wrong Password")
        else:
            messagebox.showerror("Error", "User not found")

    def signin_clicked():
        if not check_entries():
            return
        check_credentials(username.get(),password.get())


    root = tk.Tk()
    root.geometry("900x500")
    root.configure(bg="#F4F6F8")
    root.resizable(False, False)
    root.title("Login")

    win_width = 900
    win_height = 500


    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()


    x = (screen_width // 2) - (win_width // 2)
    y = (screen_height // 2) - (win_height // 2)


    root.geometry(f"{win_width}x{win_height}+{x}+{y}")

    root.lift()
    root.attributes('-topmost', True)
    root.after(0, lambda: root.attributes('-topmost', False))


    title_font = font.Font(family="Segoe UI", size=24, weight="bold")
    feature_title_font = font.Font(family="Segoe UI", size=16, weight="bold")
    feature_font = font.Font(family="Segoe UI", size=10)
    label_font = font.Font(family="Segoe UI", size=10)
    entry_font = font.Font(family="Segoe UI", size=10)
    btn_font = font.Font(family="Segoe UI", size=11, weight="bold")
    link_font = font.Font(family="Segoe UI", size=9, underline=True)

    tk.Label(
        root,
        text="Monefy",
        bg="#F4F6F8",
        fg="#111111",
        font=title_font
    ).place(relx=0.5, y=3, anchor="n")

    features_frame = tk.Frame(
        root,
        bg="#F8F9FB",
        width=300,
        height=300,
        highlightbackground="#E0E0E0",
        highlightthickness=1
    )
    features_frame.place(x=40, y=80)
    features_frame.pack_propagate(False)

    tk.Label(
        features_frame,
        text="Why Monefy?",
        bg="#F8F9FB",
        fg="#111111",
        font=feature_title_font
    ).place(x=20, y=20)

    features = [
        "• Track your income & expenses",
        "• Simple and clean interface",
        "• Secure users data",
        "• Open source",
        "• Full offline"
    ]

    y_pos = 70
    for feature in features:
        tk.Label(
            features_frame,
            text=feature,
            bg="#F8F9FB",
            fg="#333333",
            font=feature_font,
            anchor="w"
        ).place(x=20, y=y_pos)
        y_pos += 35

    card = tk.Frame(
        root,
        bg="#F6F6F6",
        width=320,
        height=330,
        highlightbackground="#DDDDDD",
        highlightthickness=1
    )
    card.place(x=520, y=80)
    card.pack_propagate(False)

    tk.Label(
        card,
        text="Username",
        bg="#F6F6F6",
        fg="#111111",
        font=label_font
    ).place(x=20, y=25)

    username = tk.Entry(
        card,
        font=entry_font,
        bd=0,
        highlightthickness=1,
        highlightbackground="#DDDDDD"
    )
    username.place(x=20, y=50, width=280, height=35)

    tk.Label(
        card,
        text="Password",
        bg="#F6F6F6",
        fg="#111111",
        font=label_font
    ).place(x=20, y=100)

    password = tk.Entry(
        card,
        font=entry_font,
        bd=0,
        show="*",
        highlightthickness=1,
        highlightbackground="#DDDDDD"
    )
    password.place(x=20, y=125, width=280, height=35)

    sign_in = tk.Button(
        card,
        text="Sign In",
        bg="#6C4AF2",
        fg="white",
        font=btn_font,
        bd=0,
        activebackground="#5A3EE6",
        cursor="hand2",
        command=signin_clicked
    )
    sign_in.place(x=20, y=185, width=280, height=40)

    forgot_label = tk.Label(
        card,
        text="Forgot password?",
        bg="#F6F6F6",
        fg="#111111",
        font=link_font,
        cursor="hand2"
    )
    forgot_label.place(x=20, y=245)
    forgot_label.bind("<Button-1>", lambda e: forgot_password_ui())

    def create_3d_signup_button(parent, x, y, text, command=None):
        width, height = 120, 42
        depth = 4

        canvas = tk.Canvas(
            parent,
            width=width + depth,
            height=height + depth,
            bg="white",
            highlightthickness=0
        )
        canvas.place(x=x, y=y)

        canvas.create_rectangle(
            depth, depth,
            width + depth, height + depth,
            fill="#C62828",
            outline=""
        )

        button = canvas.create_rectangle(
            0, 0,
            width, height,
            fill="#FF3B3B",
            outline=""
        )

        text_item = canvas.create_text(
            width // 2,
            height // 2,
            text=text,
            fill="white",
            font=btn_font
        )

        def on_press(event):
            canvas.move(button, depth, depth)
            canvas.move(text_item, depth, depth)

        def on_release(event):
            canvas.move(button, -depth, -depth)
            canvas.move(text_item, -depth, -depth)
            if command:
                command()

        for item in (button, text_item):
            canvas.tag_bind(item, "<ButtonPress-1>", on_press)
            canvas.tag_bind(item, "<ButtonRelease-1>", on_release)

        canvas.config(cursor="hand2")

    def signup_clicked():
        root.destroy()
        main.launch_signup()

    create_3d_signup_button(
        root,
        x=40,
        y=420,
        text="Sign Up",
        command=signup_clicked
    )

    root.mainloop()