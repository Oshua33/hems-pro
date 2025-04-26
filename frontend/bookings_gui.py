import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests
from utils import BASE_URL
import datetime 
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
#from customtkinter import CTkMessagebox



from tkinter import Tk, Button, messagebox
from utils import export_to_excel, print_excel
import requests
import os
import sys
import pandas as pd
from payment_gui import PaymentManagement  # Import the Payment GUI
##


class BookingManagement:
    def __init__(self, root, token):
        self.root = tk.Toplevel(root)
        self.tree = ttk.Treeview(self.root)  # Ensure the treeview is initialized
        self.root.title("Booking Management")
        self.root.state("zoomed")
        self.root.configure(bg="#f0f0f0")
        
        self.username = "current_user"
        self.token = token


        # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # Set window size and position
        window_width = 1375
        window_height = 587
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        
        # Main Container Frame
        self.container = tk.Frame(self.root, bg="#ffffff", padx=10, pady=10)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Header Frame
        self.header_frame = tk.Frame(self.container, bg="#2C3E50", height=60)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.title_label = tk.Label(self.header_frame, text="📅 Booking Management", 
                                    font=("Helvetica", 16, "bold"), fg="gold", bg="#2C3E50")
        self.title_label.pack(pady=0)
        
        # ==== New Action Frame (Right Side of Header) ====
        self.action_frame = tk.Frame(self.header_frame, bg="#2C3E50")
        self.action_frame.pack(side=tk.RIGHT, padx=20)  

        # Export to Excel
        self.export_label = tk.Label(self.action_frame, text="📊 Export to Excel",
                                    font=("Helvetica", 10, "bold"), fg="white", bg="#2C3E50", cursor="hand2")
        self.export_label.pack(side=tk.RIGHT, padx=10)
        self.export_label.bind("<Enter>", lambda e: self.export_label.config(fg="#D3D3D3"))
        self.export_label.bind("<Leave>", lambda e: self.export_label.config(fg="white"))
        self.export_label.bind("<Button-1>", lambda e: self.export_report())

        # Print Report
        self.print_label = tk.Label(self.action_frame, text="🖨 Print Report",
                                    font=("Helvetica", 10, "bold"), fg="white", bg="#2C3E50", cursor="hand2")
        self.print_label.pack(side=tk.RIGHT, padx=10)
        self.print_label.bind("<Enter>", lambda e: self.print_label.config(fg="#D3D3D3"))
        self.print_label.bind("<Leave>", lambda e: self.print_label.config(fg="white"))
        self.print_label.bind("<Button-1>", lambda e: self.print_report())


         # ==== Main Content Frame (Holds Sidebar + Right Section) ====
        self.main_frame = tk.Frame(self.container, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

         # ==== Menu Container (With "Menu" Heading) ====
        self.Menu = tk.Frame(self.main_frame, bg="#2C3E50", width=230)
        self.Menu.pack(side=tk.LEFT, fill=tk.Y)

        # === "Menu" Heading ===
        self.menu_label = tk.Label(self.Menu, text="MENU", font=("Helvetica", 12, "bold"), 
                                   fg="white", bg="#34495E", pady=5)
        self.menu_label.pack(fill=tk.X)

        # Sidebar Section (Inside `Menu` Frame)
        self.left_frame = tk.Frame(self.Menu, bg="#2C3E50", width=220)
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Right Section (Main Content)
        self.right_frame = tk.Frame(self.main_frame, bg="#ffffff", relief="ridge", borderwidth=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Subheading Label
        self.subheading_label = tk.Label(self.right_frame, text="Select an option",
                                         font=("Helvetica", 14, "bold"), fg="#2C3E50", bg="#ffffff")
        self.subheading_label.pack(pady=10)

        # ==== Booking Action Buttons in Sidebar ====
        buttons = [
            ("Create Booking", self.create_booking),
            ("List Booking", self.list_bookings),
            ("Sort By Status", self.list_bookings_by_status),
            ("Sort Guest Name", self.search_booking),
            ("Sort by ID", self.search_booking_by_id),
            ("Sort By Room", self.search_booking_by_room),
            ("Update Booking", self.update_booking),
            ("Guest Checkout", self.guest_checkout),
            ("Cancel Booking", self.cancel_booking),
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.left_frame, text=text,
                            command=lambda t=text, c=command: self.update_subheading(t, c),
                            width=10, font=("Arial", 10), anchor="w", padx=10,
                            bg="#34495E", fg="white", relief="flat", bd=0)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1ABC9C"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495E"))
            btn.pack(pady=8, padx=10, anchor="w", fill="x")

            # Dashboard Link
            self.dashboard_label = tk.Label(
            self.left_frame,
            text="⬅ Dashboard",
            cursor="hand2",
            font=("Helvetica", 10, "bold"),
            fg="white",
            bg="#1A5276",  # Deep Blue Background
            padx=10,
            pady=5,
            relief="solid",
            borderwidth=2
        )
        self.dashboard_label.pack(pady=15, padx=10, anchor="w", fill="x")

        # Change background color when hovering over
        self.dashboard_label.bind("<Enter>", lambda e: self.dashboard_label.config(bg="#154360"))  # Darker Blue on Hover
        self.dashboard_label.bind("<Leave>", lambda e: self.dashboard_label.config(bg="#1A5276"))  # Reset on Leave

        # Click event to open dashboard
        self.dashboard_label.bind("<Button-1>", lambda e: self.open_dashboard_window())


    def update_subheading(self, text, command):
        """Updates the subheading label and runs the selected command"""
        self.subheading_label.config(text=text)
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        command()
    
    def open_dashboard_window(self):
        """Opens the dashboard window"""
        from dashboard import Dashboard
        Dashboard(self.root, self.username, self.token)
        self.root.destroy()



    def apply_grid_effect(self, tree=None):
        if tree is None:
            tree = self.tree  # Default to main tree if none is provided
        
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=("evenrow",))
            else:
                tree.item(item, tags=("oddrow",))

        tree.tag_configure("evenrow", background="#f2f2f2")  # Light gray
        tree.tag_configure("oddrow", background="white")      # White


    def open_dashboard_window(self):
        from dashboard import Dashboard  # Import here to avoid circular import issues
        Dashboard(self.root, self.username, self.token)
        self.root.destroy()

    def update_subheading(self, text, command):
        if self.subheading_label.winfo_exists():
            self.subheading_label.config(text=text)
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        command()
        


            
             
        self.fetch_and_display_bookings()

       # Export and Print Buttons in Header Section
        def on_enter(e):
            e.widget.config(bg="#1ABC9C", fg="white")  # Background changes on hover

        def on_leave(e):
            e.widget.config(bg="#2C3E50", fg="white")  # Restore default background & text color

        self.export_button = tk.Label(self.header_frame, text="Export to Excel", 
                                    fg="white", bg="#2C3E50", font=("Helvetica", 9, "bold"), 
                                    cursor="hand2", padx=10, pady=5)
        self.export_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.export_button.bind("<Enter>", on_enter)
        self.export_button.bind("<Leave>", on_leave)
        self.export_button.bind("<Button-1>", lambda e: self.export_report())  # Click event

        self.print_button = tk.Label(self.header_frame, text="Print Report", 
                                    fg="white", bg="#2C3E50", font=("Helvetica", 9, "bold"), 
                                    cursor="hand2", padx=10, pady=5)
        self.print_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.print_button.bind("<Enter>", on_enter)
        self.print_button.bind("<Leave>", on_leave)
        self.print_button.bind("<Button-1>", lambda e: self.print_report())  # Click event


     



    def reset_booking_form(self):
        """Clears all input fields in the booking form."""
        if hasattr(self, "entries"):
            for key, entry in self.entries.items():
                if isinstance(entry, ttk.Combobox):
                    entry.set("")  # Clear combobox selection
                elif isinstance(entry, DateEntry):
                    entry.set_date(datetime.date.today())  # Reset date to today
                elif isinstance(entry, tk.Entry):
                    entry.delete(0, tk.END)  # Clear text entry
                else:
                    print(f"Unknown entry type for {key}")

    





    def fetch_and_display_bookings(self):
        """Fetch booking data from the API"""
        url = "http://127.0.0.1:8000/bookings/list"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.bookings_data = response.json()
            else:
                self.bookings_data = []
                messagebox.showerror("Error", "Failed to fetch bookings.")

        except Exception as e:
            self.bookings_data = []
            messagebox.showerror("Error", f"API Error: {str(e)}")



    def export_report(self):
        """Export only the visible bookings from the Treeview to Excel"""
        if not hasattr(self, "tree") or not self.tree.get_children():
            messagebox.showwarning("Warning", "No data available to export.")
            return

        # Extract column headers
        columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]

        # Extract row data from Treeview
        rows = []
        for item in self.tree.get_children():
            row_data = [self.tree.item(item)["values"][i] for i in range(len(columns))]
            rows.append(row_data)

        # Convert to DataFrame for better formatting
        df = pd.DataFrame(rows, columns=columns)

        # Save in user's Downloads folder
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(download_dir, "bookings_report.xlsx")

        try:
            df.to_excel(file_path, index=False)  # Export properly formatted Excel
            self.last_exported_file = file_path
            messagebox.showinfo("Success", f"Report exported successfully!\nSaved at: {file_path}")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied! Close the file if it's open and try again.")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to Excel: {e}")


    def print_report(self):
        """Print the exported Excel report"""
        if hasattr(self, 'last_exported_file') and self.last_exported_file:
            print_excel(self.last_exported_file)
        else:
            messagebox.showwarning("Warning", "Please export the report before printing.")

    def update_subheading(self, text, command):
        """Updates the subheading label and calls the selected function."""
        if hasattr(self, "subheading_label") and self.subheading_label.winfo_exists():
            self.subheading_label.config(text=text)
        else:
            self.subheading_label = tk.Label(self.right_frame, text=text, font=("Arial", 14, "bold"), bg="#f0f0f0")
            self.subheading_label.pack(pady=10)

        # Clear right frame before displaying new content
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        command()

    







    def create_booking(self):
        """Opens a pop-up window for creating a new booking with CustomTkinter."""
        self.clear_right_frame()

        # Create a new pop-up window
        create_window = ctk.CTkToplevel(self.root)
        create_window.title("Create Booking")
        create_window.geometry("650x400")
        create_window.resizable(False, False)
        create_window.configure(fg_color="#f5f5f5")

        # Center the window on the screen
        screen_width = create_window.winfo_screenwidth()
        screen_height = create_window.winfo_screenheight()
        x_coordinate = (screen_width - 650) // 2
        y_coordinate = (screen_height - 400) // 2
        create_window.geometry(f"650x400+{x_coordinate}+{y_coordinate}")

        # Make the window modal
        create_window.transient(self.root)
        create_window.grab_set()

        # Header
        header_frame = ctk.CTkFrame(create_window, fg_color="#2c3e50", height=50, corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_label = ctk.CTkLabel(header_frame, text="Create Booking", font=("Arial", 16, "bold"), text_color="white")
        header_label.pack(pady=10)

        # Main Content Frame
        frame = ctk.CTkFrame(create_window, fg_color="white", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Booking Fields Layout
        self.entries = {}  # Store entry widgets

        # Combo box values
        combo_box_values = {
            "Gender": ["Male", "Female"],
            "Booking Type": ["checked-in", "reservation", "complimentary"]
        }

        # Form Grid Layout
        form_data = [
            ("Room Number", ctk.CTkEntry, 0, 0), ("Guest Name", ctk.CTkEntry, 0, 2),
            ("Identification Number", ctk.CTkEntry, 1, 0), ("Gender", ctk.CTkComboBox, 1, 2),
            ("Address", ctk.CTkEntry, 2, 0, 3),  # Span across columns
            ("Phone Number", ctk.CTkEntry, 3, 0), ("Booking Type", ctk.CTkComboBox, 3, 2),
            ("Arrival Date", DateEntry, 4, 0), ("Departure Date", DateEntry, 4, 2),
        ]

        for label_text, field_type, row, col, colspan in [(*fd, 1) if len(fd) == 4 else fd for fd in form_data]:
            label = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 12, "bold"), text_color="#2c3e50")
            label.grid(row=row, column=col, sticky="w", pady=5, padx=10)

            # Create input fields
            if field_type == ctk.CTkComboBox:
                entry = ctk.CTkComboBox(frame, values=combo_box_values.get(label_text, []), state="readonly",
                                        font=("Helvetica", 12), width=200)
            elif field_type == DateEntry:
                entry = DateEntry(frame, font=("Helvetica", 12), width=12, background='darkblue', foreground='white', borderwidth=2)
            else:
                entry = field_type(frame, font=("Helvetica", 12), width=22 if label_text != "Address" else 50)

            entry.grid(row=row, column=col + 1, columnspan=colspan, pady=5, padx=10, sticky="ew")
            self.entries[label_text] = entry  # Store entry

        # Submit Button
        submit_btn = ctk.CTkButton(
            frame,
            text="Submit Booking",
            command=lambda: self.submit_booking(create_window),
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="white",
            corner_radius=10,
            width=450,
            height=40
        )
        submit_btn.grid(row=5, column=0, columnspan=4, pady=25, padx=30, sticky="ew")  # Center button



    def submit_booking(self, create_window):
        """Collects form data and sends a request to create a booking, then closes the pop-up."""
        try:
            created_by = self.username

            # Ensure entries dictionary exists
            if not hasattr(self, "entries"):
                CTkMessagebox(title="Error", message="Entry fields are not initialized properly.", icon="cancel")
                return

            # Extract data from form
            booking_data = {
                "room_number": self.entries["Room Number"].get(),
                "guest_name": self.entries["Guest Name"].get(),
                "gender": self.entries["Gender"].get(),
                "identification_number": self.entries["Identification Number"].get(),
                "address": self.entries["Address"].get(),
                "phone_number": self.entries["Phone Number"].get(),
                "arrival_date": self.entries["Arrival Date"].get_date().strftime("%Y-%m-%d"),
                "departure_date": self.entries["Departure Date"].get_date().strftime("%Y-%m-%d"),
                "booking_type": self.entries["Booking Type"].get(),
                "created_by": created_by,
            }

            # Check for empty fields
            if not all(booking_data.values()):
                CTkMessagebox(title="Missing Fields", message="Please fill in all required fields before submitting.", icon="warning")
                return

            api_url = "http://127.0.0.1:8000/bookings/create/"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            # Send POST request
            response = requests.post(api_url, json=booking_data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                booking_id = response_data.get("booking_details", {}).get("id")

                if booking_id:
                    create_window.destroy()  # Close pop-up window
                    CTkMessagebox(
                        title="Success",
                        message=f"Booking created successfully!\nBooking ID: {booking_id}",
                        icon="check"
                    )

                    # Reset form if method exists
                    if hasattr(self, "reset_booking_form"):
                        self.reset_booking_form()

                else:
                    CTkMessagebox(title="Error", message="Booking ID missing in response.", icon="cancel")

            else:
                error_message = response.json().get("detail", "Booking failed.")
                CTkMessagebox(title="Error", message=error_message, icon="warning")

        except KeyError as e:
            CTkMessagebox(title="Error", message=f"Missing entry field: {e}", icon="warning")

        except requests.exceptions.RequestException as e:
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="warning")



    def list_bookings(self):
        self.clear_right_frame()
        
        
        # Create a new frame for the table
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Bookings Report", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        fetch_btn = ttk.Button(
            filter_frame,
            text="Fetch Bookings",
            command=lambda: self.fetch_bookings(self.start_date, self.end_date)
        )
        fetch_btn.grid(row=0, column=4, padx=10, pady=5)

        # Create a frame to hold the treeview and scrollbars
        table_frame = tk.Frame(frame, bg="#ffffff", bd=1, relief="solid")  # Solid border for grid effect
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Define Treeview columns
        columns = ("ID", "Room", "Guest Name", "Gender", "Booking Cost", "Arrival", "Departure", "Status", "Number of Days", 
                "Booking Type", "Phone Number", "Booking Date", "Payment Status", "Identification Number", "Address","Created_by")

        # Create a Treeview widget
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, background="white", fieldbackground="white", borderwidth=1)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#2c3e50", foreground="white")
        style.map("Treeview", background=[("selected", "#b3d1ff")])

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)  # Set height for visibility

        # Define headings and set column widths
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=70, anchor="center")  # Adjust column width

        # Pack the Treeview inside a scrollable frame
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add vertical scrollbar
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        # Add horizontal scrollbar
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        # Label to display total booking cost
        self.total_booking_cost_label = tk.Label(frame, text="", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_booking_cost_label.pack(pady=10)

        

    def fetch_bookings(self, start_date_entry, end_date_entry):
        """Fetch bookings from the API and populate the table, while calculating total booking cost."""
        api_url ="http://127.0.0.1:8000/bookings/list"  # Ensure correct endpoint
        params = {
            "start_date": start_date_entry.get_date().strftime("%Y-%m-%d"),
            "end_date": end_date_entry.get_date().strftime("%Y-%m-%d"),
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # print("API Response:", data)  # Debugging output

                if isinstance(data, dict) and "bookings" in data:
                    bookings = data["bookings"]
                    total_booking_cost = data.get("total_booking_cost", 0)  # Get total cost from API
                else:
                    messagebox.showerror("Error", "Unexpected API response format")
                    return

                # Check if bookings list is empty
                if not bookings:
                    self.total_booking_cost_label.config(text="Total Booking Cost: 0.00")  # Reset label
                    messagebox.showinfo("No Results", "No bookings found for the selected filters.")
                    return

                self.tree.delete(*self.tree.get_children())  # Clear table

                for booking in bookings:
                    self.tree.insert("", "end", values=(
                        booking.get("id", ""),
                        booking.get("room_number", ""),
                        booking.get("guest_name", ""),
                        booking.get("gender", ""),
                        f"{float(booking.get('booking_cost', 0)) :,.2f}",
                        booking.get("arrival_date", ""),
                        booking.get("departure_date", ""),
                        booking.get("status", ""),
                        booking.get("number_of_days", ""),
                        booking.get("booking_type", ""),
                        booking.get("phone_number", ""),
                        booking.get("booking_date", ""),
                        booking.get("payment_status", ""), 
                        booking.get("identification_number", ""),  
                        booking.get("address", ""),                 
                        booking.get("created_by", ""),
                    ))

                # Apply grid effect after inserting data
                self.apply_grid_effect()

                # Display total booking cost
                self.total_booking_cost_label.config(
                    text=f"Total Booking Cost: {total_booking_cost:,.2f}"
                )
            
            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve bookings."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")


    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()

    
    
    
    
    def list_bookings_by_status(self):
        """Displays the List Bookings by Status UI."""
        self.clear_right_frame()  # Ensure old UI elements are removed

        # Create a new frame for the table with scrollable functionality
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Bookings by Status", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        # Status Dropdown
       # Status Dropdown
        tk.Label(filter_frame, text="Status:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)

        status_options = ["checked-in", "reserved", "checked-out", "cancelled", "complimentary"]
        self.status_var = tk.StringVar(value=status_options[0])  # Default selection

        status_menu = ttk.Combobox(filter_frame, textvariable=self.status_var, values=status_options, state="readonly")
        status_menu.grid(row=0, column=1, padx=5, pady=5)

        # Bind the selection event to a function that updates self.status_var
        def on_status_change(event):
            #print("Selected Status:", self.status_var.get())  # Debugging: Check what is selected
            self.status_var.set(status_menu.get())  # Ensure value updates

        status_menu.bind("<<ComboboxSelected>>", on_status_change)  # Event binding


        # Start Date
        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=3, padx=5, pady=5)

        # End Date
        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.grid(row=0, column=5, padx=5, pady=5)

        # Fetch Button
        fetch_btn = ttk.Button(filter_frame, text="Fetch Bookings", command=self.fetch_bookings_by_status)
        fetch_btn.grid(row=0, column=6, padx=10, pady=5)

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Room", "Guest Name", "Gender", "Booking Cost", "Arrival", "Departure", "Status", "Number of Days", 
                "Booking Type", "Phone Number", "Booking Date", "Payment Status", "Identification Number", "Address","Created_by")


        # ✅ Prevent recreation of table on every call
        if hasattr(self, "tree"):
            self.tree.destroy()

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        # ✅ Add Label for Total Booking Cost at the Bottom
        self.total_cost_label = tk.Label(frame, text="Total Booking Cost: 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_cost_label.pack(pady=10)  # Placed at the bottom


    def fetch_bookings_by_status(self):
        """Fetch bookings based on status and date filters."""
        api_url = "http://127.0.0.1:8000/bookings/status"

        selected_status = self.status_var.get().strip().lower()  # Ensure correct status retrieval

        # ✅ Debugging: Print the selected status before sending
        #print(f"Selected Status from Dropdown: '{selected_status}'")

        params = {
            "status": selected_status,  # Ensure correct status is passed
            "start_date": self.start_date.get_date().strftime("%Y-%m-%d"),
            "end_date": self.end_date.get_date().strftime("%Y-%m-%d"),
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
            data = response.json()

            # ✅ Debugging: Print the API response
            #print("API Response:", data)

            if response.status_code == 200:
                if "bookings" in data and isinstance(data["bookings"], list):
                    bookings = data["bookings"]

                    self.tree.delete(*self.tree.get_children())  # Clear previous data

                    total_cost = 0  # Initialize total booking cost

                    if bookings:
                        for booking in bookings:
                            is_canceled = booking.get("status", "").lower() == "cancelled"
                            tag = "cancelled" if is_canceled else "normal"

                            booking_cost = float(booking.get("booking_cost", 0))
                            total_cost += booking_cost

                            self.tree.insert("", "end", values=(
                                booking.get("id", ""),
                                booking.get("room_number", ""),
                                booking.get("guest_name", ""),
                                booking.get("gender", ""),
                                f"{booking_cost:,.2f}",
                                booking.get("arrival_date", ""),
                                booking.get("departure_date", ""),
                                booking.get("status", ""),
                                booking.get("number_of_days", ""),
                                booking.get("booking_type", ""),
                                booking.get("phone_number", ""),
                                booking.get("booking_date", ""),
                                booking.get("payment_status", ""), 
                                booking.get("identification_number", ""),  
                                booking.get("address", ""),                               
                                booking.get("created_by", ""),
                            ), tags=(tag,))

                        # Apply grid effect after inserting data
                        self.apply_grid_effect()


                        self.tree.tag_configure("cancelled", foreground="red")
                        self.tree.tag_configure("normal", foreground="black")
                        self.total_cost_label.config(text=f"Total Booking Cost: {total_cost:,.2f}")
                    else:
                        self.tree.delete(*self.tree.get_children())
                        self.total_cost_label.config(text="Total Booking Cost: ₦0.00")
                        messagebox.showinfo("No Results", "No bookings found for the selected filters.")

                elif "message" in data:
                    messagebox.showinfo("Info", data["message"])
                    self.tree.delete(*self.tree.get_children())
                    self.total_cost_label.config(text="Total Booking Cost: ₦0.00")

            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve bookings."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

            
    
    def search_booking(self):
        self.clear_right_frame()
        
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Search Booking by Guest Name", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)
        
        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=5)
        
        tk.Label(search_frame, text="Guest Name:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        search_btn = ttk.Button(
            search_frame, text="Search", command=self.fetch_booking_by_guest_name
        )
        search_btn.grid(row=0, column=2, padx=10, pady=5)
        
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Room", "Guest Name", "Gender", "Booking Cost", "Arrival", "Departure", "Status", "Number of Days", 
                "Booking Type", "Phone Number", "Booking Date", "Payment Status", "Identification Number", "Address","Created_by")

        self.search_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=70, anchor="center")
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.search_tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.configure(yscroll=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.search_tree.xview)
        x_scroll.pack(fill=tk.X)
        self.search_tree.configure(xscroll=x_scroll.set)
    
    def fetch_booking_by_guest_name(self):
        guest_name = self.search_entry.get().strip()
        if not guest_name:
            messagebox.showerror("Error", "Please enter a guest name to search.")
            return

        
         
        api_url ="http://127.0.0.1:8000/bookings/search"
        params = {"guest_name": guest_name}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                bookings = data.get("bookings", [])
                
                self.search_tree.delete(*self.search_tree.get_children())
                
                for booking in bookings:
                    self.search_tree.insert("", "end", values=(
                        booking.get("id", ""),
                        booking.get("room_number", ""),
                        booking.get("guest_name", ""),
                        booking.get("gender", ""),
                         f"{float(booking.get('booking_cost', 0)) :,.2f}",  # Format booking_cost
                        booking.get("arrival_date", ""),
                        booking.get("departure_date", ""),
                        booking.get("status", ""),
                        booking.get("number_of_days", ""),
                        booking.get("booking_type", ""),
                        booking.get("phone_number", ""),
                        booking.get("booking_date", ""),
                        booking.get("payment_status", ""),
                        booking.get("identification_number", ""),  
                        booking.get("address", ""),                               
                        booking.get("created_by", ""),

                       
                    ))
            
                # Apply grid effect after inserting data
                self.apply_grid_effect(self.search_tree)

    
            else:
                messagebox.showinfo("No result", response.json().get("detail", "No bookings found."))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

    
    def search_booking_by_id(self):
        self.clear_right_frame()
        
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Search Booking by ID", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)
        
        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=5)
        
        tk.Label(search_frame, text="Booking ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.booking_id_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.booking_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        search_btn = ttk.Button(
            search_frame, text="Search", command=self.fetch_booking_by_id
        )
        search_btn.grid(row=0, column=2, padx=10, pady=5)
        
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Room", "Guest Name", "Gender", "Booking Cost", "Arrival", "Departure", "Status", "Number of Days", 
                "Booking Type", "Phone Number", "Booking Date", "Payment Status", "Identification Number", "Address","Created_by")

        if hasattr(self, "tree"):
            self.tree.destroy()
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

    def fetch_booking_by_id(self):
        booking_id = self.booking_id_entry.get().strip()
    
        if not booking_id.isdigit():  # Ensure input is numeric
            messagebox.showerror("Error", "Please enter a valid numeric booking ID.")
            return
        
        try:
    
            #booking_id = int(booking_id)  # Convert to integer

            
            api_url = f"http://127.0.0.1:8000/bookings/{booking_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
        
        
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                booking = data.get("booking", {})
                
                # Ensure the booking details exist
                if booking:
                    self.tree.delete(*self.tree.get_children())
                    self.tree.insert("", "end", values=(
                        booking.get("id", ""),
                        booking.get("room_number", ""),
                        booking.get("guest_name", ""),
                        booking.get("gender", ""),
                        f"{float(booking.get('booking_cost', 0)) :,.2f}",  # Format booking_cost
                        booking.get("arrival_date", ""),
                        booking.get("departure_date", ""),
                        booking.get("status", ""),
                        booking.get("number_of_days", ""),
                        booking.get("booking_type", ""),
                        booking.get("phone_number", ""),
                        booking.get("booking_date", ""),
                        booking.get("payment_status", ""),
                        booking.get("identification_number", ""),  
                        booking.get("address", ""),                                                   
                        booking.get("created_by", ""),
                    ))

                 # Apply grid effect after inserting data
                    self.apply_grid_effect(self.tree)

   
                else:
                    messagebox.showinfo("No Results", "No booking found with the provided ID.")
            else:
                messagebox.showerror("Error", response.json().get("detail", "No booking found."))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
     
    def search_booking_by_room(self):
        self.clear_right_frame()

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Search Booking by Room Number", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Centered Frame for Search Inputs
        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=10)

        # Grid Configuration for Centralization
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_columnconfigure(2, weight=1)
        search_frame.grid_columnconfigure(3, weight=1)
        search_frame.grid_columnconfigure(4, weight=1)
        search_frame.grid_columnconfigure(5, weight=1)
        search_frame.grid_columnconfigure(6, weight=1)

        # Room Number Entry
        tk.Label(search_frame, text="Room Number:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.room_number_entry = tk.Entry(search_frame, font=("Arial", 11), width=12)
        self.room_number_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Start Date
        tk.Label(search_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.start_date_entry = DateEntry(search_frame, font=("Arial", 11), width=12, background="darkblue", foreground="white", borderwidth=2)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # End Date
        tk.Label(search_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.end_date_entry = DateEntry(search_frame, font=("Arial", 11), width=12, background="darkblue", foreground="white", borderwidth=2)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Search Button
        search_btn = ttk.Button(search_frame, text="Search", command=self.fetch_booking_by_room)
        search_btn.grid(row=0, column=6, padx=10, pady=5, sticky="w")

        # Table Frame for results
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Define table columns
        columns = ("ID", "Room", "Guest Name", "Gender", "Booking Cost", "Arrival", "Departure", "Status", "Number of Days",
                "Booking Type", "Phone Number", "Booking Date", "Payment Status", "Identification Number", "Address", "Created_by")

        self.search_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configure table column headings
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=70, anchor="center")

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.search_tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.search_tree.xview)
        x_scroll.pack(fill=tk.X)
        self.search_tree.configure(xscroll=x_scroll.set)

        # Total Label (Below Table)
        self.total_label = tk.Label(frame, text="Total Booking Cost: 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_label.pack(pady=10)



    def fetch_booking_by_room(self):
        room_number = self.room_number_entry.get().strip()

        if not room_number:
            messagebox.showerror("Error", "Please enter a room number.")
            return

        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()

            if not start_date or not end_date:
                messagebox.showerror("Error", "Please select both start and end dates.")
                return

            # Ensure date format matches backend expectation
            formatted_start_date = start_date.strftime("%Y-%m-%d")
            formatted_end_date = end_date.strftime("%Y-%m-%d")

            # Construct API URL
            api_url = f"http://127.0.0.1:8000/bookings/room/{room_number}"
            params = {"start_date": formatted_start_date, "end_date": formatted_end_date}
            headers = {"Authorization": f"Bearer {self.token}"}

            # Debugging output
            #print(f"Fetching bookings for Room: {room_number}, Start Date: {formatted_start_date}, End Date: {formatted_end_date}")
            #print(f"API URL: {api_url}, Headers: {headers}")

            # Make the request
            response = requests.get(api_url, params=params, headers=headers)
            response_data = response.json()

            # Print full API response for debugging
            #print("API Response:", response_data)

            # Handle response

            # Initialize total cost
            
            total_cost = 0.0
            
            if response.status_code == 200:
                if "bookings" in response_data and response_data["bookings"]:
                    self.search_tree.delete(*self.search_tree.get_children())  # Clear table

                    for booking in response_data["bookings"]:
                        cost = float(booking.get("booking_cost", 0))
                        total_cost += cost  # Sum up the total booking cost
                        self.search_tree.insert("", "end", values=(
                            booking.get("id", ""),
                            booking.get("room_number", ""),
                            booking.get("guest_name", ""),
                            booking.get("gender", ""),
                            f"{float(booking.get('booking_cost', 0)) :,.2f}",
                            booking.get("arrival_date", ""),
                            booking.get("departure_date", ""),
                            booking.get("status", ""),
                            booking.get("number_of_days", ""),
                            booking.get("booking_type", ""),
                            booking.get("phone_number", ""),
                            booking.get("booking_date", ""),
                            booking.get("payment_status", ""),
                            booking.get("identification_number", ""),  
                            booking.get("address", ""),                                                   
                            booking.get("created_by", ""),

                            
                        ))

                    # Update total label dynamically
                    self.total_label.config(text=f"Total Booking Cost: {total_cost:,.2f}")
                    # Apply grid effect after inserting data
                    self.apply_grid_effect(self.search_tree)

    
                else:
                    messagebox.showinfo("No Results", f"No bookings found for Room {room_number} between {formatted_start_date} and {formatted_end_date}.")
            else:
                error_message = response_data.get("detail", "Failed to retrieve bookings.")
                messagebox.showerror("Error", error_message)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")



    
    def update_subheading(self, text, command):
        self.subheading_label.config(text=text)
        command()

    




    def update_booking(self):
        """Opens a pop-up window for updating an existing booking with CustomTkinter."""
        self.clear_right_frame()

        # Create a new pop-up window
        update_window = ctk.CTkToplevel(self.root)
        update_window.title("Update Booking")
        update_window.geometry("650x400")  # Match create_booking window size
        update_window.resizable(False, False)
        update_window.configure(fg_color="#f5f5f5")

        # Center the window on the screen
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        x_coordinate = (screen_width - 650) // 2
        y_coordinate = (screen_height - 400) // 2
        update_window.geometry(f"650x400+{x_coordinate}+{y_coordinate}")

        # Make the window modal
        update_window.transient(self.root)
        update_window.grab_set()

        # Header
        header_frame = ctk.CTkFrame(update_window, fg_color="#2c3e50", height=50, corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_label = ctk.CTkLabel(header_frame, text="Update Booking", font=("Arial", 16, "bold"), text_color="white")
        header_label.pack(pady=10)

        # Main Content Frame
        frame = ctk.CTkFrame(update_window, fg_color="white", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Store entries
        self.entries = {}

        # Combo box values
        combo_box_values = {
            "Gender": ["Male", "Female"],
            "Booking Type": ["checked-in", "reservation", "complimentary"]
        }

        # Form Grid Layout
        form_data = [
            ("Booking ID", ctk.CTkEntry, 0, 0),
            ("Room Number", ctk.CTkEntry, 1, 0), ("Guest Name", ctk.CTkEntry, 1, 2),
            ("Identification Number", ctk.CTkEntry, 2, 0), ("Gender", ctk.CTkComboBox, 2, 2),
            ("Address", ctk.CTkEntry, 3, 0, 3),  # Span across columns
            ("Phone Number", ctk.CTkEntry, 4, 0), ("Booking Type", ctk.CTkComboBox, 4, 2),
            ("Arrival Date", DateEntry, 5, 0), ("Departure Date", DateEntry, 5, 2),
        ]

        for label_text, field_type, row, col, colspan in [(*fd, 1) if len(fd) == 4 else fd for fd in form_data]:
            label = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 12, "bold"), text_color="#2c3e50")
            label.grid(row=row, column=col, sticky="w", pady=5, padx=10)

            # Create input fields
            if field_type == ctk.CTkComboBox:
                entry = ctk.CTkComboBox(frame, values=combo_box_values.get(label_text, []), state="readonly",
                                        font=("Helvetica", 12), width=200)
            elif field_type == DateEntry:
                entry = DateEntry(frame, font=("Helvetica", 12), width=12, background='darkblue', foreground='white', borderwidth=2)
            else:
                entry = field_type(frame, font=("Helvetica", 12), width=22 if label_text != "Address" else 50)

            entry.grid(row=row, column=col + 1, columnspan=colspan, pady=5, padx=10, sticky="ew")
            self.entries[label_text] = entry  # Store entry

        # Submit Button
        submit_btn = ctk.CTkButton(
            frame,
            text="Submit Update",
            command=lambda: self.submit_update_booking(update_window),
            font=("Arial", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="white",
            corner_radius=10,
            width=450,
            height=40
        )
        submit_btn.grid(row=6, column=0, columnspan=4, pady=25, padx=30, sticky="ew")  # Center button




    def submit_update_booking(self, update_window):
        """Collects form data and sends a request to update a booking."""
        try:
            booking_data = {
                "booking_id": self.entries["Booking ID"].get(),
                "room_number": self.entries["Room Number"].get(),
                "guest_name": self.entries["Guest Name"].get(),
                 "gender": self.entries["Gender"].get(),
                "identification_number": self.entries["Identification Number"].get(),
                "address": self.entries["Address"].get(),
                "phone_number": self.entries["Phone Number"].get(),
                "arrival_date": self.entries["Arrival Date"].get_date().strftime("%Y-%m-%d"),
                "departure_date": self.entries["Departure Date"].get_date().strftime("%Y-%m-%d"),
                "booking_type": self.entries["Booking Type"].get(),
            }

            # Validate required fields
            if not all(booking_data.values()):
                update_window.grab_release()  # Release grab before showing message
                CTkMessagebox(title="Error", message="Please fill in all fields", icon="cancel", option_1="OK")
                return

            # API request
            api_url = f"http://127.0.0.1:8000/bookings/update/?booking_id={booking_data['booking_id']}"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            response = requests.put(api_url, json=booking_data, headers=headers)

            if response.status_code == 200:
                update_window.grab_release()  # Release grab before showing message
                msgbox = CTkMessagebox(title="Success", message="Booking updated successfully!", icon="check", option_1="OK")
                if msgbox.get() == "OK":
                    update_window.destroy()
            else:
                update_window.grab_release()  # Release grab before showing message
                CTkMessagebox(title="Error", message=response.json().get("detail", "Update failed."), icon="warning", option_1="OK")

        except KeyError as e:
            update_window.grab_release()  # Release grab before showing message
            CTkMessagebox(title="Error", message=f"Missing entry field: {e}", icon="cancel", option_1="OK")
        except requests.exceptions.RequestException as e:
            update_window.grab_release()  # Release grab before showing message
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel", option_1="OK")


    
#from CTkMessagebox import CTkMessagebox


    def guest_checkout(self):
        """Opens a professional pop-up window for guest checkout using CustomTkinter."""
        self.clear_right_frame()

        # 🔹 Create a pop-up window
        checkout_window = ctk.CTkToplevel(self.root)
        checkout_window.title("Guest Checkout")
        checkout_window.geometry("400x250")  # Adjusted for better spacing
        checkout_window.resizable(False, False)
        checkout_window.configure(fg_color="#f5f5f5")  # Light background color

        # Center the window on the screen
        window_width = 400
        window_height = 250
        screen_width = checkout_window.winfo_screenwidth()
        screen_height = checkout_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        checkout_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Make the window modal
        checkout_window.transient(self.root)
        checkout_window.grab_set()

        # 🔹 Dark Header
        header_frame = ctk.CTkFrame(checkout_window, fg_color="#2c3e50", height=50, corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=10)

        header_label = ctk.CTkLabel(header_frame, text="Guest Checkout", font=("Arial", 16, "bold"), text_color="white")
        header_label.pack(pady=10)

        # 🔹 Main Content Frame
        frame = ctk.CTkFrame(checkout_window, fg_color="white", corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 📌 Room Number Field
        label = ctk.CTkLabel(frame, text="Room Number", font=("Helvetica", 12, "bold"), text_color="#2c3e50")
        label.pack(anchor="w", pady=5, padx=10)

        self.room_number_entry = ctk.CTkEntry(frame, font=("Helvetica", 12), width=200)
        self.room_number_entry.pack(pady=5, padx=10)

        # 🔹 Checkout Button with Hover Effect
        submit_btn = ctk.CTkButton(
            frame,
            text="Checkout Guest",
            command=lambda: self.submit_guest_checkout(checkout_window),
            font=("Arial", 14, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="white",
            corner_radius=10,
            width=250,
            height=40
        )
        submit_btn.pack(pady=20)  # Space for better UI

    def submit_guest_checkout(self, checkout_window):
        """Sends a request to checkout the guest by room number."""
        try:
            room_number = self.room_number_entry.get().strip()

            if not room_number:
                CTkMessagebox(title="Error", message="Please enter a valid room number.", icon="cancel")
                return

            api_url = f"http://127.0.0.1:8000/bookings/{room_number}/"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            response = requests.put(api_url, headers=headers)

            if response.status_code == 200:
                checkout_window.grab_release()  # Release grab before showing message
                # Show success message and wait for user to acknowledge
                msgbox = CTkMessagebox(title="Success", message=f"Guest successfully checked out from room {room_number}!",
                                    icon="check", option_1="OK")
                if msgbox.get() == "OK":  # Check if user clicked "OK"
                    checkout_window.destroy()  # Close the window

            else:
                CTkMessagebox(title="Error", message=response.json().get("detail", "Checkout failed."), icon="warning")

        except requests.exceptions.RequestException as e:
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel")

        
            
            
            
    def update_subheading(self, text, command):
        self.subheading_label.config(text=text)
        command()

    



    def cancel_booking(self):
        self.clear_right_frame()
        
        # Open pop-up window
        cancel_window = ctk.CTkToplevel(self.root)
        cancel_window.title("Cancel Booking")
        cancel_window.configure(bg="#f8f9fa")  

        # Window size and position
        window_width, window_height = 400, 270
        x_coordinate = (cancel_window.winfo_screenwidth() - window_width) // 2
        y_coordinate = (cancel_window.winfo_screenheight() - window_height) // 2
        cancel_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Make it modal
        cancel_window.transient(self.root)
        cancel_window.grab_set()

        # Header
        header = ctk.CTkLabel(cancel_window, text="Cancel Booking", font=("Arial", 16, "bold"), fg_color="#2c3e50", text_color="white", pady=10)
        header.pack(fill="x")

        # Form Frame
        form_frame = ctk.CTkFrame(cancel_window, fg_color="white", corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Booking ID Field
        ctk.CTkLabel(form_frame, text="Booking ID", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(5, 0))
        self.booking_id_entry = ctk.CTkEntry(form_frame, font=("Arial", 12), width=260)
        self.booking_id_entry.pack(pady=5)

        # Cancellation Reason
        ctk.CTkLabel(form_frame, text="Reason (Optional)", font=("Arial", 12, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(5, 0))
        self.cancellation_reason_entry = ctk.CTkEntry(form_frame, font=("Arial", 12), width=260)
        self.cancellation_reason_entry.pack(pady=5)

        # Submit Button
        submit_btn = ctk.CTkButton(cancel_window, text="Cancel Booking", font=("Arial", 13, "bold"), fg_color="#d9534f", hover_color="#c9302c",
                                command=lambda: self.submit_cancel_booking(cancel_window))
        submit_btn.pack(pady=15)

    def submit_cancel_booking(self, cancel_window):
        """Handles the booking cancellation request."""
        try:
            booking_id = self.booking_id_entry.get().strip()
            cancellation_reason = self.cancellation_reason_entry.get().strip()

            if not booking_id:
                cancel_window.grab_release()  # Release before showing message
                CTkMessagebox(title="Error", message="Please enter a Booking ID.", icon="cancel")
                return

            # API request
            api_url = f"http://127.0.0.1:8000/bookings/cancel/{booking_id}/"
            if cancellation_reason:
                api_url += f"?cancellation_reason={requests.utils.quote(cancellation_reason)}"

            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            response = requests.post(api_url, headers=headers)

            # Handle response
            if response.status_code == 200:
                cancel_window.grab_release()  # Ensure grab is released
                canceled_booking = response.json().get("canceled_booking", {})

                # Success message
                CTkMessagebox(
                    title="Success",
                    message=f"Booking {canceled_booking.get('id', booking_id)} canceled successfully!\n"
                            f"Room Status: {canceled_booking.get('room_status', 'N/A')}\n"
                            f"Booking Status: {canceled_booking.get('status', 'N/A')}\n"
                            f"Reason: {canceled_booking.get('cancellation_reason', 'None')}",
                    icon="check",
                )

                # Close window after a short delay
                cancel_window.after(500, cancel_window.destroy)

            else:
                cancel_window.grab_release()  # Release before showing message
                CTkMessagebox(title="Error", message=response.json().get("detail", "Cancellation failed."), icon="warning")

        except requests.exceptions.RequestException as e:
            cancel_window.grab_release()
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel")







#class UpdateBooking:
    #def __init__(self, root, token):
        #self.root = tk.Toplevel(root)
        #self.root.title("Update Booking")
        #self.root.geometry("900x600")
        #self.token = token
        #self.root.configure(bg="#f0f0f0")
        
        
        
   



    
    
    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    BookingManagement(root, token="dummy_token")
    root.mainloop()
    
    
