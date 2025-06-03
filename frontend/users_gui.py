from customtkinter import *
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import customtkinter as ctk
from tkinter import font

import requests

class UserManagement:
    def __init__(self, parent, token):
        self.parent = parent
        self.token = token
        self.api_base_url = "http://127.0.0.1:8000"

        # Create modal window
        self.user_management_window = CTkToplevel(self.parent)
        self.user_management_window.title("HEMS - User Management")
        self.user_management_window.geometry("750x480")
        self.user_management_window.resizable(False, False)
        self.user_management_window.configure(fg_color="#2C3E50")  # Dark background

        self.user_management_window.transient(self.parent)
        self.user_management_window.grab_set()
        self.user_management_window.focus()
        self.center_window(self.user_management_window, 750, 480)

        self.setup_widgets()
        self.fetch_users()

    def center_window(self, window, width, height, base=None):
        base = base or self.parent
        base.update_idletasks()
        x = base.winfo_rootx() + (base.winfo_width() // 2) - (width // 2)
        y = base.winfo_rooty() + (base.winfo_height() // 2) - (height // 2)  +10
        window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_widgets(self):
    # Header
        header_label = CTkLabel(
            self.user_management_window,
            text="User Management",
            font=("Segoe UI", 22, "bold"),
            fg_color="#1E2B38",  # Darker header bar
            text_color="white",
            height=45,
            corner_radius=8
        )
        header_label.pack(fill="x", padx=16, pady=(18, 10))

        # Action Buttons
        btn_frame = CTkFrame(self.user_management_window, fg_color="transparent")
        btn_frame.pack(pady=6)

        button_style = {
            "width": 110,
            "height": 30,
            "corner_radius": 10,
            "font": ("Segoe UI", 12, "bold"),
            "text_color": "white"
        }

        CTkButton(
            btn_frame, text="Add", command=self.add_user,
            fg_color="#2563EB", hover_color="#1D4ED8", **button_style
        ).grid(row=0, column=0, padx=8)

        CTkButton(
            btn_frame, text="Edit", command=self.update_user,
            fg_color="#6C757D", hover_color="#5C636A", **button_style
        ).grid(row=0, column=1, padx=8)

        CTkButton(
            btn_frame, text="Delete", command=self.delete_user,
            fg_color="#E74C3C", hover_color="#C0392B", **button_style
        ).grid(row=0, column=2, padx=8)

        # Treeview Section
        tree_frame = CTkFrame(self.user_management_window, fg_color="white", corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(12, 16))

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#2C3E50", foreground="white")
        style.map("Treeview", background=[("selected", "#2980B9")], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Role"), show="headings")
        self.tree.heading("ID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Username", width=300, anchor="center")
        self.tree.column("Role", width=150, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky="ns")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    def apply_grid_effect(self, tree=None):
        tree = tree or self.tree
        for i, item in enumerate(tree.get_children()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.item(item, tags=(tag,))
        tree.tag_configure("evenrow", background="#ecf0f1")  # Light gray
        tree.tag_configure("oddrow", background="white")

    def fetch_users(self):
        try:
            response = requests.get(f"{self.api_base_url}/users", headers={"Authorization": f"Bearer {self.token}"})
            response.raise_for_status()
            users = response.json()
            self.populate_tree(users)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch users:\n{e}")

    def populate_tree(self, users):
        self.tree.delete(*self.tree.get_children())
        for user in users:
            self.tree.insert("", "end", values=(user["id"], user["username"], user["role"]))
        self.apply_grid_effect()
        self.apply_grid_effect()


    def add_user(self):
        self.open_user_form("Add User", self.submit_new_user)

    def update_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to update.")
            return
        values = self.tree.item(selected)["values"]
        self.open_user_form("Update User", self.submit_updated_user, values)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to delete.")
            return
        username = self.tree.item(selected)["values"][1]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{username}'?"):
            try:
                response = requests.delete(f"{self.api_base_url}/users/{username}", headers={"Authorization": f"Bearer {self.token}"})
                if response.status_code == 200:
                    messagebox.showinfo("Success", "User deleted successfully.")
                    self.fetch_users()
                else:
                    messagebox.showerror("Error", response.text)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def open_user_form(self, title, callback, values=None):
        form = CTkToplevel(self.user_management_window)
        form.title(title)
        self.center_window(form, 400, 340, base=self.user_management_window)

        form.resizable(False, False)

        # Ensure the form stays on top and grabs focus
        form.transient(self.user_management_window)
        form.grab_set()
        form.focus()

        CTkLabel(form, text=title, font=("Arial", 20, "bold"), fg_color="#34495E", text_color="white").pack(pady=20)

        username_entry = CTkEntry(form, placeholder_text="Username", width=250)
        username_entry.pack(pady=8)
        if values:
            username_entry.insert(0, values[1])

        password_entry = CTkEntry(form, placeholder_text="Password", show="*", width=250)
        password_entry.pack(pady=8)

        role_combobox = CTkComboBox(form, values=["user", "admin"], width=250)
        role_combobox.pack(pady=8)
        role_combobox.set(values[2] if values else "user")

        admin_password_entry = CTkEntry(form, placeholder_text="Admin Password", show="*", width=250)

        def toggle_admin_password(role):
            if role_combobox.get() == "admin":
                admin_password_entry.pack(pady=8)
            else:
                admin_password_entry.pack_forget()

        role_combobox.configure(command=toggle_admin_password)
        if values and values[2] == "admin":
            admin_password_entry.pack(pady=8)

        CTkButton(form, text="Submit", command=lambda: callback(username_entry.get(), password_entry.get(), role_combobox.get(), admin_password_entry.get(), form), width=200, corner_radius=10, fg_color="#1ABC9C", hover_color="#16A085").pack(pady=20)

    def submit_new_user(self, username, password, role, admin_password, form):
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return
        payload = {
            "username": username,
            "password": password,
            "role": role
        }
        if role == "admin":
            payload["admin_password"] = admin_password
        try:
            res = requests.post(f"{self.api_base_url}/users/register/", json=payload, headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code in [200, 201]:
                messagebox.showinfo("Success", "User added successfully.")
                form.destroy()
                self.fetch_users()
            elif res.status_code == 409:
                messagebox.showerror("Error", "Username already exists.")
            else:
                messagebox.showerror("Error", res.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def submit_updated_user(self, username, password, role, admin_password, form):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No user selected.")
            return
        original_username = self.tree.item(selected)["values"][1]
        payload = {
            "username": username,
            "password": password,
            "role": role
        }
        if role == "admin":
            payload["admin_password"] = admin_password
        try:
            res = requests.put(f"{self.api_base_url}/users/{original_username}", json=payload, headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code == 200:
                messagebox.showinfo("Success", "User updated successfully.")
                form.destroy()
                self.fetch_users()
            else:
                messagebox.showerror("Error", res.text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

             
