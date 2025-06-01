import tkinter as tk
from tkinter import ttk, messagebox
from users_gui import UserManagement
from rooms_gui import RoomManagement
from bookings_gui import BookingManagement
from payment_gui import PaymentManagement
from event_gui import EventManagement
from reservation_alert import ReservationAlertWindow
from utils import load_token, get_user_role
import os
from PIL import Image, ImageTk
import requests
import threading
import time
import customtkinter as ctk

class Dashboard(ctk.CTk):
    def __init__(self, root, username, token):
        super().__init__()
        self.root = root
        self.username = username
        self.token = token

        self.root.title("HEMS-Hotel & Event Management System")
        try:
            self.root.state("zoomed")
        except:
            self.root.attributes("-zoomed", True)

        self.root.configure(bg="#2c3e50")

        # Loading label
        self.loading_text = "wait...loading files.... "
        self.progress = 0
        self.max_progress = 100

        self.loading_label = tk.Label(
            self.root,
            text=self.loading_text + "0%",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        self.loading_label.pack(expand=True, fill="both")

        # Start counter animation and then load dashboard
        self.animate_loading()
        self.root.after(3000, self.load_dashboard)  # Delay before loading real UI

    def animate_loading(self):
        if self.progress <= self.max_progress:
            self.loading_label.config(text=f"{self.loading_text}{self.progress}%")
            self.progress += 1
            self.animation_job = self.root.after(30, self.animate_loading)  # ~3 seconds total
        else:
            # Once at 100%, stop animation and load dashboard
            self.load_dashboard()

    def load_dashboard(self):
        # Stop the animation if running
        if hasattr(self, 'animation_job'):
            self.root.after_cancel(self.animation_job)

        # Build actual dashboard UI
        self.build_ui()

    def build_ui(self):
        self.loading_label.destroy()

        self.user_role = get_user_role(self.token)

        # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # === HEADER ===
        self.header_shadow = tk.Frame(self.root, bg="#1a252f", height=40)
        self.header_shadow.pack(fill=tk.X)

        self.header = tk.Frame(self.root, bg="#2C3E50", height=46)
        self.header.place(relx=0, rely=0, relwidth=1)

        left_title = tk.Label(self.header, text="Dashboard", fg="white", bg="#2C3E50",
                              font=("Helvetica", 14, "bold"))
        left_title.pack(side=tk.LEFT, padx=20, pady=10)

        center_title = tk.Label(self.header, text="🏨 H E M S", fg="gold", bg="#2C3E50",
                                font=("Helvetica", 16, "bold"))
        center_title.place(relx=0.5, rely=0.5, anchor="center")

        right_title = tk.Label(self.header, text="Hotel & Event Management System", fg="white", bg="#2C3E50",
                               font=("Helvetica", 12))
        right_title.pack(side=tk.RIGHT, padx=20, pady=10)

        border = tk.Frame(self.root, bg="#1abc9c", height=2)
        border.pack(fill=tk.X)

        def on_enter(event):
            center_title.config(fg="#1abc9c")

        def on_leave(event):
            center_title.config(fg="gold")

        center_title.bind("<Enter>", on_enter)
        center_title.bind("<Leave>", on_leave)

       # === SIDEBAR ===
        self.sidebar_container = tk.Frame(self.root, bg="#2C3E50", width=100, bd=2, relief=tk.RIDGE)
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        menu_title = tk.Label(self.sidebar_container, text="MENU", fg="white", bg="#2C3E50",
                            font=("Arial", 14, "bold"))
        menu_title.pack(pady=8)

        self.sidebar = tk.Frame(self.sidebar_container, bg="#34495E", bd=2, relief=tk.GROOVE)
        self.sidebar.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # === Uniform Button Style ===
        button_font = ("Arial", 12)
        button_padx = 6
        button_pady = 6

        menu_items = [
            ("👤 Users", self.manage_users),
            ("🏨 Rooms", self.manage_rooms),
            ("📅 Bookings", self.manage_bookings),
            ("💳 Payments", self.manage_payments),
            ("🎉 Events", self.manage_events),
        ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, command=command, fg="white", bg="#2C3E50",
                            font=button_font, relief=tk.RAISED,
                            padx=button_padx, pady=button_pady, anchor="w", bd=2)
            btn.pack(fill=tk.X, pady=5, padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1ABC9C"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2C3E50"))

        # === RESERVE ALERT BUTTON ===
        self.reservation_alert_btn = tk.Button(
            self.sidebar,
            text="🔔 Reserve Alert",
            command=self.open_reservation_alert,
            fg="white", bg="#F82710",  # Red alert color
            font=button_font,
            relief=tk.RAISED,
            padx=button_padx, pady=button_pady, anchor="w", bd=2
        )
        self.reservation_alert_btn.pack(fill=tk.X, pady=5, padx=10)

        # === LOGOUT BUTTON (darker red) ===
        logout_btn = tk.Button(
            self.sidebar, text="🚪 Logout", command=self.logout, fg="white",
            bg="#641A12",  # Slightly darker red
            font=button_font, relief=tk.RAISED,
            padx=button_padx, pady=button_pady, anchor="w", bd=2
        )
        logout_btn.pack(fill=tk.X, pady=5, padx=10)

    # === RESERVATION ALERT CHECK ===
    def check_reservation_alert(self):
        try:
            response = requests.get("http://localhost:8000/bookings/reservations/alerts")
            data = response.json()
            #print("Reservation alert response:", data)  # 🔍 Add this line
            has_active = data["active_reservations"]


            if has_active:
                #print("Reservation exists - setting red")
                self.reservation_alert_btn.config(
                    bg="#E74C3C", activebackground="#E74C3C"
                )
            else:
                #print("No active reservations - setting gray")
                self.reservation_alert_btn.config(
                    bg="#7f8c8d", activebackground="#7f8c8d"
                )

            self.reservation_alert_btn.update_idletasks()

        except Exception as e:
            print("Failed to fetch reservation alert:", e)


    # === SCHEDULED PERIODIC CHECK ===
    def schedule_reservation_check(self):
        self.check_reservation_alert()
        self.root.after(1000, self.schedule_reservation_check)  # Check every 30 seconds

    # Call the scheduler once after UI is set up (outside the method)
    



    



        


    
    def manage_users(self):
        if self.user_role != "admin":
            messagebox.showerror("Access Denied", "You do not have permission to manage users.")
            return
        UserManagement(self.root, self.token)

    def manage_rooms(self):
        RoomManagement(self.root, self.token)

    def manage_bookings(self):
        BookingManagement(self.root, self.token)

    def manage_payments(self):
        PaymentManagement(self.root, self.token)

    def manage_events(self):
        EventManagement(self.root, self.token)

    def open_reservation_alert(self):
        ReservationAlertWindow(self, self.token)



    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        from login_gui import LoginGUI
        LoginGUI(root)
        root.mainloop()

if __name__ == "__main__":
    token = load_token()
    if token:
        root = tk.Tk()
        Dashboard(root, "Admin", token)
        root.mainloop()
    else:
        print("No token found. Please log in.")
