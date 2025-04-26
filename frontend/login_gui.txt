import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
from dashboard import Dashboard  # Import the Dashboard class

class LoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.configure(bg="#d3d3d3")  # Full light gray background
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.api_base_url = "http://127.0.0.1:8000"

        # Create a main frame to center the login/register form
        self.main_frame = tk.Frame(self.root, bg="#d3d3d3")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.create_login_ui()  # Show login UI initially

    def create_login_ui(self):
        """Creates the login UI with a border frame and horizontal entry fields."""
        self.clear_window()

        # Outer frame with border
        border_frame = tk.Frame(self.main_frame, bg="#555", padx=3, pady=3)  # Dark gray border
        border_frame.pack(padx=10, pady=10)

        # Inner white frame for form
        frame = tk.Frame(border_frame, bg="white", padx=10, pady=10, relief="ridge", bd=5, width=400)
        frame.pack()

        tk.Label(frame, text="Login", font=("Arial", 14, "bold"), fg="white", bg="#2c3e50", pady=8).pack(fill=tk.X)

        form_frame = tk.Frame(frame, bg="white")
        form_frame.pack(pady=5)

        # Username Row (Label + Entry in One Line)
        row1 = tk.Frame(form_frame, bg="white")
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Username:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="w").pack(side=tk.LEFT)
        self.username_entry = tk.Entry(row1, font=("Arial", 11), width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)

        # Password Row (Label + Entry in One Line)
        row2 = tk.Frame(form_frame, bg="white")
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Password:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="w").pack(side=tk.LEFT)
        self.password_entry = tk.Entry(row2, font=("Arial", 11), width=20, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame, text="Login", command=self.login, style="Bold.TButton").pack(pady=10)
        tk.Button(frame, text="Register", command=self.create_register_ui, fg="blue", bg="white", borderwidth=0, font=("Arial", 10, "underline")).pack()

    def create_register_ui(self):
        """Creates the register UI with a border frame and horizontal entry fields."""
        self.clear_window()

        border_frame = tk.Frame(self.main_frame, bg="#555", padx=3, pady=3)  # Dark gray border
        border_frame.pack(padx=10, pady=10)

        frame = tk.Frame(border_frame, bg="white", padx=10, pady=10, relief="ridge", bd=5, width=400)
        frame.pack()

        tk.Label(frame, text="Register", font=("Arial", 14, "bold"), fg="white", bg="#2c3e50", pady=8).pack(fill=tk.X)

        form_frame = tk.Frame(frame, bg="white")
        form_frame.pack(pady=5)

        # Username Row
        row1 = tk.Frame(form_frame, bg="white")
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Username:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="w").pack(side=tk.LEFT)
        self.reg_username_entry = tk.Entry(row1, font=("Arial", 11), width=20)
        self.reg_username_entry.pack(side=tk.LEFT, padx=5)

        # Password Row
        row2 = tk.Frame(form_frame, bg="white")
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Password:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="w").pack(side=tk.LEFT)
        self.reg_password_entry = tk.Entry(row2, font=("Arial", 11), width=20, show="*")
        self.reg_password_entry.pack(side=tk.LEFT, padx=5)

        # Role Row
        row3 = tk.Frame(form_frame, bg="white")
        row3.pack(fill=tk.X, pady=5)
        tk.Label(row3, text="Role:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="w").pack(side=tk.LEFT)
        self.role_combobox = ttk.Combobox(row3, values=["user", "admin"], state="readonly", font=("Arial", 11), width=15)
        self.role_combobox.pack(side=tk.LEFT, padx=5)
        self.role_combobox.current(0)
        self.role_combobox.bind("<<ComboboxSelected>>", self.toggle_admin_password)

        # Admin Password (Initially Hidden)
        self.admin_password_label = tk.Label(form_frame, text="Admin Password:", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50")
        self.reg_admin_password_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, show="*")

        ttk.Button(frame, text="Register", command=self.register, style="Bold.TButton").pack(pady=10)
        tk.Button(frame, text="Back to Login", command=self.create_login_ui, fg="blue", bg="white", borderwidth=0, font=("Arial", 10, "underline")).pack()

    def toggle_admin_password(self, event):
        """Toggles admin password field visibility."""
        if self.role_combobox.get() == "admin":
            self.admin_password_label.pack(anchor="w")
            self.reg_admin_password_entry.pack(pady=5)
        else:
            self.admin_password_label.pack_forget()
            self.reg_admin_password_entry.pack_forget()

    def clear_window(self):
        """Clears all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def login(self):
        """Handles login."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        try:
            response = requests.post(f"{self.api_base_url}/users/token", data={"username": username, "password": password})

            if response.status_code == 500:
                messagebox.showerror("Error", "Invalid username or password.")
                return

            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")

            if token:
                messagebox.showinfo("Success", "Login successful!")
                self.root.destroy()
                dashboard_root = tk.Tk()
                Dashboard(dashboard_root, username, token)
                dashboard_root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid response from server.")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def register(self):
        """Handles user registration."""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        role = self.role_combobox.get()
        admin_password = self.reg_admin_password_entry.get() if role == "admin" else None

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if role == "admin" and not admin_password:
            messagebox.showerror("Error", "Admin password is required for admin registration.")
            return

        try:
            data = {"username": username, "password": password, "role": role, "admin_password": admin_password}
            response = requests.post(f"{self.api_base_url}/users/register/", json=data)

            if response.status_code == 400:
                messagebox.showerror("Error", "Username already exists.")
                return

            if response.status_code == 403:
                messagebox.showerror("Error", "Invalid admin password.")
                return

            response.raise_for_status()
            messagebox.showinfo("Success", "User registered successfully!")
            self.create_login_ui()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Registration failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginGUI(root)
    root.mainloop()
