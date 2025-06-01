import customtkinter as ctk
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
import requests
import tkinter as tk  # Add this import at the top of your file


class ReservationAlertWindow(ctk.CTkToplevel):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.title("Reservation Alerts")
        self.geometry("1150x500")
        self.token = token

        self.create_ui()
        self.load_reservations()

    def create_ui(self):
        self.label = ctk.CTkLabel(self, text="🔔 Reserved Bookings", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        columns = (
            "ID", "Room No", "Guest Name", "Address", "Arrival Date", "Departure Date",
            "Booking Type", "Phone Number", "Payment Status", " Days",
            "Booking Cost", "Created By"
        )

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)  # Center the header text
            self.tree.column(col, width=90, anchor=tk.CENTER)   # Center the cell data

        self.tree.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)




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
            else:
                CTkMessagebox(title="Error", message=f"Failed to fetch reservation data: {response.status_code}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error: {e}")
