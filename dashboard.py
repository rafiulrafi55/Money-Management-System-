
import tkinter as tk
from tkinter import font
from ctypes import windll
import os
import json
from security_utils import decrypt_json, hash_password, encrypt_json
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
import main
import PIL
from PIL import Image, ImageTk
import webbrowser
import sys

from tkinter import filedialog, messagebox
from openpyxl import Workbook






try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

appdata_path = os.getenv("APPDATA")
folder_name = "Monefy"
folder_path = os.path.join(appdata_path, folder_name)
current_user_path = os.path.join(folder_path, "current_user.json")
users_path = os.path.join(folder_path, "users.json")
user_data_file = os.path.join(folder_path, "user_data.json")

def dashboard_ui():



    def export_transactions_to_excel(recents):
        if not recents:
            messagebox.showwarning("No Data", "No transactions to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Export Transactions"
        )

        if not file_path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"

        ws.append(["Date", "Description", "Type", "Amount"])

        for txn in sorted(recents.values(), key=lambda x: x["datetime"]):
            amount = txn["amount"]
            ws.append([
                txn["datetime"],
                txn["description"],
                "Income" if amount >= 0 else "Expense",
                amount
            ])

        wb.save(file_path)
        messagebox.showinfo("Exported", "Transactions exported successfully!")

    def render_analytics():
        for widget in chart_card.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        sorted_txns = sorted(recents.values(), key=lambda x: x["datetime"], reverse=True)[:10]

        if not sorted_txns:
            tk.Label(chart_card, text="No transactions yet", bg="white", fg="#9CA3AF").pack(expand=True)
            return

        def draw_chart():
            chart_card.update_idletasks()
            w = chart_card.winfo_width()
            h = chart_card.winfo_height()
            if w < 10 or h < 10:
                root.after(50, draw_chart)
                return

            amounts = [txn["amount"] for txn in sorted_txns]
            labels = [txn["datetime"].split(" ")[0] for txn in sorted_txns]
            colors = ["#10B981" if amt >= 0 else "#EF4444" for amt in amounts]

            dpi = 100
            fig_w = w / dpi
            fig_h = h / dpi

            fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi, constrained_layout=True)
            ax.bar(range(len(labels)), amounts, color=colors)

            ax.set_title("Last 10 Transactions", fontsize=10, pad=5)
            ax.set_ylabel("Amount (BDT)", fontsize=8, labelpad=3)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
            ax.tick_params(axis='y', labelsize=8)
            ax.margins(x=0.05)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            canvas = FigureCanvasTkAgg(fig, master=chart_card)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(x=0, y=30, width=w, height=h - 40)

        root.after(50, draw_chart)

    try:
        with open(current_user_path, "r") as f:
            data = json.load(f)
        username = data["username"]
        del data
    except FileNotFoundError:
        messagebox.showinfo("Error", "No user logged in")
        from main import launch_signin
        launch_signin()
        return


    with open(users_path, "rb") as file:
        data = decrypt_json(file.read())

    for user_id, user_data in data.items():
        if user_id == username:
            first_name = user_data["firstname"]
            last_name = user_data["lastname"]
            email = user_data["email"]
            password = user_data["password"]
    del data

    budget_value = None
    balance_value = 0.00
    transactions_value = 0
    transactions_change_value = 0.00
    recents = {}


    try:
        with open(user_data_file, "r") as f:
            data = json.load(f)
            if username in data:
                user_data = data[username]
                balance_value = float(user_data.get("balance_value", 0))
                transactions_value = int(user_data.get("transactions_value", 0))
                transactions_change_value = float(user_data.get("transactions_change_value", 0))
                recents = user_data.get("recents", {})
                budget_value = user_data.get("budget_value", None)


    except FileNotFoundError:
        pass

    def saving_data(balance, transactions, transactions_change, recents_data):
        if os.path.exists(user_data_file):
            with open(user_data_file, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[username] = {
            "balance_value": balance,
            "transactions_value": transactions,
            "transactions_change_value": transactions_change,
            "recents": recents_data,
            "budget_value": budget_value
        }

        with open(user_data_file, "w") as f:
            json.dump(data, f, indent=4)
        render_recent_transactions()

    flash_after_id = None
    flash_active = True

    def on_closing():
        nonlocal flash_active, flash_after_id, first_login
        flash_active = False
        if flash_after_id is not None:
            root.after_cancel(flash_after_id)
        saving_data(balance_value, transactions_value, transactions_change_value, recents)
        plt.close('all')
        root.destroy()

    def logout():
        os.remove(current_user_path)
        nonlocal flash_active, flash_after_id
        flash_active = False
        if flash_after_id is not None:
            root.after_cancel(flash_after_id)
        saving_data(balance_value, transactions_value, transactions_change_value, recents)
        plt.close('all')
        root.destroy()
        main.launch_signin()

    def get_remaining_budget():
        if budget_value is None:
            return "Budget not set"
        total_spent = sum(-txn["amount"] for txn in recents.values() if txn["amount"] < 0)
        remaining = budget_value - total_spent
        return f"Remaining Budget {remaining:,.2f}  BDT"

    def flash_warning():
        nonlocal flash_after_id
        if not flash_active:
            return
        if budget_warning_var.get():
            current_color = warning_label.cget("fg")
            new_color = "#FEE2E2" if current_color == "#EE2D24" else "#EE2D24"
            warning_label.config(fg=new_color)
            flash_after_id = root.after(1000, flash_warning)

    def update_remaining_budget():
        nonlocal budget_value, recents

        if budget_value is None:
            remaining_var.set("Budget not set")
            budget_warning_var.set("")
            return

        total_spent = sum(-txn["amount"] for txn in recents.values() if txn["amount"] < 0)
        remaining = budget_value - total_spent
        remaining_var.set(f"Remaining Budget {remaining:,.2f} BDT")

        warning_limit = getattr(root, "budget_warning_limit", 500)

        if remaining < warning_limit:
            budget_warning_var.set("⚠ Low budget remaining!")
            flash_warning()
        else:
            budget_warning_var.set("")

    def center_popup(popup, width, height):
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

    def render_recent_transactions():
        for widget in recent_list.winfo_children():
            widget.destroy()

        if not recents:
            tk.Label(recent_list, text="No transactions yet", bg="white", fg="#9CA3AF", font=CARD_SUB).pack(anchor="w")
            return

        sorted_txns = sorted(recents.values(), key=lambda x: x["datetime"], reverse=True)

        for txn in sorted_txns[:3]:
            amount = txn["amount"]
            date_time = txn["datetime"]
            color = "#10B981" if amount >= 0 else "#EF4444"
            sign = "+" if amount >= 0 else "-"
            text = f"{sign}{abs(amount):,.2f}  ({date_time})"
            tk.Label(recent_list, text=text, bg="white", fg=color, font=CARD_SUB, anchor="w").pack(fill="x", pady=2)

    def render_top_spend():
        for widget in top_spend_card.winfo_children():
            if isinstance(widget, tk.Label) and widget != top_spend_card.children['!label']:
                widget.destroy()

        expenses = [txn for txn in recents.values() if txn["amount"] < 0]

        if not expenses:
            tk.Label(top_spend_card, text="No expenses yet",bg="white", fg="#9CA3AF", font=CARD_SUB).pack(anchor="w", padx=15, pady=3)
            return

        highest = min(expenses, key=lambda x: x["amount"])
        amount = abs(highest["amount"])
        description = highest["description"]
        date_time = highest["datetime"]

        tk.Label(top_spend_card, text=f"{amount:,.2f} BDT", bg="white", fg="#EF4444", font=CARD_VALUE).pack(anchor="w", padx=15, pady=(5, 0))
        tk.Label(top_spend_card, text=f"{description}\n{date_time}", bg="white", fg="#374151", font=CARD_SUB, justify="left").pack(anchor="w", padx=15, pady=(5, 0))

    def get_top_spend_previous_month():
        from datetime import datetime, timedelta

        if not recents:
            return "No transactions last month"

        now = datetime.now()
        first_day_this_month = datetime(now.year, now.month, 1)
        last_month_end = first_day_this_month - timedelta(days=1)
        last_month_start = datetime(last_month_end.year, last_month_end.month, 1)


        last_month_expenses = [
            txn for txn in recents.values()
            if txn["amount"] < 0 and
               last_month_start <= datetime.strptime(txn["datetime"], "%Y-%m-%d %H:%M:%S") <= last_month_end
        ]

        if not last_month_expenses:
            return "No spend last month"


        top_spend = min(last_month_expenses, key=lambda x: x["amount"])
        amount = abs(top_spend["amount"])
        desc = top_spend.get("description", "No description")
        return f"Top spend last month: {amount:,.2f} BDT ({desc})"

    def center_window(window, width, height):
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    root = tk.Tk()
    root.title("Dashboard")
    root_width, root_height = 1100, 650
    center_window(root, root_width, root_height)
    root.configure(bg="#F3F4F6")
    root.resizable(False, False)




    TITLE_FONT = font.Font(family="Segoe UI", size=18, weight="bold")
    CARD_TITLE = font.Font(family="Segoe UI", size=11, weight="bold")
    CARD_VALUE = font.Font(family="Segoe UI", size=20, weight="bold")
    CARD_SUB = font.Font(family="Segoe UI", size=9)

    header = tk.Frame(root, bg="white", height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="Dashboard", bg="white", font=TITLE_FONT).pack(side="left", padx=25)

    content = tk.Frame(root, bg="#F3F4F6")
    content.pack(fill="both", expand=True, padx=25, pady=20)
    content.columnconfigure((0, 1, 2), weight=1)
    content.rowconfigure((1, 2, 3), weight=1)

    def create_card(parent, row, col, w, h, colspan=1, rowspan=1):
        frame = tk.Frame(parent, bg="white", width=w, height=h, bd=2, relief="ridge")
        frame.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, padx=12, pady=12, sticky="nsew")
        frame.pack_propagate(False)
        return frame

    balance_card = create_card(content, 1, 0, 260, 120)
    transactions_card = create_card(content, 1, 1, 260, 120)
    chart_card = create_card(content, 1, 2, 420, 400, rowspan=2)

    balance_var = tk.StringVar(value=f"{balance_value:,.2f} BDT")
    remaining_var = tk.StringVar(value=get_remaining_budget())
    budget_warning_var = tk.StringVar(value="")
    transactions_var = tk.StringVar(value=f"{transactions_value:,}")
    transactions_change_var = tk.StringVar(value=get_top_spend_previous_month())

    tk.Label(balance_card, text="Current Balance", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12,4))
    tk.Label(balance_card, textvariable=balance_var, bg="white", font=CARD_VALUE).pack(anchor="w", padx=15)
    tk.Label(balance_card, textvariable=remaining_var, bg="white", fg="#6B7280", font=CARD_SUB).pack(anchor="w", padx=15)

    warning_label = tk.Label(balance_card, textvariable=budget_warning_var, bg="white", fg="#EE2D24", font=CARD_SUB)
    warning_label.pack(anchor="w", padx=15)

    tk.Label(transactions_card, text="Total Transactions", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12,4))
    tk.Label(transactions_card, textvariable=transactions_var, bg="white", font=CARD_VALUE).pack(anchor="w", padx=15)
    tk.Label(transactions_card, textvariable=transactions_change_var, bg="white", fg="#10B981", font=CARD_SUB).pack(anchor="w", padx=15)

    tk.Label(chart_card, text="Analytics", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=5)

    quick_card = create_card(content, 2, 0, 560, 120, colspan=2)
    tk.Label(quick_card, text="Transactions", bg="white", font=CARD_TITLE).pack(anchor="w", padx=15, pady=(12,10))
    btns = tk.Frame(quick_card, bg="white")
    btns.pack(fill="x", padx=15, pady=(0,10))

    def creator_info_popup(root):
        popup = tk.Toplevel(root)
        popup.title("Welcome")
        popup.configure(bg="white")
        popup.resizable(False, False)


        popup_width, popup_height = 400, 300
        x = (popup.winfo_screenwidth() // 2) - (popup_width // 2)
        y = (popup.winfo_screenheight() // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.transient(root)
        popup.grab_set()

        from tkinter import font
        title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        sub_font = font.Font(family="Segoe UI", size=11)

        frame = tk.Frame(popup, bg="white", padx=20, pady=20)
        frame.pack(expand=True, fill="both")


        try:
            logo_image = Image.open(main.resource_path("app_icon.png"))
            logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(frame, image=logo_photo, bg="white")
            logo_label.image = logo_photo
            logo_label.pack(pady=(0, 15))
        except Exception as e:
            logo_canvas = tk.Canvas(frame, width=60, height=60, bg="#6366F1", highlightthickness=0)
            logo_canvas.create_text(30, 30, text="M", fill="white", font=("Segoe UI", 28, "bold"))
            logo_canvas.pack(pady=(0, 15))


        tk.Label(frame, text="Welcome to Monefy!", font=title_font, bg="white").pack(pady=(0, 10))

        tk.Label(
            frame,
            text="Created by: Rafiul Islam",
            font=sub_font,
            bg="white",
            fg="#374151",
            justify="center"
        ).pack()

        tk.Label(
            frame,
            text="Email: rafiulrafi55@gmail.com\nGitHub: github.com/rafiulrafi55",
            font=sub_font,
            bg="white",
            fg="#374151",
            justify="center"
        ).pack(pady=(0, 15))



        popup.wait_window()

    def open_recents_popup():
        popup = tk.Toplevel(root)
        popup.title("All Transactions")
        popup.configure(bg="white")
        popup.transient(root)
        popup.grab_set()


        width, height = 520, 500
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.resizable(False, False)

        tk.Label(
            popup,
            text="All Transactions",
            font=("Segoe UI", 16, "bold"),
            bg="white"
        ).pack(pady=(15, 10))

        container = tk.Frame(popup, bg="white")
        container.pack(fill="both", expand=True, padx=15, pady=10)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(window_id, width=e.width)
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not recents:
            tk.Label(
                scroll_frame,
                text="No transactions yet",
                bg="white",
                fg="#9CA3AF",
                font=("Segoe UI", 11)
            ).pack(pady=30)
            return

        sorted_txns = sorted(
            recents.values(),
            key=lambda x: x["datetime"],
            reverse=True
        )

        for txn in sorted_txns:
            amount = txn["amount"]
            desc = txn["description"]
            dt = txn["datetime"]

            is_income = amount >= 0
            color = "#10B981" if is_income else "#EF4444"
            sign = "+" if is_income else "-"

            card = tk.Frame(
                scroll_frame,
                bg="#F9FAFB",
                bd=1,
                relief="solid"
            )
            card.pack(fill="x", expand=True, pady=6, padx=2)


            top = tk.Frame(card, bg="#F9FAFB")
            top.pack(fill="x", padx=10, pady=(6, 2))

            tk.Label(
                top,
                text=desc or "No description",
                bg="#F9FAFB",
                font=("Segoe UI", 11, "bold")
            ).pack(side="left")

            tk.Label(
                top,
                text=f"{sign}{abs(amount):,.2f} BDT",
                bg="#F9FAFB",
                fg=color,
                font=("Segoe UI", 11, "bold")
            ).pack(side="right")

            bottom = tk.Frame(card, bg="#F9FAFB")
            bottom.pack(fill="x", padx=10, pady=(0, 6))

            tk.Label(
                bottom,
                text=dt,
                bg="#F9FAFB",
                fg="#6B7280",
                font=("Segoe UI", 9)
            ).pack(side="left")

            tk.Label(
                bottom,
                text="Income" if is_income else "Expense",
                bg="#F9FAFB",
                fg="#6B7280",
                font=("Segoe UI", 9)
            ).pack(side="right")

        export_btn = tk.Button(
            popup,
            text="⭳ Export",
            command=lambda: export_transactions_to_excel(recents),
            bg="#111827",
            fg="white",
            activebackground="#1F2937",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2"
        )

        export_btn.place(
            relx=1.0,
            rely=1.0,
            x=-40,
            y=-20,
            anchor="se"
        )



    def budget_popup():
        popup = tk.Toplevel()
        popup.title("Set Budget")
        popup.configure(bg="white")
        popup.transient(root)
        popup.grab_set()
        center_popup(popup, 400, 200)


        container = tk.Frame(popup, bg="white", padx=30, pady=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Budget Amount", bg="white", fg="#333333", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        budget_entry = tk.Entry(container, font=("Arial", 12), relief="flat", highlightthickness=1, highlightbackground="#D3D3D3")
        budget_entry.grid(row=1, column=0, sticky="ew", pady=(0,20))

        def submit_budget():
            nonlocal budget_value, recents
            try:
                amount = float(budget_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")
                return
            if amount <= 0:
                messagebox.showerror("Error", "Budget must be positive")
                return

            budget_value = amount
            recents = {k: v for k, v in recents.items() if v["amount"] >= 0}
            update_remaining_budget()
            saving_data(balance_value, transactions_value, transactions_change_value, recents)

            popup.destroy()

        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))
        tk.Button(btn_frame, text="Submit", bg="#333333", fg="white", font=("Arial",12,"bold"),
                  width=10, pady=10, relief="raised", cursor="hand2", command=submit_budget).pack(side="left", expand=True, padx=10)
        tk.Button(btn_frame, text="Cancel", bg="#EE2D24", fg="white", font=("Arial",12,"bold"),
                  width=10, pady=10, relief="raised", cursor="hand2", command=popup.destroy).pack(side="right", expand=True, padx=10)
        container.columnconfigure(0, weight=1)

    def add_money_popup(is_add=True):
        popup_width = 500
        popup_height = 350
        popup = tk.Toplevel()
        popup.title("Add Money" if is_add else "Remove Money")
        popup.configure(bg="white")
        popup.transient(root)
        popup.grab_set()
        center_popup(popup, popup_width, popup_height)


        container = tk.Frame(popup, bg="white", padx=30, pady=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Amount", bg="white", fg="#333333", font=("Arial",11,"bold")).grid(row=0,column=0,sticky="w", pady=(0,5))
        amount_entry = tk.Entry(container, font=("Arial",12), relief="flat", highlightthickness=1, highlightbackground="#D3D3D3")
        amount_entry.grid(row=1,column=0,sticky="ew", pady=(0,15))

        tk.Label(container, text="Description", bg="white", fg="#333333", font=("Arial",11,"bold")).grid(row=2,column=0,sticky="w", pady=(0,5))
        desc_entry = tk.Text(container, font=("Arial",12), height=5, relief="flat", highlightthickness=1, highlightbackground="#D3D3D3")
        desc_entry.grid(row=3,column=0,sticky="ew", pady=(0,20))

        def limit_desc_length(event):
            content = desc_entry.get("1.0","end-1c")
            if len(content)>20:
                desc_entry.delete("1.0","end")
                desc_entry.insert("1.0",content[:20])
        desc_entry.bind("<KeyRelease>", limit_desc_length)

        def submit_amount():
            nonlocal balance_value, transactions_value, transactions_change_value
            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Error","Enter a valid number")
                return
            if amount<=0:
                messagebox.showerror("Error","Amount must be positive")
                return

            if not is_add:
                if amount>balance_value:
                    messagebox.showerror("Error","Not enough balance")
                    return
                if budget_value is not None:
                    total_spent = sum(-txn["amount"] for txn in recents.values() if txn["amount"]<0)
                    new_total_spent = total_spent+amount
                    if new_total_spent>budget_value:
                        confirm = messagebox.askyesno("Confirm Overspend",f"This will exceed your budget by {new_total_spent-budget_value:,.2f} BDT. Proceed?")
                        if not confirm:
                            return
                balance_value -= amount
                transactions_change_value -= amount
            else:
                balance_value += amount
                transactions_change_value += amount

            transactions_value +=1

            txn_id = f"txn_{int(datetime.now().timestamp())}"
            recents[txn_id] = {
                "amount": amount if is_add else -amount,
                "description": desc_entry.get("1.0","end").strip(),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            balance_var.set(f"{balance_value:,.2f} BDT")
            transactions_var.set(f"{transactions_value:,}")
            sign = "+" if transactions_change_value>=0 else "-"
            transactions_change_var.set(get_top_spend_previous_month())

            saving_data(balance_value, transactions_value, transactions_change_value, recents)
            render_recent_transactions()
            render_top_spend()
            update_remaining_budget()
            render_analytics()

            popup.destroy()

        btn_frame = tk.Frame(container,bg="white")
        btn_frame.grid(row=4,column=0,sticky="ew")
        tk.Button(btn_frame,text="Submit",bg="#333333",fg="white",font=("Arial",12,"bold"),width=10,pady=10,relief="raised",cursor="hand2",command=submit_amount).pack(side="left",expand=True,padx=10)
        tk.Button(btn_frame,text="Cancel",bg="#EE2D24",fg="white",font=("Arial",12,"bold"),width=10,pady=10,relief="raised",cursor="hand2",command=popup.destroy).pack(side="right",expand=True,padx=10)
        container.columnconfigure(0,weight=1)

    def open_settings():
        popup = tk.Toplevel(root)
        popup.title("Settings")
        popup.configure(bg="white")
        popup.transient(root)
        popup.grab_set()


        width, height = 450, 600
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.resizable(False, False)

        header = tk.Label(popup, text="Settings", font=("Segoe UI", 16, "bold"), bg="white")
        header.pack(pady=(15, 10))

        notebook = ttk.Notebook(popup)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        tab1 = tk.Frame(notebook, bg="white")
        notebook.add(tab1, text="User Info")

        tk.Label(tab1, text="First Name", bg="white").pack(anchor="w", pady=(10, 2), padx=10)
        first_entry = ttk.Entry(tab1, font=("Arial", 11))
        first_entry.pack(fill="x", padx=10, pady=(0, 10))
        first_entry.insert(0, first_name)

        tk.Label(tab1, text="Last Name", bg="white").pack(anchor="w", pady=(10, 2), padx=10)
        last_entry = ttk.Entry(tab1, font=("Arial", 11))
        last_entry.pack(fill="x", padx=10, pady=(0, 10))
        last_entry.insert(0, last_name)

        tk.Label(tab1, text="Email", bg="white").pack(anchor="w", pady=(10, 2), padx=10)
        email_entry = ttk.Entry(tab1, font=("Arial", 11))
        email_entry.pack(fill="x", padx=10, pady=(0, 10))
        email_entry.insert(0, email)

        tk.Label(tab1, text="Password (leave blank to keep)", bg="white").pack(anchor="w", pady=(10, 2), padx=10)
        password_entry = ttk.Entry(tab1, font=("Arial", 11), show="*")
        password_entry.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(tab1, text="Confirm Password", bg="white").pack(anchor="w", pady=(10, 2), padx=10)
        confirm_entry = ttk.Entry(tab1, font=("Arial", 11), show="*")
        confirm_entry.pack(fill="x", padx=10, pady=(0, 15))

        tab2 = tk.Frame(notebook, bg="white")
        notebook.add(tab2, text="Budget")

        tk.Label(tab2, text="Budget Warning Threshold (BDT)", font=("Segoe UI", 11, "bold")).pack(anchor="w",
                                                                                                   pady=(15, 5),
                                                                                                   padx=10)
        warning_entry = ttk.Entry(tab2, font=("Arial", 11))
        warning_entry.pack(fill="x", padx=10, pady=(0, 15))

        current_warning = getattr(root, "budget_warning_limit", 500)
        warning_entry.insert(0, str(current_warning))

        def save_settings():
            nonlocal first_entry, last_entry, email_entry, password_entry, confirm_entry, warning_entry

            f = first_entry.get().strip()
            l = last_entry.get().strip()
            e = email_entry.get().strip()
            p = password_entry.get()
            c = confirm_entry.get()

            try:
                new_warning = float(warning_entry.get())
                if new_warning < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Warning threshold must be a positive number")
                return

            if not f or not l or not e:
                messagebox.showerror("Error", "User info fields cannot be empty")
                return

            if p or c:
                if p != c:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                password_hash = hash_password(p)
            else:
                with open(users_path, "rb") as file:
                    data = decrypt_json(file.read())
                password_hash = data[username]["password"]

            with open(users_path, "rb") as file:
                data = decrypt_json(file.read())

            data[username]["firstname"] = f
            data[username]["lastname"] = l
            data[username]["email"] = e
            data[username]["password"] = password_hash
            data[username]["budget_warning_limit"] = new_warning

            with open(users_path, "wb") as file:
                file.write(encrypt_json(data))

            global first_name, last_name, email
            first_name, last_name, email = f, l, e
            root.budget_warning_limit = new_warning
            update_remaining_budget()

            messagebox.showinfo("Success", "Settings updated successfully!")
            popup.destroy()

        save_btn = tk.Button(popup, text="Save Changes", bg="#111827", fg="white",
                             font=("Segoe UI", 11, "bold"), command=save_settings)
        save_btn.pack(fill="x", padx=15, pady=(0, 15))

    buttons = [
        ("Add Money", "#10B981", lambda:add_money_popup(True)),
        ("Remove Money","#EF4444",lambda:add_money_popup(False)),
        ("All Tranactions","#6366F1",open_recents_popup),
        ("Budget","#111827",budget_popup)
    ]

    for i,(txt,clr,fn) in enumerate(buttons):
        btn = tk.Button(btns,text=txt,bg=clr,fg="white",font=("Segoe UI",11,"bold"),
                        height=2,bd=4,relief="raised",activebackground=clr,
                        activeforeground="white",cursor="hand2",command=fn)
        btn.grid(row=0,column=i,sticky="nsew",padx=5,pady=5)
    for i in range(len(buttons)):
        btns.columnconfigure(i,weight=1)

    recent_card = create_card(content,3,0,360,170)
    top_spend_card = create_card(content,3,1,360,170)

    tk.Label(recent_card,text="Recent Transactions",bg="white",font=CARD_TITLE).pack(anchor="w",padx=15,pady=(12,6))
    recent_list = tk.Frame(recent_card,bg="white")
    recent_list.pack(fill="both",expand=True,padx=15)
    render_recent_transactions()

    tk.Label(top_spend_card,text="Top Spend",bg="white",font=CARD_TITLE).pack(anchor="w",padx=15,pady=2)
    button_frame = tk.Frame(content, bg="#F3F4F6")
    button_frame.grid(row=3, column=2, sticky="nsew", padx=12, pady=(0, 12))
    button_frame.columnconfigure((0, 1), weight=1)

    btn_settings = tk.Button(button_frame, text="Settings", bg="blue", fg="white", font=("Segoe UI", 11, "bold"),
                             height=2, bd=4, relief="raised", cursor="hand2",
                             command=open_settings)
    btn_settings.grid(row=0, column=0, sticky="nsew", padx=5)

    btn_logout = tk.Button(button_frame, text="Logout", bg="#EF4444", fg="white", font=("Segoe UI", 11, "bold"),
                           height=2, bd=4, relief="raised", cursor="hand2",
                           command=logout)
    btn_logout.grid(row=0, column=1, sticky="nsew", padx=5)

    render_top_spend()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    update_remaining_budget()
    render_analytics()

    first_login = True


    with open(users_path, "rb") as file:
        users_data = decrypt_json(file.read())

    if username in users_data:
        first_login = users_data[username].get("first_login", True)

    if first_login:
        creator_info_popup(root)
        users_data[username]["first_login"] = False
        with open(users_path, "wb") as file:
            file.write(encrypt_json(users_data))





    root.mainloop()


if __name__ == "__main__":
    dashboard_ui()