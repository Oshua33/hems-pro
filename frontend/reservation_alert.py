import customtkinter as ctk
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
import requests
import tkinter as tk  # Add this import at the top of your file
import requests


class ReservationAlertWindow(ctk.CTkToplevel):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.title("Reservation Alerts")
        self.geometry("1000x500")
        self.token = token

        self.create_ui()
        self.load_reservations()


    def apply_grid_effect(self, tree=None):
        if tree is None:
            tree = self.tree  # Default to main tree if none is provided

        for i, item in enumerate(tree.get_children()):
            # Get existing tags as a list
            existing_tags = list(tree.item(item, "tags"))
            
            # Remove any old 'evenrow' or 'oddrow' tags first (optional cleanup)
            existing_tags = [tag for tag in existing_tags if tag not in ("evenrow", "oddrow")]

            # Append the new tag
            if i % 2 == 0:
                existing_tags.append("evenrow")
            else:
                existing_tags.append("oddrow")

            # Set the updated tags back on the item
            tree.item(item, tags=existing_tags)

        # Configure tag styles for background colors only
        tree.tag_configure("evenrow", background="#d9d9d9")  # medium gray
        tree.tag_configure("oddrow", background="white")
    

    def create_ui(self):
        # 🔹 Set main background color (light grayish-blue for contrast)
        self.configure(fg_color="#ecf0f3")  # Soft neutral background

        # 🔹 Title Label
        self.label = ctk.CTkLabel(
            self,
            text="🔔 Reserved Bookings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2c3e50"  # Deep blue-gray
        )
        self.label.pack(pady=(20, 10))

        # 🔹 Table container with card style
        table_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="white",
            border_color="#d1d9e6",  # Soft border
            border_width=2
        )
        table_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # 🔹 Define table columns
        columns = (
            "ID", "Room No", "Guest Name", "Address", "Arrival Date", "Departure Date",
            "Booking Type", "Phone Number", "Payment", "Days",
            "Booking Cost", "Created By"
        )

        # 🔹 Apply style to Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        background="#dfe6ed",  # Light header background
                        foreground="#2c3e50")  # Darker text
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=30,
                        background="white",
                        foreground="#34495e",
                        fieldbackground="white",
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#d0e7f9")])

        # 🔹 Treeview Widget
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER, width=75)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        # 🔹 Vertical scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", pady=8)
        self.tree.configure(yscrollcommand=scrollbar.set)


        
    def load_reservations(self):
        url = "http://127.0.0.1:8000/bookings/reservation-alerts"  # Updated to match backend prefix
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Clear existing tree rows before inserting new data
                for row in self.tree.get_children():
                    self.tree.delete(row)
                for item in data:
                    self.tree.insert("", "end", values=(
                        item.get("id", ""),
                        item.get("room_number", ""),
                        item.get("guest_name", ""),
                        item.get("address", ""),
                        item.get("arrival_date", ""),
                        item.get("departure_date", ""),
                        item.get("booking_type", ""),
                        item.get("phone_number", ""),
                        item.get("payment_status", ""),
                        item.get("number_of_days", ""),
                        item.get("booking_cost", ""),
                        item.get("created_by", "")
                    ))

                    self.apply_grid_effect()
            else:
                CTkMessagebox(title="Error", message=f"Failed to fetch reservation data: {response.status_code}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error: {e}")


    

    
