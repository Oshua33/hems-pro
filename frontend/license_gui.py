import tkinter as tk
from CTkMessagebox import CTkMessagebox
import requests
from login_gui import LoginGUI
from PIL import Image, ImageTk
import os

API_URL = "http://127.0.0.1:8000/license"

class LicenseGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("License & Welcome")
        self.state('zoomed')
        self.configure(bg="#2C3E50")

        # Icon Setup
        icon_ico_path = os.path.abspath("frontend/icon.ico").replace("\\", "/")
        icon_png_path = os.path.abspath("frontend/icon.png").replace("\\", "/")

        if os.path.exists(icon_ico_path):
            self.iconbitmap(icon_ico_path)
        elif os.path.exists(icon_png_path):
            try:
                icon_img = Image.open(icon_png_path)
                icon_resized = icon_img.resize((80, 80))
                self.icon_image = ImageTk.PhotoImage(icon_resized)
                self.iconphoto(True, self.icon_image)
            except Exception as e:
                print(f"Error loading PNG icon: {e}")
        else:
            print("Error: Icon file not found!")

        # License Frame
        self.license_frame = tk.Frame(self, bg="#34495E", padx=40, pady=30)
        self.license_frame.place(relx=0.5, rely=0.45, anchor="center", width=500, height=380)

        self.add_label("Admin License Password:")
        self.password_entry = self.create_entry(show="*")

        self.add_label("License Key:")
        self.key_entry = self.create_entry()

        self.create_button("Generate License", self.generate_license)

        self.add_label("Enter License Key to Verify:")
        self.verify_key_entry = self.create_entry()

        self.create_button("Verify License", self.verify_license)

        # Welcome Text
        tk.Label(self, text="✦  W E L C O M E  TO  HEMS✦\nHotel & Event Management System",
                 font=("Century Gothic", 24, "bold"), fg="white", bg="#2C3E50",
                 padx=10, pady=5).place(relx=0.5, rely=0.08, anchor="n")

        tk.Label(self, text="Produced & Licensed by School of Accounting Package",
                 font=("Arial", 10, "italic"), fg="white", bg="#2C3E50").place(relx=0.8, rely=0.94, anchor="n")

        tk.Label(self, text="© 2025",
                 font=("Arial", 10, "italic"), fg="white", bg="#2C3E50").place(relx=0.85, rely=0.97, anchor="n")

    def add_label(self, text):
        tk.Label(self.license_frame, text=text, font=("Arial", 12, "bold"),
                 fg="white", bg="#34495E").pack(padx=5, pady=(10, 2))

    def create_entry(self, show=None):
        entry = tk.Entry(self.license_frame, width=25, font=("Arial", 12),
                        bg="#ECF0F1", fg="black", show=show if show else "")
        entry.pack(padx=5, pady=5)

        # Hover effects
        def on_enter(e):
            entry.config(bg="#A2D9CE")  # Lighter teal color on hover

        def on_leave(e):
            entry.config(bg="#ECF0F1")  # Original color

        entry.bind("<Enter>", on_enter)
        entry.bind("<Leave>", on_leave)

        return entry

    def create_button(self, text, command):
        btn = tk.Label(self.license_frame, text=text, font=("Arial", 12, "bold"),
                    bg="#1ABC9C", fg="white", padx=10, pady=5,
                    relief="flat", bd=0, cursor="hand2")
        btn.pack(pady=10)

        # Hover effect
        def on_enter(e):
            btn.config(bg="#16A085")  # Darker teal on hover

        def on_leave(e):
            btn.config(bg="#1ABC9C")  # Original color

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", lambda e: command())  # Click action

        return btn
        
        

    def generate_license(self):
        license_password = self.password_entry.get()
        key = self.key_entry.get()

        if not license_password or not key:
            CTkMessagebox(title="Input Error", message="Please enter both license password and key.", icon="cancel")
            return

        try:
            response = requests.post(
                f"{API_URL}/generate?license_password={license_password}&key={key}",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            new_license = response.json()
            CTkMessagebox(title="License Generated", message=f"New License Key: {new_license['key']}", icon="check")

        except requests.exceptions.HTTPError as err:
            if response.status_code == 400:
                error_message = response.json().get("detail", "License key already exists.")
                CTkMessagebox(title="Error", message=error_message, icon="cancel")
            elif response.status_code == 403:
                CTkMessagebox(title="Error", message="Invalid license password.", icon="cancel")
            else:
                CTkMessagebox(title="Error", message=f"HTTP Error: {response.status_code} - {response.text}", icon="cancel")

        except requests.exceptions.RequestException as e:
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")

    def verify_license(self):
        key = self.verify_key_entry.get()

        if not key:
            CTkMessagebox(title="Input Error", message="Please enter a license key.", icon="cancel")
            return

        try:
            response = requests.get(f"{API_URL}/verify/{key}")
            response.raise_for_status()
            result = response.json()

            if result["valid"]:
                msg = CTkMessagebox(title="License Valid",
                                    message="The license key is valid!",
                                    icon="check",
                                    option_1="OK")
                if msg.get() == "OK":
                    self.destroy()
                    login_window = tk.Toplevel(self.master)
                    LoginGUI(login_window)
            else:
                CTkMessagebox(title="Invalid License", message=result["message"], icon="warning")

        except requests.exceptions.HTTPError:
            CTkMessagebox(title="Error", message="Invalid license key", icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")

# Main Execution
root = tk.Tk()
root.withdraw()
license_splash = LicenseGUI(root)
root.mainloop()
