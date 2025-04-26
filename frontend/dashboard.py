import tkinter as tk
from tkinter import ttk, messagebox
from users_gui import UserManagement
from rooms_gui import RoomManagement
from bookings_gui import BookingManagement
from payment_gui import PaymentManagement
from event_gui import EventManagement  
from utils import load_token, get_user_role
import os
from PIL import Image, ImageTk

class Dashboard:
    def __init__(self, root, username, token):
        #self.root = tk.Toplevel(root)
        self.root = root
        self.tree = ttk.Treeview(self.root)
        self.token = token
        self.username = username
        #self.root.state("zoomed")
        self.root.title("Hotel & Event Management System")
        #self.root.geometry("1280x900")
         # Maximize the window properly
        self.root.after(100, lambda: self.root.state("zoomed"))  # Ensures full zoom

        
        self.user_role = get_user_role(self.token)

        # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # HEADER FRAME
        self.header = tk.Frame(self.root,  bg="#1E3C72", height=60)
        self.header.pack(fill=tk.X)

        title_label = tk.Label(self.header, text="Dashboard                                                                             HEMS    🏨Hotel & Event Management System", fg="gold", bg="#1E3C72", 
                               font=("Arial", 14, "bold"), )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # SIDEBAR CONTAINER FRAME
        self.sidebar_container = tk.Frame(self.root, bg="#2C3E50", width=220, bd=2, relief=tk.RIDGE)
        self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # SIDEBAR MENU TITLE
        menu_title = tk.Label(self.sidebar_container, text="MENU", fg="white", bg="#2C3E50", 
                               font=("Arial", 14, "bold"))
        menu_title.pack(pady=10)

        # SIDEBAR FRAME (Inside Container)
        self.sidebar = tk.Frame(self.sidebar_container, bg="#34495E", bd=2, relief=tk.GROOVE)
        self.sidebar.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # MENU BUTTONS IN SIDEBAR WITH SYMBOLS
        menu_items = [
            ("👤 Users", self.manage_users),         # User icon
            ("🏨 Rooms", self.manage_rooms),         # Hotel/room icon
            ("📅 Bookings", self.manage_bookings),   # Calendar/booking icon
            ("💳 Payments", self.manage_payments),   # Credit card/payment icon
            ("🎉 Events", self.manage_events),       # Celebration/event icon
        ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, command=command, fg="white", bg="#2C3E50",
                            font=("Arial", 12), relief=tk.RAISED, padx=10, pady=8, anchor="w", bd=2)
            btn.pack(fill=tk.X, pady=5, padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1ABC9C"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2C3E50"))

        # LOGOUT BUTTON (Under "Events" in Sidebar)
        logout_btn = tk.Button(self.sidebar, text="🚪 Logout", command=self.logout, fg="white", 
                               bg="#E74C3C", font=("Arial", 12), relief=tk.RAISED, padx=10, pady=8, anchor="w", bd=2)
        logout_btn.pack(fill=tk.X, pady=20, padx=10)
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#C0392B"))  # Darker red on hover
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="#E74C3C"))  # Back to default

        # MAIN CONTENT FRAME
        self.main_content = tk.Frame(self.root, bg="#ECF0F1", bd=5, relief=tk.RIDGE)
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        welcome_label = tk.Label(self.main_content, text="Welcome, {}".format(self.username), 
                                 fg="#2C3E50", bg="#ECF0F1", font=("Arial", 14, "bold"))
        welcome_label.pack(pady=20)

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
        """Opens the Event Management window"""
        EventManagement(self.root, self.token)

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
        Dashboard(root, token)
        root.mainloop()
    else:
        print("No token found. Please log in.")
