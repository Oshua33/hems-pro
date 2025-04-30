import tkinter as tk
from tkinter import ttk, messagebox
from utils import api_request, get_user_role
import re

class RoomManagement:
    def __init__(self, root, token):
        self.root = tk.Toplevel(root)
        self.token = token
        self.root.title("Room Management")

        # Set window size and position at the center
        window_width = 780
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2) - 20  # Move slightly up
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        self.user_role = get_user_role(self.token)

        self.setup_ui()
        self.fetch_rooms()

    def apply_grid_effect(self, tree=None):
        if tree is None:
            tree = self.tree  # Default to main tree if none is provided
        
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=("evenrow",))
            else:
                tree.item(item, tags=("oddrow",))

        tree.tag_configure("evenrow", background="#d9d9d9")  # medium gray
        tree.tag_configure("oddrow", background="white")

        # Style Configuration
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="#2C3E50", foreground="white")
        style.configure("Treeview", font=("Helvetica", 12), rowheight=25)
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=6)
        style.map("TButton", background=[("active", "#2980B9")])  # Hover effect

    def setup_ui(self):
        self.root.configure(bg="#f8f9fa")  # Light gray background for modern UI

        # Title Label
        title_label = tk.Label(self.root, text="Room Management", font=("Helvetica", 18, "bold"),
                               bg="#2C3E50", fg="white", padx=10, pady=10)
        title_label.pack(fill=tk.X)

        # Frame for Treeview (Card-like Container)
        card_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=2)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 5))

        # Treeview (Room List Table)
        columns = ("Room Number", "Room Type", "Amount", "Status", "Booking Type")
        self.tree = ttk.Treeview(card_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Apply alternating row colors
        self.tree.tag_configure("oddrow", background="#ECF0F1")  # Light gray
        self.tree.tag_configure("evenrow", background="white")

        # Button Frame
        btn_frame = tk.Frame(self.root, bg="#f8f9fa")
        btn_frame.pack(pady=10, padx=10)

        # Buttons with Icons
        buttons = [
            ("➕ Add Room", self.open_room_form),
            ("✏️ Update Room", self.update_room),
            ("❌ Delete Room", self.delete_room),
            ("🟢 Available Rooms", self.list_available_rooms),
            ("🔄 Refresh", self.fetch_rooms)
        ]

        for idx, (text, command) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=command, width=18)
            btn.grid(row=0, column=idx, padx=5, pady=5)

            # Disable buttons for non-admin users
            if self.user_role != "admin" and text in ["➕ Add Room", "✏️ Update Room", "❌ Delete Room"]:
                btn.config(state=tk.DISABLED)

                

    def natural_sort_key(self, room):
        """Sort room numbers correctly, handling both numeric and alphanumeric values."""
        room_number = str(room.get("room_number", ""))  # Ensure it's a string
        parts = re.split(r'(\d+)', room_number)  # Split letters and numbers
        return [int(part) if part.isdigit() else part for part in parts]  # Convert numeric parts to int

    def fetch_rooms(self):
        """Fetch and display rooms."""
        response = api_request("GET", "/rooms", self.token)
        if response.get("status") == "success":
            rooms = response.get("data", [])

            # Ensure sorting function is available
            rooms.sort(key=self.natural_sort_key)

            # Clear the tree before inserting new data
            for row in self.tree.get_children():
                self.tree.delete(row)

            for index, room in enumerate(rooms):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert("", tk.END, values=(
                    room["room_number"], room["room_type"], room["amount"], 
                    room["status"], room["booking_type"]
                ), tags=(tag,))

        else:
            messagebox.showerror("Error", "Failed to fetch rooms")

   

    def fetch_rooms(self):
        """Fetch all rooms from the API and update the display with their latest statuses, sorted naturally."""
        response = api_request("/rooms", "GET", token=self.token)

        if not response or "rooms" not in response:
            messagebox.showerror("Error", "Failed to fetch rooms")
            return

        self.tree.delete(*self.tree.get_children())  # Clear existing entries

        rooms = response["rooms"]  # Get the list of rooms

        # Sort rooms using natural sorting (handles "A1", "B2", "101" correctly)
        rooms.sort(key=self.natural_sort_key)  # Use self.natural_sort_key()

        for room in rooms:
            room_number = room.get("room_number", "N/A")
            room_type = room.get("room_type", "N/A")
            amount = room.get("amount", "N/A")

            # Fetch the latest status for each room
            room_details = api_request(f"/rooms/{room_number}", "GET", token=self.token)
            current_status = room_details.get("status", "N/A") if room_details else room.get("status", "N/A")
            booking_type = room_details.get("booking_type", "N/A") if room_details else "No active booking"

            # Insert the room details into the display
            self.tree.insert("", tk.END, values=(room_number, room_type, amount, current_status, booking_type))
            
            self.apply_grid_effect()  
            
    def list_available_rooms(self):
        """Fetch and display available rooms in a structured format."""
        response = api_request("/rooms/available", "GET", token=self.token)

        if not response or "available_rooms" not in response:
            messagebox.showerror("Error", "Unable to retrieve available rooms. Please try again.")
            return

        available_rooms = response["available_rooms"]
        available_rooms.sort(key=self.natural_sort_key)  # Apply natural sorting
        total_available = len(available_rooms)

        # Create new window
        available_window = tk.Toplevel(self.root)
        available_window.title("Available Rooms")
        available_window.geometry("550x420")
        available_window.configure(bg="#EAEAEA")  # Light gray background

        # Header Frame with subtle border color
        header_frame = tk.Frame(available_window, bg="white", relief="solid", borderwidth=1, highlightbackground="#B0B0B0")
        header_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            header_frame, 
            text=f"Available Rooms ({total_available})", 
            font=("Helvetica", 14, "bold"), 
            background="white"
        ).pack(pady=8)

        # Main Content Frame
        content_frame = tk.Frame(available_window, bg="#F5F5F5", padx=10, pady=10, relief="solid", borderwidth=1, highlightbackground="#B0B0B0")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Define Treeview (Table)
        columns = ("Room Number", "Room Type", "Amount")
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=10)

        # Format Columns
        for col in columns:
            tree.heading(col, text=col, anchor="center")
            tree.column(col, width=160, anchor="center")

        tree.pack(pady=5, fill=tk.BOTH, expand=True)

        # Insert available room data
        for room in available_rooms:
            tree.insert("", tk.END, values=(room["room_number"], room["room_type"], room["amount"]))

        # Close Button
        ttk.Button(available_window, text="Close", command=available_window.destroy).pack(pady=10)


    
    def open_room_form(self):
        form = tk.Toplevel(self.root)
        form.title("Add Room")
        form.geometry("350x320")
        form.resizable(False, False)

        # Center the window
        form.update_idletasks()  # Ensure correct size calculation
        screen_width = form.winfo_screenwidth()
        screen_height = form.winfo_screenheight()
        window_width = 350
        window_height = 320

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        form.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Border Frame
        container = tk.Frame(form, bg="#f8f9fa", padx=15, pady=15, relief="groove", bd=3)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title Label
        title_label = tk.Label(container, text="Add New Room", font=("Arial", 12, "bold"), bg="#f8f9fa")
        title_label.pack(pady=5)

        # Room Number
        tk.Label(container, text="Room Number:", bg="#f8f9fa").pack(anchor="w")
        room_number_entry = tk.Entry(container, width=30)
        room_number_entry.pack(pady=3)

        # Room Type
        tk.Label(container, text="Room Type:", bg="#f8f9fa").pack(anchor="w")
        room_type_entry = tk.Entry(container, width=30)
        room_type_entry.pack(pady=3)

        # Amount
        tk.Label(container, text="Amount:", bg="#f8f9fa").pack(anchor="w")
        amount_entry = tk.Entry(container, width=30)
        amount_entry.pack(pady=3)

        # Status Dropdown
        tk.Label(container, text="Status:", bg="#f8f9fa").pack(anchor="w")
        status_options = ["available"]
        status_entry = ttk.Combobox(container, values=status_options, state="readonly", width=27)
        status_entry.pack(pady=3)
        status_entry.current(0)


        # Submit Function
        def submit():
            room_number = room_number_entry.get()
            response = api_request("/rooms", "GET", token=self.token)
            if response and "rooms" in response:
                if any(room["room_number"] == room_number for room in response["rooms"]):
                    messagebox.showerror("Error", f"Room {room_number} already exists!")
                    return

            data = {
                "room_number": room_number,
                "room_type": room_type_entry.get(),
                "amount": amount_entry.get(),
                "status": status_entry.get()
            }

            add_response = api_request("/rooms", "POST", data, self.token)
            if add_response:
                messagebox.showinfo("Success", "Room added successfully")
                form.destroy()
                self.fetch_rooms()
            else:
                messagebox.showerror("Error", "Failed to add room")

        # Submit Button with Style
        submit_button = tk.Button(container, text="Submit", command=submit, bg="#007BFF", fg="white",
                                font=("Arial", 10, "bold"), padx=10, pady=3, relief="raised", bd=2)
        submit_button.pack(pady=10)

        
    def update_room(self):
        """Update selected room details."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a room to update")
            return

        # Get selected room details
        values = self.tree.item(selected[0], "values")

        room_number = values[0]  # Ensure this value is correct

        # Fetch the full room details from API
        response = api_request(f"/rooms/{room_number}", "GET", token=self.token)

        # Ensure the response contains valid data
        if not response or not isinstance(response, dict) or "room_number" not in response:
            messagebox.showerror("Error", f"Failed to fetch room details. Response: {response}")
            return

        room_data = response  # Assign the response directly if valid

        # Prevent updates if the room is checked-in
        if room_data["status"] == "checked-in":
            messagebox.showwarning("Warning", "Room cannot be updated as it is currently checked-in")
            return

        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Room")
        update_window.geometry("350x320")
        update_window.resizable(False, False)

        # Center the window
        update_window.update_idletasks()  # Ensure correct size calculation
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        window_width = 350
        window_height = 320

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        update_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Border Frame
        container = tk.Frame(update_window, bg="#f8f9fa", padx=15, pady=15, relief="groove", bd=3)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title Label
        title_label = tk.Label(container, text="Update Room Details", font=("Arial", 12, "bold"), bg="#f8f9fa")
        title_label.pack(pady=5)

        # Room Number (Ensure case is maintained)
        # Room Number Entry (Ensure case is preserved)
        tk.Label(container, text="Room Number:", bg="#f8f9fa").pack(anchor="w")
        room_number_entry = tk.Entry(container, width=30)

        # Ensure it is inserted correctly without modification
        room_number_entry.insert(0, room_data["room_number"])  
        room_number_entry.pack(pady=3)


        # Room Type
        tk.Label(container, text="Room Type:", bg="#f8f9fa").pack(anchor="w")
        room_type_entry = tk.Entry(container, width=30)
        room_type_entry.insert(0, room_data["room_type"])
        room_type_entry.pack(pady=3)

        # Amount
        tk.Label(container, text="Amount:", bg="#f8f9fa").pack(anchor="w")
        amount_entry = tk.Entry(container, width=30)
        amount_entry.insert(0, str(room_data["amount"]))
        amount_entry.pack(pady=3)

        # Status Dropdown
        tk.Label(container, text="Select New Status:", bg="#f8f9fa").pack(anchor="w")
        status_options = ["available"]
        status_entry = ttk.Combobox(container, values=status_options, state="readonly", width=27)
        status_entry.pack(pady=3)
        status_entry.set(room_data["status"])  # Set current status as default

        # Submit Function
        def submit_update():
            """Submit updated room data to API."""
            new_room_number = room_number_entry.get()
            new_room_type = room_type_entry.get()
            new_amount = amount_entry.get()
            new_status = status_entry.get()

            # Validate input
            if not new_room_number or not new_room_type or not new_amount:
                messagebox.showwarning("Warning", "All fields must be filled")
                return

            # Convert amount to float
            try:
                new_amount = float(new_amount)
            except ValueError:
                messagebox.showwarning("Warning", "Amount must be a number")
                return

            # Prepare update payload
            data = {
                "room_number": str(new_room_number),  # Maintain original case
                "room_type": new_room_type,
                "amount": new_amount,
                "status": new_status
            }


            # Send update request
            response = api_request(f"/rooms/{room_number}", "PUT", data, self.token)
            if response:
                messagebox.showinfo("Success", "Room updated successfully")
                update_window.destroy()
                self.fetch_rooms()
            else:
                messagebox.showerror("Error", "Failed to update room")

        # Submit Button with Style
        submit_button = tk.Button(container, text="Update", command=submit_update, bg="#28A745", fg="white",
                                font=("Arial", 10, "bold"), padx=10, pady=3, relief="raised", bd=2)
        submit_button.pack(pady=10)



    def delete_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a room to delete")
            return

        room_number = self.tree.item(selected[0], "values")[0]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete room {room_number}?")
        if confirm:
            response = api_request(f"/rooms/{room_number}", "DELETE", token=self.token)
            if response:
                messagebox.showinfo("Success", "Room deleted successfully")
                self.fetch_rooms()
            else:
                messagebox.showerror("Error", "Failed to delete room")

if __name__ == "__main__":
    root = tk.Tk()
    RoomManagement(root, "your_token_here")
    root.mainloop()