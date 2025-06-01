import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import api_request, get_user_role
import re
from datetime import datetime

class RoomManagement:
    def __init__(self, root, token):
        self.root = tk.Toplevel(root)
        self.token = token
        self.root.title("HEMS-Room Management")

        # Set window size and position at the center
        window_width = 780
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2) - 10  # Move slightly up
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        self.user_role = get_user_role(self.token)

        self.setup_ui()
        self.fetch_rooms()

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

       

        # Compact Button Frame
        btn_frame = ctk.CTkFrame(self.root, fg_color="#f8f9fa")
        btn_frame.pack(pady=5, padx=5)

        # Buttons with Icons and Compact Styling
        buttons = [
            ("➕ Add", self.open_room_form),
            ("✏️ Update", self.update_room),
            ("❌ Delete", self.delete_room),
            ("🧾 View Faults", self.view_faults),
            ("🟢 Rooms Available", self.list_available_rooms),
            ("🔄 Refresh", self.fetch_rooms)
        ]

        for idx, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                width=100,               # Reduced width
                height=25,               # Reduced height
                corner_radius=10,
                font=("Segoe UI", 11, "bold"),  # Slightly smaller font
                text_color="white",
                fg_color="#1e3d59",
                hover_color="#2563eb"
            )
            btn.grid(row=0, column=idx, padx=7, pady=7)
        
            # Disable buttons for non-admin users
            if self.user_role != "admin" and text in ["➕ Add",  "❌ Delete"]:
                btn.configure(state="disabled", fg_color="#adb5bd", hover_color="#adb5bd")

                

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
        response = api_request("/rooms/available", "GET", token=self.token)

        if not response or "available_rooms" not in response:
            messagebox.showerror("Error", "Unable to retrieve available rooms. Please try again.")
            return

        available_rooms = response["available_rooms"]
        available_rooms.sort(key=self.natural_sort_key)

        # Only count rooms that are NOT under maintenance
        total_available = sum(1 for room in available_rooms if room.get("status") != "maintenance")

        available_window = ctk.CTkToplevel(self.root)
        available_window.title("Available Rooms")
        available_window.geometry("600x460")
        available_window.resizable(False, False)
        available_window.transient(self.root)
        available_window.grab_set()

        header_frame = ctk.CTkFrame(available_window, fg_color="#1e1e1e", corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text=f"Available Rooms ({total_available})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=10)

        content_frame = ctk.CTkFrame(available_window, fg_color="#2a2a2a", corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background="#2a2a2a",
                        foreground="white",
                        fieldbackground="#2a2a2a",
                        rowheight=28,
                        font=("Segoe UI", 11))

        style.configure("Treeview.Heading",
                        background="#3a3a3a",
                        foreground="white",
                        font=("Segoe UI", 11, "bold"))

        tree = ttk.Treeview(content_frame, columns=("Room Number", "Room Type", "Amount"), show="headings")

        for col in ("Room Number", "Room Type", "Amount"):
            tree.heading(col, text=col, anchor="center")
            tree.column(col, anchor="center", width=180)

        for room in available_rooms:
            status = room.get("status")

            if status == "maintenance":
                # Surround each field with warning symbol
                symbol = "⚠️"
                room_number = f"{symbol} {room['room_number']} {symbol}"
                room_type = f"{symbol} {room['room_type']} {symbol}"
                amount = f"{symbol} {room['amount']} {symbol}"

            else:
                room_number = room['room_number']
                room_type = room['room_type']
                amount = room['amount']

            tree.insert("", tk.END, values=(room_number, room_type, amount))

        tree.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkButton(
            available_window,
            text="Close",
            command=available_window.destroy,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            corner_radius=8
        ).pack(pady=(0, 15))

        self.apply_grid_effect(tree)




    
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
        status_options = ["available", "maintenance"]
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



    def view_faults(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a room to view faults")
            return

        room_number = self.tree.item(selected[0], "values")[0]
        response = api_request(f"/rooms/{room_number}/faults", "GET", token=self.token)

        if response is None or not isinstance(response, list):
            messagebox.showerror("Error", "Failed to fetch faults or unexpected response format.")
            return

        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except Exception:
                    return None

        # Sort faults: unresolved first by created_at desc, then resolved by resolved_at asc
        response.sort(key=lambda x: (
            x.get("resolved", False),
            -parse_date(x["created_at"]).timestamp() if not x.get("resolved", False) and parse_date(x["created_at"]) else float('inf'),
            parse_date(x["resolved_at"]).timestamp() if x.get("resolved", False) and parse_date(x["resolved_at"]) else float('inf')
        ))

        fault_window = tk.Toplevel(self.root)
        fault_window.title(f"Faults for Room {room_number}")
        fault_window.geometry("800x550")
        fault_window.configure(bg="#e0e0e0")

        tk.Label(
            fault_window,
            text=f"Faults - Room {room_number}",
            font=("Arial", 14, "bold"),
            bg="#2C3E50",
            fg="white",
            pady=10
        ).pack(fill=tk.X)

        # Treeview Frame
        tree_frame = tk.Frame(fault_window, bg="#e0e0e0")
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("Id", "Fault Description", "Resolved", "Created_at", "Resolved_at")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, anchor="center")

        tree.column("Id", width=50)
        tree.column("Fault Description", width=250)
        tree.column("Resolved", width=100)
        tree.column("Created_at", width=150)
        tree.column("Resolved_at", width=150)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#d0d0d0")
        style.configure("Treeview", font=("Arial", 12), rowheight=30, background="#f4f4f4")
        style.map("Treeview", background=[("selected", "#3399ff")])

        tree.tag_configure("unresolved", font=("Arial", 12, "bold"))
        tree.tag_configure("resolved", font=("Arial", 12), foreground="gray")

        for fault in response:
            fault_id = fault.get("id")
            desc = fault.get("description", "")
            resolved = fault.get("resolved", False)
            created_at_dt = parse_date(fault.get("created_at"))
            resolved_at_dt = parse_date(fault.get("resolved_at"))

            resolved_display = "Done✅" if resolved else "Pending"
            created_str = created_at_dt.strftime("%Y-%m-%d %H:%M") if created_at_dt else "-"
            resolved_str = resolved_at_dt.strftime("%Y-%m-%d %H:%M") if resolved_at_dt else "-"

            tag = "resolved" if resolved else "unresolved"

            tree.insert(
                "", "end",
                values=(fault_id, desc, resolved_display, created_str, resolved_str),
                tags=(tag,)
            )

            # Apply grid effect first (assumed to be your row-style helper)
            self.apply_grid_effect(tree)

            # Reapply specific tag styles after apply_grid_effect, in case they were overridden
            tree.tag_configure("unresolved", font=("Arial", 12, "bold"))
            tree.tag_configure("resolved", font=("Arial", 12), foreground="gray")



        def unresolve_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a fault to unresolve")
                return

            item = tree.item(selected_item[0])
            fault_id = item["values"][0]
            current_status = item["values"][2]

            if current_status != "Done✅":
                messagebox.showinfo("Info", "This fault is already unresolved.")
                return

            update_data = [{"id": fault_id, "resolved": False}]
            save_response = api_request("/rooms/faults/update", method="PUT", data=update_data, token=self.token)

            if save_response:
                tree.set(selected_item[0], column="resolved", value="Pending")
                tree.set(selected_item[0], column="resolved_at", value="-")
                tree.item(selected_item[0], tags=("unresolved",))

                # If room was marked 'available' when all faults resolved, you might want to update room status accordingly
                # For example, set status to 'maintenance' or another appropriate status if there's at least one unresolved fault
                any_unresolved = any(tree.set(child, "resolved") == "Pending" for child in tree.get_children())
                if any_unresolved:
                    status_update = api_request(
                        f"/rooms/{room_number}/status",
                        method="PUT",
                        data={"status": "maintenance"},  # or your appropiate status for faults present
                        token=self.token
                    )
                    if status_update:
                        messagebox.showinfo("Room Updated", f"Room {room_number} set to 'maintenance' due to unresolved faults.")
                    else:
                        messagebox.showerror("Error", "Failed to update room status.")

            else:
                messagebox.showerror("Error", "Failed to update fault status.")



        def resolve_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a fault to resolve")
                return

            item = tree.item(selected_item[0])
            fault_id = item["values"][0]
            current_status = item["values"][2]

            if current_status == "Done✅":
                messagebox.showinfo("Info", "This fault is already resolved.")
                return

            update_data = [{"id": fault_id, "resolved": True}]
            save_response = api_request("/rooms/faults/update", method="PUT", data=update_data, token=self.token)

            if save_response:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                tree.set(selected_item[0], column="resolved", value="Done✅")
                tree.set(selected_item[0], column="resolved_at", value=now_str)
                tree.item(selected_item[0], tags=("resolved",))

                # ✅ If all faults resolved, set room status to 'available'
                all_resolved = all(tree.set(child, "resolved") == "Done✅" for child in tree.get_children())
                if all_resolved:
                    status_update = api_request(
                        f"/rooms/{room_number}/status",
                        method="PUT",
                        data={"status": "available"},
                        token=self.token
                    )

                    if status_update:
                        messagebox.showinfo("Room Updated", f"All faults resolved. Room {room_number} set to 'available'.")
                    else:
                        messagebox.showerror("info", "Failed to update room status to available.")
            else:
                messagebox.showerror("Error", "Failed to update fault status.")



        # Example: assume self.user_role stores current user's role
        is_admin = getattr(self, "user_role", "").lower() == "admin"

        btn_frame = ctk.CTkFrame(fault_window, fg_color="#e0e0e0")
        btn_frame.pack(pady=10)

        button_width = 120
        button_height = 35
        button_font = ("Arial", 12)

        resolve_button = ctk.CTkButton(
            btn_frame, text="Resolve Selected", command=resolve_selected,
            fg_color="#28a745", hover_color="#218838", text_color="white",
            font=button_font, corner_radius=8, width=button_width, height=button_height
        )
        resolve_button.pack(side="left", padx=10)

        if is_admin:
            unresolve_button = ctk.CTkButton(
                btn_frame, text="Unresolve Selected", command=unresolve_selected,
                fg_color="#dc3545", hover_color="#c82333", text_color="white",
                font=button_font, corner_radius=8, width=button_width, height=button_height
            )
            unresolve_button.pack(side="left", padx=10)

        close_button = ctk.CTkButton(
            btn_frame, text="Close", command=fault_window.destroy,
            fg_color="#8B0000", hover_color="#A52A2A", text_color="white",
            font=button_font, corner_radius=8, width=button_width, height=button_height
        )
        close_button.pack(side="left", padx=10)






        
    def update_room(self):
        """Update selected room details."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a room to update")
            return

        values = self.tree.item(selected[0], "values")
        room_number = values[0]

        response = api_request(f"/rooms/{room_number}", "GET", token=self.token)
        if not response or not isinstance(response, dict) or "room_number" not in response:
            messagebox.showerror("Error", f"Failed to fetch room details. Response: {response}")
            return

        room_data = response
        if room_data["status"] == "checked-in":
            messagebox.showwarning("Warning", "Room cannot be updated as it is currently checked-in")
            return

        update_window = tk.Toplevel(self.root)
        update_window.title("Update Room")
        update_window.geometry("400x500")
        update_window.resizable(False, False)

        # Center the window
        update_window.update_idletasks()
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 500) // 2
        update_window.geometry(f"400x500+{x}+{y}")

        container = tk.Frame(update_window, bg="#f8f9fa", padx=15, pady=15, relief="groove", bd=3)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(container, text="Update Room Details", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(pady=5)

        # Room Number
        tk.Label(container, text="Room Number:", bg="#f8f9fa").pack(anchor="w")
        room_number_entry = tk.Entry(container, width=30)
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

        # Status
        tk.Label(container, text="Select New Status:", bg="#f8f9fa").pack(anchor="w")
        status_options = ["available", "maintenance"]
        status_entry = ttk.Combobox(container, values=status_options, state="readonly", width=27)
        status_entry.pack(pady=3)
        status_entry.set(room_data["status"])

        # Maintenance Frame (Initially hidden)
        maintenance_frame = tk.Frame(container, bg="#f8f9fa")
        maintenance_check_vars = []
        maintenance_faults = []

        def load_fault_items():
            maintenance_check_vars.clear()
            for widget in maintenance_frame.winfo_children():
                widget.destroy()

            tk.Label(maintenance_frame, text="Fault Items:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))

            fault_items = room_data.get("faults", [])
            for fault in fault_items:
                var = tk.BooleanVar(value=fault.get("done", False))
                cb = tk.Checkbutton(maintenance_frame, text=fault["description"], variable=var, bg="#f8f9fa")
                cb.pack(anchor="w")
                maintenance_check_vars.append((fault, var))

            # Add new fault item
            tk.Label(maintenance_frame, text="Add New Fault:", bg="#f8f9fa").pack(anchor="w", pady=(10, 0))
            new_fault_entry = tk.Entry(maintenance_frame, width=30)
            new_fault_entry.pack(pady=3)

            def add_fault_item():
                desc = new_fault_entry.get().strip()
                if desc:
                    maintenance_check_vars.append(({"description": desc, "done": False}, tk.BooleanVar(value=False)))
                    cb = tk.Checkbutton(maintenance_frame, text=desc, variable=maintenance_check_vars[-1][1], bg="#f8f9fa")
                    cb.pack(anchor="w")
                    new_fault_entry.delete(0, tk.END)

            tk.Button(maintenance_frame, text="Add Fault", command=add_fault_item).pack(pady=5)

        def toggle_maintenance_section(event):
            if status_entry.get() == "maintenance":
                load_fault_items()
                maintenance_frame.pack(fill="x", pady=5)
            else:
                maintenance_frame.pack_forget()

        status_entry.bind("<<ComboboxSelected>>", toggle_maintenance_section)
        if room_data["status"] == "maintenance":
            load_fault_items()
            maintenance_frame.pack(fill="x", pady=5)

        def submit_update(original_room_number=room_number):
            new_room_number = room_number_entry.get()
            new_room_type = room_type_entry.get()
            new_amount = amount_entry.get()
            new_status = status_entry.get()

            if not new_room_number or not new_room_type or not new_amount:
                messagebox.showwarning("Warning", "All fields must be filled")
                return

            try:
                new_amount = float(new_amount)
            except ValueError:
                messagebox.showwarning("Warning", "Amount must be a number")
                return

            faults_payload = []
            for fault_data, var in maintenance_check_vars:
                faults_payload.append({
                    "room_number": room_data["room_number"],
                    "description": fault_data["description"],
                    "done": var.get()
                })


            data = {
                "room_type": room_type_entry.get(),
                "amount": float(amount_entry.get()),
                "status": status_entry.get(),
                "faults": faults_payload
            }

            update_response = api_request(f"/rooms/{original_room_number}", method="PUT", data=data, token=self.token)

            if update_response:
                messagebox.showinfo("Success", "Room updated successfully")
                update_window.destroy()
                #self.load_rooms()  # or self.display_rooms() — depending on what you named it

            else:
                messagebox.showerror("Error", "Failed to update room")

        tk.Button(container, text="Update", command=submit_update, bg="#28A745", fg="white",
                font=("Arial", 10, "bold"), padx=10, pady=3, relief="raised", bd=2).pack(pady=10)



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