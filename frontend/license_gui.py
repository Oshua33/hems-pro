import tkinter as tk
from CTkMessagebox import CTkMessagebox
import requests
from login_gui import LoginGUI
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
import math
import tkinter.messagebox as tkmb  # at the top of your file



import os

API_URL = "http://127.0.0.1:8000/license"


class LicenseGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("HEMS License Portal")
        self.state('zoomed')
        self.configure(bg="#2C3E50")



        # Initialize containers
        self.bg_lines = []
        self.ribbon_stripes = []

        # Background Canvas - full screen
        self.bg_canvas = tk.Canvas(self, bg="#2C3E50", highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Ribbon Canvas - full screen (to allow bottom & top movement)
        self.ribbon_canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(),
                                    highlightthickness=0, bd=0, bg="#2C3E50")
        self.ribbon_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Create background lines and animated ribbons
        self.create_moving_background()
        self.animate_background()
        self.animate_ribbon()

        # Set icon
        self.set_icon()

        # UI layers (always on top of canvas)
        self.create_top_menu()
        self.create_branding_labels()
        self.create_footer()

        # Central content frame (above all)
        self.license_frame = tk.Frame(self, bg="#34495E")
        self.license_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome screen shown on launch
        self.show_welcome_screen()

    def set_icon(self):
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

    def create_moving_background(self):
        self.bg_lines.clear()
        self.ribbon_stripes.clear()

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.bg_canvas.delete("all")
        self.ribbon_canvas.delete("all")

        # Diagonal background lines (shortened to avoid covering bottom ribbons)
        for i in range(0, width + 300, 80):
            line = self.bg_canvas.create_line(
                i, 0, i - 200, height - 200,  # shorten here
                fill="#95A5A6", width=1
            )
            self.bg_lines.append(line)

        # Ribbon stripe parameters
        num_stripes = 5
        self.ribbon_width = 150
        self.ribbon_height = 50
        spacing = self.ribbon_width + 100

        # Top wave-shaped ribbon polygons
        for i in range(num_stripes):
            x = width + (i * spacing)
            y = int(height * 0.2) + i * 30

            stripe = self.ribbon_canvas.create_polygon(
                x, y,
                x + self.ribbon_width, y,
                x + self.ribbon_width - 30, y + self.ribbon_height,
                x - 30, y + self.ribbon_height,
                smooth=True, fill="#1ABC9C", outline=""
            )
            self.ribbon_stripes.append(stripe)

        # Bottom wave-shaped ribbon polygons
        for i in range(num_stripes):
            x = width + (i * spacing)
            y = int(height * 0.88) + (i * 10)

            stripe = self.ribbon_canvas.create_polygon(
                x, y,
                x + self.ribbon_width, y,
                x + self.ribbon_width - 30, y + self.ribbon_height,
                x - 30, y + self.ribbon_height,
                smooth=True, fill="#3498DB", outline=""
            )
            self.ribbon_stripes.append(stripe)

        self.ribbon_canvas.update()
        self.wave_phase = 0
        self.ribbon_speed = 4



    def animate_background(self):
        for line in self.bg_lines:
            self.bg_canvas.move(line, 0.8, 0)
            coords = self.bg_canvas.coords(line)
            if coords[0] > self.winfo_screenwidth():
                self.bg_canvas.move(line, -self.winfo_screenwidth() - 300, 0)
        self.after(33, self.animate_background)


    def animate_ribbon(self):
        half = len(self.ribbon_stripes) // 2
        screen_width = self.winfo_screenwidth()

        for i, stripe in enumerate(self.ribbon_stripes):
            self.ribbon_canvas.move(stripe, -self.ribbon_speed, 0)
            coords = self.ribbon_canvas.coords(stripe)

            if coords:
                if i < half:
                    dy = 3 * math.sin(self.wave_phase + coords[0] * 0.015)
                else:
                    dy = -3 * math.sin(self.wave_phase + coords[0] * 0.015)

                self.ribbon_canvas.move(stripe, 0, dy)

                if coords[0] + self.ribbon_width < 0:
                    self.ribbon_canvas.move(stripe, screen_width + self.ribbon_width, 0)

        self.wave_phase += 0.08
        self.after(40, self.animate_ribbon)

    def create_top_menu(self):
        menu_frame = tk.Frame(self, bg="#1ABC9C", height=50)
        menu_frame.pack(fill="x", side="top")

        options = [
            ("Home", self.show_welcome_screen),
            ("Generate Key", self.show_create_license),
            ("Verify Key", self.show_verify_key),
            ("Exit", self.destroy)
        ]

        for text, command in options:
            btn = tk.Button(menu_frame, text=text, font=("Arial", 12, "bold"),
                            bg="#1ABC9C", fg="white", bd=0,
                            activebackground="#16A085", command=command)
            btn.pack(side="left", padx=20, pady=10)

            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#16A085"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#1ABC9C"))

    def create_branding_labels(self):
        ctk.CTkLabel(self, text="H     E     M     S",
                     font=ctk.CTkFont("Century Gothic", 38, "bold"),
                     text_color="white", fg_color="#2C3E50").place(relx=0.5, rely=0.15, anchor="center")

        ctk.CTkLabel(self, text="Hotel & Event Management System",
                     font=ctk.CTkFont("Century Gothic", 20, "bold"),
                     text_color="gold", fg_color="#2C3E50").place(relx=0.5, rely=0.21, anchor="center")

    def create_footer(self):
        tk.Label(self, text="Produced & Licensed by School of Accounting Package",
                 font=("Arial", 10, "italic"), fg="white", bg="#2C3E50").place(relx=0.8, rely=0.94, anchor="n")
        tk.Label(self, text="© 2025", font=("Arial", 10, "italic"),
                 fg="white", bg="#2C3E50").place(relx=0.85, rely=0.97, anchor="n")

    def clear_license_frame(self):
        if self.license_frame:
            self.license_frame.destroy()
            self.license_frame = None



    def show_welcome_screen(self):
        self.clear_license_frame()

        self.license_frame = tk.Frame(self, bg="#34495E")
        self.license_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Optional: background or shadow layer for frame contrast
        shadow_frame = ctk.CTkFrame(
            self.license_frame,
            fg_color="#1a252f",  # darker background for shadow effect
            corner_radius=20
        )
        shadow_frame.pack(expand=True, padx=44, pady=44)  # slightly more than the main frame to create a visible edge

        # Main welcome card with more visible border
        welcome_card = ctk.CTkFrame(
            shadow_frame,
            fg_color="#2C3E50",
            corner_radius=20,
            border_color="#1ABC9C",
            border_width=4  # increase border thickness
        )
        welcome_card.pack(expand=True, fill="both", padx=0, pady=0)

        # Add HEMS Title
        ctk.CTkLabel(
            welcome_card,
            text="Welcome to HEMS License Portal",
            font=ctk.CTkFont("Century Gothic", 24, "bold"),
            text_color="white"
        ).pack(pady=(30, 10))

        # Subtitle
        ctk.CTkLabel(
            welcome_card,
            text="Hotel & Event Management System",
            font=ctk.CTkFont("Bahnschrift SemiBold", 16),
            text_color="#f1c40f"
        ).pack(pady=(0, 20))

        # Welcome Message
        ctk.CTkLabel(
            welcome_card,
            text=(
                "Streamline your hospitality operations .\n"
                "with our all-in-one system.\n"
                "Maximize efficiency \n"
                "And \n"
                "amplify your guest experience with HEMS."
            ),
            font=ctk.CTkFont("Arial", 14),
            text_color="white",
            justify="center"
        ).pack(padx=20, pady=10)

        # Start Button
        ctk.CTkButton(
            welcome_card,
            text="Get Started",
            command=self.show_verify_key,
            font=ctk.CTkFont("Arial", 14, "bold"),
            corner_radius=10,
            fg_color="#1ABC9C",
            hover_color="#16A085",
            text_color="white",
            width=150
        ).pack(pady=(20, 30))

        self.license_frame.lift()


    def show_create_license(self):
        self.clear_license_frame()

        # Clear previous license frame if it exists
        if hasattr(self, 'license_frame') and self.license_frame:
            self.license_frame.destroy()

        # Outer frame with a darker background for contrast
        self.license_frame = ctk.CTkFrame(self, fg_color="#22313F", corner_radius=15)
        self.license_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Inner card container with lighter color
        form_card = ctk.CTkFrame(self.license_frame, fg_color="#2C3E50", corner_radius=12)
        form_card.pack(padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            form_card,
            text="Generate License Key",
            font=ctk.CTkFont("Segoe UI", 22, "bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        # Admin Password Label & Entry
        ctk.CTkLabel(
            form_card,
            text="Admin License Password",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(10, 2))

        self.password_entry = ctk.CTkEntry(form_card, show="*", width=300)
        self.password_entry.pack(padx=20, pady=5)

        # License Key Label & Entry
        ctk.CTkLabel(
            form_card,
            text="License Key",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(10, 2))

        self.key_entry = ctk.CTkEntry(form_card, width=300)
        self.key_entry.pack(padx=20, pady=5)

        # Submit Button
        ctk.CTkButton(
            form_card,
            text="Generate License",
            command=self.generate_license,
            fg_color="#1ABC9C",
            hover_color="#16A085",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            width=180
        ).pack(pady=20)

        # Raise frame above background
        self.license_frame.lift()





    def show_verify_key(self):
        self.clear_license_frame()

        # Outer frame with a subtle but visible background contrast
        self.license_frame = ctk.CTkFrame(self, fg_color="#22313F", corner_radius=15)
        self.license_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Inner card with a lighter shade for contrast
        verify_card = ctk.CTkFrame(self.license_frame, fg_color="#2C3E50", corner_radius=12)
        verify_card.pack(padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            verify_card,
            text="Verify License Key",
            font=ctk.CTkFont("Segoe UI", 22, "bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        # Label
        ctk.CTkLabel(
            verify_card,
            text="Enter License Key",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(10, 2))

        # Entry
        self.verify_entry = ctk.CTkEntry(verify_card, width=300)
        self.verify_entry.pack(padx=20, pady=5)

        # Button
        ctk.CTkButton(
            verify_card,
            text="Verify Key",
            command=self.verify_license,
            fg_color="#1ABC9C",
            hover_color="#16A085",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            width=180
        ).pack(pady=20)

        # Raise frame above background
        self.license_frame.lift()


    # --- UI helpers ---
    def add_label(self, text):
        tk.Label(self.license_frame, text=text, font=("Arial", 12, "bold"),
                 fg="white", bg="#34495E").pack(padx=5, pady=(10, 2))

    def create_entry(self, show=None):
        entry = tk.Entry(self.license_frame, width=25, font=("Arial", 12),
                         bg="#ECF0F1", fg="black", show=show if show else "")
        entry.pack(padx=5, pady=5)
        return entry

    def create_rounded_button(self, text, command):
        btn = ctk.CTkButton(self.license_frame, text=text, command=command,
                            fg_color="#1ABC9C", hover_color="#16A085", width=200, height=40)
        btn.pack(pady=(20, 10))

    # --- Placeholder logic for buttons ---
    def generate_license(self):
        license_password = self.password_entry.get()
        key = self.key_entry.get()

        if not license_password or not key:
            CTkMessagebox(
                title="Input Error",
                message="Please enter both license password and key.",
                icon="cancel"
            )
            return

        try:
            response = requests.post(
                f"{API_URL}/generate?license_password={license_password}&key={key}",
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 409:
                CTkMessagebox(
                    title="Key Already Exists",
                    message="This license key is already in use.",
                    icon="cancel"
                )
                return

            response.raise_for_status()
            new_license = response.json()

            # Wait for user to click "OK" before going back to welcome screen
            msg = CTkMessagebox(
                title="License Generated",
                message=f"New License Key: {new_license['key']}",
                icon="check",
                option_1="OK"
            )

            if msg.get() == "OK":
                self.show_welcome_screen()

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get("detail", "").lower():
                    CTkMessagebox(
                        title="Duplicate Key",
                        message="The license key you entered already exists.",
                        icon="cancel"
                    )
                else:
                    CTkMessagebox(
                        title="Error",
                        message=error_data.get("detail", "An error occurred."),
                        icon="cancel"
                    )
            else:
                CTkMessagebox(title="Error", message="Invalid Admin Password", icon="cancel")

        except requests.exceptions.RequestException:
            CTkMessagebox(title="Connection Error", message="Failed to reach the server.", icon="cancel")


    def create_verify_license_form(self):  
        self.clear_license_frame()

        # Title
        title = ctk.CTkLabel(self.license_frame, text="Verify License Key", font=("Arial", 18, "bold"), text_color="white")
        title.pack(pady=20)

        # Entry for Key
        self.verify_key_entry = ctk.CTkEntry(self.license_frame, placeholder_text="Enter license key")
        self.verify_key_entry.pack(pady=10, ipady=5, ipadx=50)

        # Button to verify
        self.create_rounded_button("Verify Key", self.verify_license)
     

    def verify_license(self):
        key = self.verify_entry.get()
        if not key:
            CTkMessagebox(title="Input Error", message="Please enter a license key.", icon="cancel")
            return
        try:
            response = requests.get(f"{API_URL}/verify/{key}")
            response.raise_for_status()
            result = response.json()

            if result.get("valid"):
                msg = CTkMessagebox(
                    title="License Valid",
                    message="The license key is valid!",
                    icon="check",
                    option_1="OK"
                )
                if msg.get() == "OK":
                    self.destroy()
                    login_window = tk.Toplevel(self.master)
                    LoginGUI(login_window)
            else:
                CTkMessagebox(title="Invalid License", message=result.get("message", "Invalid license key."), icon="warning")

        except Exception as e:
            CTkMessagebox(title="Error",  message="Invalid license key.", icon="cancel")

    def create_rounded_button(self, text, command):
        button = ctk.CTkButton(self.license_frame, text=text,
                            command=command,
                            font=("Arial", 12, "bold"),
                            fg_color="#1ABC9C",
                            hover_color="#16A085",
                            text_color="white",
                            corner_radius=12,
                            width=180,
                            height=40)
        button.pack(pady=10)
        return button





# Main Execution
root = tk.Tk()
root.withdraw()
license_splash = LicenseGUI(root)
root.mainloop()
