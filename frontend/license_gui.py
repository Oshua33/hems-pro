import tkinter as tk
from CTkMessagebox import CTkMessagebox
import requests
from login_gui import LoginGUI
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
import math



import os

API_URL = "http://127.0.0.1:8000/license"


class LicenseGUI(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("License & Welcome")
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

        # License Frame (Define this BEFORE using it)
        self.license_frame = tk.Frame(self, bg="#34495E", padx=40, pady=30)
        self.license_frame.place(relx=0.5, rely=0.45, anchor="center", width=500, height=385)

        # Add labels and entries AFTER license_frame is defined
        self.add_label("Admin License Password:")
        self.password_entry = self.create_entry(show="*")

        self.add_label("License Key:")
        self.key_entry = self.create_entry()

        self.create_rounded_button("Generate License", self.generate_license)

        self.add_label("Enter License Key to Verify:")
        self.verify_key_entry = self.create_entry()

        self.create_rounded_button("Verify License", self.verify_license)

        # Labels & Branding
        ctk.CTkLabel(self, text="", font=ctk.CTkFont("Century Gothic", 20, "bold"),
                     text_color="white", fg_color="#2C3E50", anchor="center").place(relx=0.5, rely=0.05, anchor="n")

        ctk.CTkLabel(self, text="H     E     M     S",
                     font=ctk.CTkFont("Century Gothic", 32, "bold"),
                     text_color="white", fg_color="#2C3E50", anchor="center").place(relx=0.5, rely=0.11, anchor="n")

        ctk.CTkLabel(self, text="Hotel & Event Management System",
                     font=ctk.CTkFont("Century Gothic", 18, "bold"),
                     text_color="gold", fg_color="#2C3E50", anchor="center").place(relx=0.5, rely=0.17, anchor="n")

        tk.Label(self, text="Produced & Licensed by School of Accounting Package",
                 font=("Arial", 10, "italic"), fg="white", bg="#2C3E50").place(relx=0.8, rely=0.94, anchor="n")

        tk.Label(self, text="© 2025", font=("Arial", 10, "italic"),
                 fg="white", bg="#2C3E50").place(relx=0.85, rely=0.97, anchor="n")

        self.ribbon_canvas.master.tkraise(self.ribbon_canvas)
        self.license_frame.master.tkraise(self.license_frame)





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
        self.ribbon_speed = 3.5



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

    def create_rounded_button(self, text, command):
        button = RoundedButton(self.license_frame, text=text, command=command, 
                               radius=12, padding=10, color="#1ABC9C", hover_color="#16A085", 
                               text_color="white", font=("Arial", 12, "bold"), border_color="#16A085", border_width=2)
        button.pack(pady=10)

        return button

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
                print(f"HTTP Error 400: {error_message}")
                CTkMessagebox(title="Error", message=error_message, icon="cancel")
            elif response.status_code == 403:
                CTkMessagebox(title="Error", message="Invalid license password.", icon="cancel")
            else:
                print(f"HTTP Error: {response.status_code} - {response.text}")
                CTkMessagebox(title="Error", message=f"HTTP Error: {response.status_code} - {response.text}", icon="cancel")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel")
        except Exception as e:
            print(f"Unexpected error: {e}")
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
                print(f"Invalid License: {result['message']}")
                CTkMessagebox(title="Invalid License", message=result["message"], icon="warning")

        except requests.exceptions.HTTPError:
            print("Invalid license key")
            CTkMessagebox(title="Error", message="Invalid license key", icon="cancel")
        except Exception as e:
            print(f"Unexpected error: {e}")
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=12, padding=5, 
                 color="#34495E", hover_color="#1ABC9C", text_color="white", 
                 font=("Helvetica", 10), border_color="#16A085", border_width=2):
        self.command = command  # Store the command to execute when the button is clicked
        self.radius = radius
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.padding = padding
        self.font = font
        self.text = text
        self.border_color = border_color
        self.border_width = border_width
        
        # Adjusted button size
        self.width = 200  # Wider width for better alignment with your text
        self.height = 40  # Adjusted height for better appearance

        super().__init__(parent, width=self.width, height=self.height, bg=parent["bg"], highlightthickness=0)

        # Draw rounded rectangle and text
        self.rounded_rect = self.create_round_rect(5, 5, self.width-5, self.height-5, self.radius, fill=self.color, outline=self.border_color, width=self.border_width)
        self.text_id = self.create_text(self.width//2, self.height//2, text=self.text, fill=self.text_color, font=self.font)

        # Bind Events
        self.tag_bind(self.rounded_rect, "<Enter>", self.on_enter)
        self.tag_bind(self.rounded_rect, "<Leave>", self.on_leave)
        self.tag_bind(self.rounded_rect, "<Button-1>", self.on_click)
        self.tag_bind(self.text_id, "<Enter>", self.on_enter)
        self.tag_bind(self.text_id, "<Leave>", self.on_leave)
        self.tag_bind(self.text_id, "<Button-1>", self.on_click)

    def create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def on_enter(self, event=None):
        self.itemconfig(self.rounded_rect, fill=self.hover_color)

    def on_leave(self, event=None):
        self.itemconfig(self.rounded_rect, fill=self.color)

    def on_click(self, event=None):
        if self.command:
            self.command()  # Trigger the command when the button is clicked




# Main Execution
root = tk.Tk()
root.withdraw()
license_splash = LicenseGUI(root)
root.mainloop()
