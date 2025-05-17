import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import requests
import os
from dashboard import Dashboard  # Import the Dashboard class

class LoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.configure(bg="#2c3e50")

        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.api_base_url = "http://127.0.0.1:8000"
        
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#2c3e50")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_login_ui()


    

    def create_login_ui(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        frame.pack(padx=40, pady=20, fill="x", expand=True)

        ctk.CTkLabel(frame, text="Login", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=5, padx=40, fill='x')
        
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=200)
        self.password_entry.pack(pady=5, padx=40, fill='x')
        
        ctk.CTkButton(frame, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(frame, text="Don't have an account?\nRegister", command=self.create_register_ui, fg_color="gray").pack(pady=5)

    def create_register_ui(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        frame.pack(padx=40, pady=20, fill="x", expand=True)

        ctk.CTkLabel(frame, text="Register", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.reg_username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=200)
        self.reg_username_entry.pack(pady=5, padx=40, fill='x')
        
        self.reg_password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=200)
        self.reg_password_entry.pack(pady=5, padx=40, fill='x')
        
        self.role_combobox = ctk.CTkComboBox(frame, values=["user", "admin"], command=self.toggle_admin_password)
        self.role_combobox.pack(pady=5, padx=40, fill='x')
        self.role_combobox.set("user")
        
        self.admin_password_entry = ctk.CTkEntry(frame, placeholder_text="Admin Password", show="*", width=200)
        
        ctk.CTkButton(frame, text="Register", command=self.register).pack(pady=10)
        ctk.CTkButton(frame, text="Back to Login", command=self.create_login_ui, fg_color="gray").pack(pady=5)

    def toggle_admin_password(self, choice):
        if choice == "admin":
            self.admin_password_entry.pack(pady=5, padx=40, fill='x')
        else:
            self.admin_password_entry.pack_forget()

    def clear_window(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    from CTkMessagebox import CTkMessagebox

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            CTkMessagebox(title="Error", message="Please enter both username and password.", icon="cancel")
            return

        try:
            response = requests.post(f"{self.api_base_url}/users/token", data={"username": username, "password": password})
            if response.status_code == 500:
                CTkMessagebox(title="Error", message="Invalid username or password.", icon="cancel")
                return

            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")

            if token:
                msg_box = CTkMessagebox(title="Success", message="Login successful!", icon="check", option_1="OK")
                if msg_box.get() == "OK":  # Waits for user to click OK
                    self.root.destroy()
                    dashboard_root = ctk.CTk()
                    Dashboard(dashboard_root, username, token)
                    #dashboard_root.mainloop()
            else:
                CTkMessagebox(title="Error", message="Invalid response from server.", icon="cancel")
        except requests.RequestException as e:
            CTkMessagebox(title="Error", message=f"Login failed: {e}", icon="cancel")


    def register(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        role = self.role_combobox.get()
        admin_password = self.admin_password_entry.get().strip() if role == "admin" else None

        if not username or not password:
            CTkMessagebox(title="Error", message="Please enter both username and password.", icon="cancel")
            return

        if role == "admin" and not admin_password:
            CTkMessagebox(title="Error", message="Admin password is required for admin registration.", icon="cancel")
            return

        try:
            data = {"username": username, "password": password, "role": role, "admin_password": admin_password}
            response = requests.post(f"{self.api_base_url}/users/register/", json=data)

            if response.status_code == 409:  # ❌ Username already exists
                CTkMessagebox(title="Error", message="Username already exists. Please choose a different username.", icon="warning")

            elif response.ok:  # ✅ Successful registration (since backend does not return 201)
                CTkMessagebox(title="Success", message="User registered successfully!", icon="check")
                self.create_login_ui()

            else:  # ❌ Other errors
                error_message = response.json().get("detail", "Registration failed.")
                CTkMessagebox(title="Error", message=f"Error: {error_message}", icon="cancel")

        except requests.RequestException as e:
            CTkMessagebox(title="Error", message=f"Registration failed due to network error: {e}", icon="cancel")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    app = LoginGUI(root)
    root.mainloop()
