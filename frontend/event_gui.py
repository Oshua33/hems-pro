import tkinter as tk
from tkinter import ttk, messagebox
import requests
from utils import BASE_URL
from tkcalendar import DateEntry
from datetime import datetime
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from utils import export_to_excel, print_excel
import os
import pandas as pd
import sys



class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=12, padding=5, 
                 color="#34495E", hover_color="#1ABC9C", text_color="white", 
                 font=("Helvetica", 10), border_color="#16A085", border_width=2):
        self.command = command
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
        self.width = 130  # Smaller width
        self.height = 30  # Smaller height

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
            self.command()



class EventManagement:
    def __init__(self, root, token):
        self.root = tk.Toplevel(root)
        self.root.title("Event Management")
        self.root.state("zoomed")
        self.root.configure(bg="#f0f0f0")
        
        self.username = "current_user"
        self.token = token


        # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # Set window size and position at the center
        window_width = 1375
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # ========== Main Layout ==========
        self.container = tk.Frame(self.root, bg="#ECF0F1", padx=10, pady=10)  # Light background for overall app
        self.container.pack(fill=tk.BOTH, expand=True)

        # Header Frame
        self.header_frame = tk.Frame(self.container, bg="#2C3E50", height=50)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))  # More breathing room after header
        self.header_frame.pack_propagate(False)  # Prevent auto resizing based on child widgets

        # Title Label (left side of header)
        self.title_label = tk.Label(
            self.header_frame,
            text="                                                                                               🎉Event Management",
            font=("Helvetica", 16, "bold"),
            fg="gold",
            bg="#2C3E50",
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT, padx=20)  # Padding left so it doesn't stick to edge

        # Action Frame (right side of header)
        self.action_frame = tk.Frame(self.header_frame, bg="#2C3E50")
        self.action_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        # Add buttons to action frame (example: Export and Print buttons)
        self.export_button = RoundedButton(
            self.action_frame,
            text="📊 Export to Excel",
            command=lambda: self.export_report(),
            radius=10,
            color="#95A5A6",
            hover_color="#16A085",
            text_color="white",
            border_color="#16A085",
            font=("Helvetica", 9, "bold"),
            border_width=2
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.print_button = RoundedButton(
            self.action_frame,
            text="🖨 Print Report",
            command=lambda: self.print_report(),
            radius=10,
            color="#95A5A6",
            hover_color="#16A085",
            text_color="white",
            border_color="#16A085",
            font=("Helvetica", 9, "bold"),
            border_width=2
        )
        self.print_button.pack(side=tk.LEFT, padx=5)

        

         # ==== Main Content Frame (Holds Sidebar + Right Section) ====
        self.main_frame = tk.Frame(self.container, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

         # ==== Menu Container (With "Menu" Heading) ====
        self.Menu = tk.Frame(self.main_frame, bg="#2C3E50", width=200)
        self.Menu.pack(side=tk.LEFT, fill=tk.Y)

        # === "Menu" Heading ===
        self.menu_label = tk.Label(self.Menu, text="MENU", font=("Helvetica", 12, "bold"), 
                                   fg="white", bg="#34495E", pady=5)
        self.menu_label.pack(fill=tk.X)

        # Sidebar Section (Inside `Menu` Frame)
        self.left_frame = tk.Frame(self.Menu, bg="#2C3E50", width=230)
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Right Section (Main Content)
        self.right_frame = tk.Frame(self.main_frame, bg="#ffffff", relief="ridge", borderwidth=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Subheading Label
        self.subheading_label = tk.Label(self.right_frame, text="Select an option",
                                         font=("Helvetica", 14, "bold"), fg="#2C3E50", bg="#ffffff")
        self.subheading_label.pack(pady=10)
 
        # Event Action Buttons
        self.buttons = []
        event_buttons = [
            ("Create Event", self.create_event),
            ("List Event", self.list_events),
            ("Sort by ID", self.search_event_by_id),
            ("Update Event", self.update_event),
            ("Cancel Event", self.cancel_event),
        ]

        for text, command in event_buttons:
            rb = RoundedButton(
                self.left_frame,
                text=text,
                command=lambda t=text, c=command: self.update_subheading(t, c),
                radius=15,
                color="#34495E",
                hover_color="#1ABC9C",
                font=("Helvetica", 10)
            )
            rb.pack(anchor="w", padx=(8, 0), pady=2)  # <<< only pad from the left

        # Separation Line
        separator = tk.Frame(self.left_frame, height=4, bg="#ECF0F1")
        separator.pack(fill="x", padx=5, pady=10)

        # Event Payment Buttons
        payment_buttons = [
            ("Create Payment", self.create_event_payment),
            ("List Payments", self.list_events_payment),
            ("Sort By Status", self.list_payment_by_status),
            ("Sort Payment ID", self.search_payment_by_id),
            ("Debtor List", self.event_debtor_list),
            ("Void Payment", self.void_payment),
        ]

        for text, command in payment_buttons:
            rb = RoundedButton(
                self.left_frame,
                text=text,
                command=lambda t=text, c=command: self.update_subheading(t, c),
                radius=15,
                color="#34495E",
                hover_color="#1ABC9C",
                font=("Helvetica", 10)
            )
            rb.pack(anchor="w", padx=(8, 0), pady=2)  # <<< only pad from the left


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
        

    def update_subheading(self, text, command):
        self.subheading_label.config(text=text)
        command()
     
    def export_report(self):
        if not hasattr(self, "tree") or not self.tree.get_children():
            messagebox.showwarning("Warning", "No data available to export.")
            return

        if not self.current_view:
            messagebox.showwarning("Warning", "No view selected for export.")
            return

        columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        rows = [
            [self.tree.item(item)["values"][i] for i in range(len(columns))]
            for item in self.tree.get_children()
        ]

        df = pd.DataFrame(rows, columns=columns)

        file_name_map = {
            "event_list": ("event_list_report.xlsx", "Event List Report"),
            "event_payments": ("event_payment_report.xlsx", "Event Payments Report"),
            "event_debtors": ("event_debtor_report.xlsx", "Event Debtors Report"),
        }

        mapped = file_name_map.get(self.current_view)
        if not mapped:
            messagebox.showerror("Error", "Unknown event report view selected.")
            return

        file_name, report_title = mapped
        file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)

        try:
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                sheet_name = self.current_view.replace("_", " ").title()
                df.to_excel(writer, sheet_name=sheet_name, startrow=5, index=False)

                workbook = writer.book
                worksheet = writer.sheets[sheet_name]

                # === Styles ===
                title_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 16
                })

                timestamp_format = workbook.add_format({'italic': True, 'font_size': 10})
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#DDEBF7',
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                cell_format = workbook.add_format({'border': 1, 'valign': 'top'})

                # === Merge Title ===
                worksheet.merge_range('A1:E1', report_title, title_format)
                worksheet.write('A3', f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_format)

                # === Format Headers ===
                for col_num, col_name in enumerate(columns):
                    worksheet.write(5, col_num, col_name, header_format)

                # === Apply border to cells ===
                for row_num in range(len(rows)):
                    for col_num in range(len(columns)):
                        worksheet.write(row_num + 6, col_num, rows[row_num][col_num], cell_format)

                # === Autofit columns ===
                for i, col in enumerate(columns):
                    col_width = max(len(str(col)), max(len(str(row[i])) for row in rows if row[i] is not None))
                    worksheet.set_column(i, i, col_width + 2)

                # === Summary Section ===
                start_row = len(rows) + 8
                col_span = len(columns)
                end_col_letter = chr(64 + col_span) if col_span <= 26 else 'Z'  # fallback if columns > 26
                summary_range = f"A{start_row+1}:{end_col_letter}{start_row+1}"

                # Merge the summary title across all columns
                worksheet.merge_range(summary_range, "Summary", header_format)

                def extract_amount(label_widget):
                    if not label_widget:
                        return "N/A"
                    text = label_widget.cget("text")
                    parts = text.split(":", 1)
                    if len(parts) > 1:
                        try:
                            amount = float(parts[1].strip().replace(",", ""))
                            return "{:,.0f}".format(amount)
                        except ValueError:
                            return "N/A"
                    return "N/A"

                def write_summary_row(row_offset, label_text, label_widget):
                    worksheet.write(start_row + row_offset, 0, label_text, header_format)
                    worksheet.write(start_row + row_offset, 1, extract_amount(label_widget), cell_format)

                if self.current_view == "event_payments":
                    write_summary_row(2, "Cash", getattr(self, "total_cash_label", None))
                    write_summary_row(3, "POS Card", getattr(self, "total_pos_label", None))
                    write_summary_row(4, "Bank Transfer", getattr(self, "total_bank_label", None))
                    write_summary_row(5, "Total Amount", getattr(self, "total_label", None))

                elif self.current_view == "event_debtors":
                    write_summary_row(2, "Current Debt", getattr(self, "total_current_label", None))
                    write_summary_row(3, "Gross Debt", getattr(self, "total_gross_label", None))

                elif self.current_view == "event_list":
                    write_summary_row(2, "Total Amount", getattr(self, "total_label", None))

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

    def create_event(self):
        self.clear_right_frame()

        create_window = ctk.CTkToplevel(self.root)
        create_window.title("Create Event")
        create_window.geometry("620x380")
        create_window.resizable(False, False)

        # Center the window
        screen_width = create_window.winfo_screenwidth()
        screen_height = create_window.winfo_screenheight()
        x_position = (screen_width - 620) // 2
        y_position = (screen_height - 380) // 2
        create_window.geometry(f"620x380+{x_position}+{y_position}")

        create_window.transient(self.root)
        create_window.grab_set()

        # 🔷 Dark header bar
        header_frame = ctk.CTkFrame(create_window, fg_color="#2c3e50", height=50)
        header_frame.pack(fill="x")
        header_label = ctk.CTkLabel(header_frame, text="Create Event", font=("Arial", 18, "bold"), text_color="white")
        header_label.pack(pady=10)

        form_frame = ctk.CTkFrame(create_window, corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        form_frame.columnconfigure((0, 2), weight=1)
        form_frame.columnconfigure(1, weight=2)
        form_frame.columnconfigure(3, weight=2)

        self.entries = {}

        def add_field(row, col, label_text, widget_type, **kwargs):
            label = ctk.CTkLabel(form_frame, text=label_text + ":", font=("Arial", 13))
            label.grid(row=row, column=col, sticky="w", padx=10, pady=6)

            if widget_type == ctk.CTkTextbox:
                entry = widget_type(form_frame, height=60, **kwargs)
            elif widget_type == DateEntry:
                entry = widget_type(form_frame, width=16, background="darkblue", foreground="white", borderwidth=2)
            else:
                entry = widget_type(form_frame, **kwargs)

            entry.grid(row=row, column=col + 1, sticky="ew", padx=10, pady=6)
            self.entries[label_text] = entry

        # 🔸 Side-by-side fields
        add_field(0, 0, "Organizer", ctk.CTkEntry)
        add_field(0, 2, "Title", ctk.CTkEntry)

        add_field(1, 0, "Start Date", DateEntry)
        add_field(1, 2, "End Date", DateEntry)

        add_field(2, 0, "Event Amount", ctk.CTkEntry)
        add_field(2, 2, "Caution Fee", ctk.CTkEntry)

        add_field(3, 0, "Phone Number", ctk.CTkEntry)
        add_field(3, 2, "Location", ctk.CTkEntry)

        # 🔸 Description (medium width)
        label = ctk.CTkLabel(form_frame, text="Description:", font=("Arial", 13))
        label.grid(row=4, column=0, sticky="nw", padx=10, pady=6)
        desc_box = ctk.CTkTextbox(form_frame, height=20)
        desc_box.grid(row=4, column=1, columnspan=3, sticky="ew", padx=10, pady=6)
        self.entries["Description"] = desc_box

        # 🔸 Address (longer)
        label = ctk.CTkLabel(form_frame, text="Address:", font=("Arial", 13))
        label.grid(row=5, column=0, sticky="w", padx=10, pady=6)
        address_entry = ctk.CTkEntry(form_frame)
        address_entry.grid(row=5, column=1, columnspan=3, sticky="ew", padx=10, pady=6)
        self.entries["Address"] = address_entry

        # 🔸 Buttons
        btn_frame = ctk.CTkFrame(create_window, fg_color="transparent")
        btn_frame.pack(pady=10)

        submit_btn = ctk.CTkButton(btn_frame, text="Submit", command=lambda: self.submit_event(create_window))
        submit_btn.grid(row=0, column=0, padx=10)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="#aaaaaa", hover_color="#888888", command=create_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)





    def submit_event(self, create_window):
        try:
            created_by = self.username

            event_data = {
                "organizer": self.entries["Organizer"].get(),
                "title": self.entries["Title"].get(),
                "description": self.entries["Description"].get("1.0", "end-1c"),
                "start_datetime": self.entries["Start Date"].get_date().strftime("%Y-%m-%d"),
                "end_datetime": self.entries["End Date"].get_date().strftime("%Y-%m-%d"),
                "event_amount": self.entries["Event Amount"].get(),
                "caution_fee": self.entries["Caution Fee"].get(),
                "location": self.entries["Location"].get(),
                "phone_number": self.entries["Phone Number"].get(),
                "address": self.entries["Address"].get(),
                "payment_status": "active",
                "created_by": created_by,
            }

            if not all(event_data.values()):
                CTkMessagebox(title="Error", message="Please fill in all fields", icon="cancel")
                return

            url = "http://127.0.0.1:8000/events/"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            response = requests.post(url, json=event_data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                event_id = response_data.get("id")

                if event_id:
                    create_window.destroy()
                    self.root.after(100, lambda: CTkMessagebox(
                        title="Success",
                        message=f"Event created successfully!\nEvent ID: {event_id}",
                        icon="check"
                    ))
                else:
                    CTkMessagebox(title="Error", message="Event ID missing in response.", icon="cancel")

            else:
                CTkMessagebox(title="Error", message=response.json().get("detail", "Event creation failed."), icon="cancel")

        except KeyError as e:
            CTkMessagebox(title="Error", message=f"Missing field: {e}", icon="cancel")
        except requests.exceptions.RequestException as e:
            CTkMessagebox(title="Error", message=f"Request failed: {e}", icon="cancel")
    
    
    
    def list_events(self):
        """List events with filtering by date."""
        self.clear_right_frame()
        self.current_view = "event_list"

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="📅 List Events", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # ---------------- Filter Section ---------------- #
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        fetch_btn = ttk.Button(filter_frame, text="🔍 Fetch Events", command=lambda: self.fetch_events(self.start_date, self.end_date))
        fetch_btn.grid(row=0, column=4, padx=10, pady=5)

                # ---------------- Event Table ---------------- #
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Apply bold font styling for Treeview headings
        style = ttk.Style()
        style.theme_use("clam")  # Ensures styling is applied
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), foreground="black")

        columns = ("Event ID", "Organizer", "Title", "Event_Amount", "Caution_Fee", 
                "Start Date", "End Date", "Location", "Phone", "Status/Payment", "Created_at","created_by")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")  # Centered heading
            self.tree.column(col, width=80, anchor="center")    # Adjust width and center text

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        # Total Amount Label
        self.total_label = tk.Label(frame, text="Total Event Amount: 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_label.pack(pady=10)

    def fetch_events(self, start_date_entry, end_date_entry):
        """Fetch events from API and populate the table."""
        api_url = "http://127.0.0.1:8000/events"
        params = {
            "start_date": start_date_entry.get_date().strftime("%Y-%m-%d"),
            "end_date": end_date_entry.get_date().strftime("%Y-%m-%d"),
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                events = response.json()
                self.tree.delete(*self.tree.get_children())  # Clear table
                total_amount = 0

                for event in events:
                    payment_status = event.get("payment_status", "").lower()
                    event_amount = float(event.get("event_amount", 0))

                    # Only add to total if the event is not cancelled
                    if payment_status != "cancelled":
                        total_amount += event_amount

                    self.tree.insert("", "end", values=(
                        event.get("id", ""),
                        event.get("organizer", ""),
                        event.get("title", ""),
                        f"{event_amount:,.2f}",
                        f"{float(event.get('caution_fee', 0)) :,.2f}",
                        event.get("start_datetime", ""),
                        event.get("end_datetime", ""),
                        event.get("location", ""),
                        event.get("phone_number", ""),
                        payment_status,
                        event.get("created_at", ""),
                        event.get("created_by", ""),
                    ))

                self.apply_grid_effect()

                self.total_label.config(text=f"Total Event Amount: {total_amount:,.2f}")

                if not events:
                    messagebox.showinfo("No Results", "No events found for the selected filters.")
                    self.total_label.config(text="Total Event Amount: 0.00")

            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve events."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

    def clear_right_frame(self):
        """Clears the right frame before rendering new content."""
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()





    

    
    
    def search_event_by_id(self):
        self.clear_right_frame()
        
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Search Event by ID", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)
        
        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=5)
        
        tk.Label(search_frame, text="Event ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.event_id_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.event_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        search_btn = ttk.Button(
            search_frame, text="Search", command=self.fetch_event_by_id
        )
        search_btn.grid(row=0, column=2, padx=10, pady=5)
        
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Organizer", "Title", "Event_Amount", "Caution_Fee", "Start Date", "End Date", 
                "Location", "Phone Number", "Payment Status", "Created_by")
        
        if hasattr(self, "tree"):
            self.tree.destroy()

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

    def fetch_event_by_id(self):
        event_id = self.event_id_entry.get().strip()

        if not event_id.isdigit():  # Ensure input is numeric
            messagebox.showerror("Error", "Please enter a valid numeric event ID.")
            return
        
        try:
            api_url = f"http://127.0.0.1:8000/events/{event_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
        
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                event = response.json()
                
                # Ensure the event details exist
                if event:
                    self.tree.delete(*self.tree.get_children())
                    self.tree.insert("", "end", values=(
                        event.get("id", ""),
                        event.get("organizer", ""),
                        event.get("title", ""),
                        #f"₦{float(booking.get('booking_cost', 0)) :,.2f}",
                        f"{float(event.get('event_amount', 0)) :,.2f}",
                        f"{float(event.get('caution_fee', 0)) :,.2f}",
                        event.get("start_datetime", ""),
                        event.get("end_datetime", ""),
                        event.get("location", ""),
                        event.get("phone_number", ""),
                        event.get("payment_status", ""),
                        event.get("created_by", ""),
                    ))

                    self.apply_grid_effect(self.tree)
                else:
                    messagebox.showinfo("No Results", "No event found with the provided ID.")
            else:
                messagebox.showerror("Error", response.json().get("detail", "No event found."))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
  
        
        
    def update_event(self):
        self.clear_right_frame()
        """Opens a professional pop-up window for updating an event using CustomTkinter."""

        self.update_window = ctk.CTkToplevel(self.root)
        self.update_window.title("Update Event")
        self.update_window.geometry("620x450")
        self.update_window.resizable(False, False)

        # Center the window on the screen
        screen_width = self.update_window.winfo_screenwidth()
        screen_height = self.update_window.winfo_screenheight()
        x_coordinate = (screen_width - 620) // 2
        y_coordinate = (screen_height - 450) // 2
        self.update_window.geometry(f"620x450+{x_coordinate}+{y_coordinate}")

        # Make the window modal
        self.update_window.transient(self.root)
        self.update_window.grab_set()

        # 🔷 Dark header bar
        header_frame = ctk.CTkFrame(self.update_window, fg_color="#2c3e50", height=50, corner_radius=8)
        header_frame.pack(fill="x")
        header_label = ctk.CTkLabel(header_frame, text="Update Event", font=("Arial", 18, "bold"), text_color="white")
        header_label.pack(pady=10)

        # Main Content Frame
        form_frame = ctk.CTkFrame(self.update_window, corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        form_frame.columnconfigure((0, 2), weight=1)
        form_frame.columnconfigure(1, weight=2)
        form_frame.columnconfigure(3, weight=2)

        self.entries = {}

        def add_field(row, col, label_text, widget_type, **kwargs):
            label = ctk.CTkLabel(form_frame, text=label_text + ":", font=("Arial", 13))
            label.grid(row=row, column=col, sticky="w", padx=10, pady=6)

            if widget_type == ctk.CTkTextbox:
                entry = widget_type(form_frame, height=80, **kwargs)  # Increased height for Description
            elif widget_type == DateEntry:
                entry = widget_type(form_frame, width=16, background="darkblue", foreground="white", borderwidth=2)
            else:
                entry = widget_type(form_frame, **kwargs)

            entry.grid(row=row, column=col + 1, sticky="ew", padx=10, pady=6)
            self.entries[label_text] = entry

        # 🔸 Event ID Field (Added)
        add_field(0, 0, "Event ID", ctk.CTkEntry)
        
        # 🔸 Side-by-side fields
        add_field(1, 0, "Organizer", ctk.CTkEntry)
        add_field(1, 2, "Title", ctk.CTkEntry)

        add_field(2, 0, "Start Date", DateEntry)
        add_field(2, 2, "End Date", DateEntry)

        add_field(3, 0, "Event Amount", ctk.CTkEntry)
        add_field(3, 2, "Caution Fee", ctk.CTkEntry)

        add_field(4, 0, "Phone Number", ctk.CTkEntry)
        add_field(4, 2, "Location", ctk.CTkEntry)

        # 🔸 Description (medium width with increased height)
        label = ctk.CTkLabel(form_frame, text="Description:", font=("Arial", 13))
        label.grid(row=5, column=0, sticky="nw", padx=10, pady=6)
        desc_box = ctk.CTkTextbox(form_frame, height=30)  # Increased height for better visibility
        desc_box.grid(row=5, column=1, columnspan=3, sticky="ew", padx=10, pady=6)
        self.entries["Description"] = desc_box

        # 🔸 Address (longer)
        label = ctk.CTkLabel(form_frame, text="Address:", font=("Arial", 13))
        label.grid(row=6, column=0, sticky="w", padx=10, pady=6)
        address_entry = ctk.CTkEntry(form_frame)
        address_entry.grid(row=6, column=1, columnspan=3, sticky="ew", padx=10, pady=6)
        self.entries["Address"] = address_entry

        # 🔸 Payment Status (Dropdown)
        add_field(7, 0, "Status", ctk.CTkComboBox, values=["active", "complete", "incomplete", "cancelled"])

        # 🔸 Buttons
        btn_frame = ctk.CTkFrame(self.update_window, fg_color="transparent")
        btn_frame.pack(pady=10)

        submit_btn = ctk.CTkButton(btn_frame, text="Submit Update", command=lambda: self.submit_update_event(), font=("Arial", 14, "bold"), fg_color="#3498db", hover_color="#2980b9", text_color="white", corner_radius=10, width=200, height=30)
        submit_btn.grid(row=0, column=0, padx=10)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="#aaaaaa", hover_color="#888888", command=self.update_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)





    def submit_update_event(self):
        """Collects form data and sends a request to update an event."""
        try:
            event_id = self.entries["Event ID"].get().strip()
            if not event_id.isdigit():
                messagebox.showerror("Error", "Event ID must be a valid number.")
                return
            
            # Collect form data
            event_data = {
                "organizer": self.entries["Organizer"].get().strip(),
                "title": self.entries["Title"].get().strip(),
                "description": self.entries["Description"].get("1.0", "end").strip(),
                "location": self.entries["Location"].get().strip(),
                "phone_number": self.entries["Phone Number"].get().strip(),
                "address": self.entries["Address"].get().strip(),
                "start_datetime": self.entries["Start Date"].get_date().strftime("%Y-%m-%d"),
                "end_datetime": self.entries["End Date"].get_date().strftime("%Y-%m-%d"),
                "event_amount": float(self.entries["Event Amount"].get().strip() or 0),
                "caution_fee": float(self.entries["Caution Fee"].get().strip() or 0),
                "payment_status": self.entries["Payment Status"].get().strip(),
            }

            # Validate that required fields are not empty
            if not all(event_data.values()):
                messagebox.showerror("Error", "All fields must be filled.")
                return

            api_url = f"http://127.0.0.1:8000/events/{event_id}"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

            response = requests.put(api_url, json=event_data, headers=headers)

            if response.status_code == 200:
                messagebox.showinfo("Success", "Event updated successfully!")
                self.update_window.destroy()  # ✅ Close popup on success
            else:
                messagebox.showerror("Error", response.json().get("detail", "Update failed."))

        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input for Event Amount or Caution Fee.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
            
      
    def cancel_event(self):
            self.clear_right_frame()

            cancel_window = tk.Toplevel(self.root)
            cancel_window.title("Cancel Event")
            cancel_window.configure(bg="#2c3e50")

            window_width = 470
            window_height = 260  # Reduced a bit too
            screen_width = cancel_window.winfo_screenwidth()
            screen_height = cancel_window.winfo_screenheight()
            x_coordinate = (screen_width - window_width) // 2
            y_coordinate = (screen_height - window_height) // 2
            cancel_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

            cancel_window.transient(self.root)
            cancel_window.grab_set()

            # === Header Frame ===
            header_frame = tk.Frame(cancel_window, bg="#1abc9c", height=50)
            header_frame.pack(fill=tk.X)

            header_label = tk.Label(header_frame, text="Cancel Event", font=("Century Gothic", 16, "bold"),
                                    fg="white", bg="#1abc9c", pady=10)
            header_label.pack()

            # === Outer Content Frame ===
            outer_frame = tk.Frame(cancel_window, bg="#ecf0f1", padx=15, pady=20)
            outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

            # === Data Entry Section ===
            form_frame = tk.Frame(outer_frame, bg="#ecf0f1")
            form_frame.pack(fill=tk.X, pady=(0, 20))

            fields = [
                ("Event ID", tk.Entry),
                ("Cancellation Reason", tk.Entry),
            ]
            self.entries = {}

            for i, (label_text, field_type) in enumerate(fields):
                label = tk.Label(form_frame, text=label_text, font=("Helvetica", 10, "bold"),
                                bg="#ecf0f1", fg="#2c3e50")
                label.grid(row=i, column=0, sticky="w", pady=5, padx=(5, 10))

                # Frame around each Entry
                entry_outer_frame = tk.Frame(form_frame, bg="white", relief="groove", borderwidth=2)
                entry_outer_frame.grid(row=i, column=1, sticky="ew", pady=5)

                entry = field_type(entry_outer_frame, font=("Helvetica", 10), width=28,
                                bg="white", fg="black", relief="flat")
                entry.pack(fill=tk.X, padx=4, pady=3)  # Smaller vertical padding!

                self.entries[label_text] = entry

            form_frame.columnconfigure(1, weight=1)

            # === Buttons Frame ===
            btn_frame = tk.Frame(outer_frame, bg="#ecf0f1")
            btn_frame.pack()

            submit_btn = RoundedButton(
                btn_frame,
                text="Submit",
                command=lambda: self.submit_cancel_event(cancel_window),
                radius=14,
                padding=8,  # Slightly smaller buttons too
                color="#1abc9c",
                hover_color="#16a085",
                text_color="white",
                font=("Helvetica", 10, "bold"),
                border_color="#16a085",
                border_width=2,
            )
            submit_btn.grid(row=0, column=0, padx=15)

            cancel_btn = RoundedButton(
                btn_frame,
                text="Cancel",
                command=cancel_window.destroy,
                radius=14,
                padding=8,
                color="#e74c3c",
                hover_color="#c0392b",
                text_color="white",
                font=("Helvetica", 10, "bold"),
                border_color="#c0392b",
                border_width=2,
            )
            cancel_btn.grid(row=0, column=1, padx=15)


        
    def submit_cancel_event(self, cancel_window):
        """Sends a request to cancel an event by event ID, including the cancellation reason."""
        try:
            event_id = self.entries["Event ID"].get().strip()  # Ensure input is stripped
            cancellation_reason = self.entries["Cancellation Reason"].get().strip()  # Ensure proper retrieval

            if not event_id:
                messagebox.showerror("Error", "Please enter an Event ID.")
                return

            if not cancellation_reason:
                messagebox.showerror("Error", "Cancellation reason is required.")
                return

            # Construct the API URL with cancellation reason as a query parameter
            api_url = f"http://127.0.0.1:8000/events/{event_id}/cancel?cancellation_reason={requests.utils.quote(cancellation_reason)}"

            headers = {"Authorization": f"Bearer {self.token}"}

            # Send PUT request without JSON body since params are in the URL
            response = requests.put(api_url, headers=headers)

            if response.status_code == 200:
                messagebox.showinfo("Success", f"Event ID {event_id} has been successfully canceled!\n"
                                            f"Cancellation Reason: {cancellation_reason}")
                cancel_window.destroy()  # Close the pop-up
            else:
                messagebox.showerror("Error", response.json().get("detail", "Cancellation failed."))

        except KeyError as e:
            messagebox.showerror("Error", f"Missing entry field: {e}")  # Handle missing key errors
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

                
    

    def create_event_payment(self):
        """Displays a modern CTk popup window for event payment entry (centered layout)."""
        self.clear_right_frame()

        self.payment_window = ctk.CTkToplevel(self.root)
        self.payment_window.title("Create Event Payment")
        self.payment_window.geometry("500x350")
        self.payment_window.resizable(False, False)

        # Center the window on screen
        window_width, window_height = 500, 350
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.payment_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.payment_window.transient(self.root)
        self.payment_window.grab_set()

        # 🔷 Dark header
        header_frame = ctk.CTkFrame(self.payment_window, fg_color="#2c3e50", height=50)
        header_frame.pack(fill="x")
        header_label = ctk.CTkLabel(header_frame, text="Create Event Payment", font=("Arial", 17, "bold"), text_color="white")
        header_label.pack(pady=10)

        # 🔷 Form Frame
        form_frame = ctk.CTkFrame(self.payment_window, corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=2)

        # 🔷 Fields
        fields = [
            ("Event ID", ctk.CTkEntry),
            ("Organiser", ctk.CTkEntry),
            ("Amount Paid", ctk.CTkEntry),
            ("Discount Allowed", ctk.CTkEntry),
            ("Payment Method", ctk.CTkComboBox)
        ]

        self.entries = {}

        for i, (label_text, widget_type) in enumerate(fields):
            label = ctk.CTkLabel(form_frame, text=label_text + ":", font=("Arial", 13))
            label.grid(row=i, column=0, sticky="e", padx=10, pady=7)

            if widget_type == ctk.CTkComboBox:
                entry = widget_type(form_frame, values=["Cash", "POS Card", "Bank Transfer"], state="readonly")
                entry.set("Cash")
            else:
                entry = widget_type(form_frame)

            entry.grid(row=i, column=1, sticky="w", padx=10, pady=7)
            self.entries[label_text] = entry

        # 🔷 Submit Button (centered in frame)
        submit_btn = ctk.CTkButton(self.payment_window, text="Submit Payment", width=270, command=self.submit_event_payment)
        submit_btn.pack(pady=15)




    def submit_event_payment(self):
        """Handles event payment submission to the backend with structured validation and error handling."""
        try:
            errors = []  # ✅ Collect all validation errors

            # 🔹 Validate Event ID
            event_id_str = self.entries["Event ID"].get().strip()
            if not event_id_str.isdigit():
                errors.append("Event ID must be a valid integer.")

            # 🔹 Validate Organiser
            organiser = self.entries["Organiser"].get().strip()
            if not organiser:
                errors.append("Organiser name is required.")

            # 🔹 Validate Amount Paid
            amount_paid_str = self.entries["Amount Paid"].get().strip()
            if not amount_paid_str.replace(".", "", 1).isdigit():
                errors.append("Amount Paid must be a valid number.")

            # 🔹 Validate Discount Allowed (Optional)
            discount_str = self.entries["Discount Allowed"].get().strip()
            discount_allowed = float(discount_str) if discount_str.replace(".", "", 1).isdigit() else 0.0

            # 🔹 Validate Payment Method
            payment_method = self.entries["Payment Method"].get().strip()
            if not payment_method:
                errors.append("Payment Method is required.")

            # ❌ If errors found, show all at once
            if errors:
                self.payment_window.grab_release()
                CTkMessagebox(title="Error", message="\n".join(errors), icon="cancel")
                return

            # ✅ Convert validated values
            event_id = int(event_id_str)
            amount_paid = float(amount_paid_str)

            # ✅ Prepare data
            payload = {
                "event_id": event_id,
                "organiser": organiser,
                "amount_paid": amount_paid,
                "discount_allowed": discount_allowed,
                "payment_method": payment_method,
                "created_by": self.username
            }

            # ✅ Make request
            url = "http://127.0.0.1:8000/eventpayment/"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            if response.status_code == 200:
                payment_details = data.get("payment_details", {})  # adjust if your API returns something else
                payment_id = payment_details.get("payment_id")
                created_by = payment_details.get("created_by", self.username)

                # ✅ Success feedback
                self.payment_window.destroy()
                self.root.after(100, lambda: CTkMessagebox(
                    title="Success",
                    message=f"Event Payment created successfully!",
                    icon="check"
                ))
            else:
                self.payment_window.grab_release()
                CTkMessagebox(title="Error", message=data.get("detail", "Payment failed."), icon="cancel")

        except Exception as e:
            self.payment_window.grab_release()
            CTkMessagebox(title="Error", message=f"Unexpected error occurred: {e}", icon="cancel")




    def list_events_payment(self):
        self.clear_right_frame()
        self.current_view = "event_payments"
        
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Event Payments", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

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
            text="Fetch Payments",
            command=lambda: self.fetch_event_payments(self.start_date, self.end_date)
        )
        fetch_btn.grid(row=0, column=4, padx=10, pady=5)

        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Payment ID", "Event ID", "Organiser", "Event Amount", "Amount Paid", "Discount Allowed", 
                   "Balance Due", "Payment Method", "Payment Status", "Payment Date", "Created By")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        self.total_payment_label = tk.Label(frame, text="", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_payment_label.pack(pady=10)

      # Payment Breakdown Frame (Closer to Summary Frame)
        breakdown_frame = tk.Frame(frame, bg="#ffffff", padx=1, pady=1)  # Reduced padding
        breakdown_frame.pack(fill=tk.X, pady=1)  # Reduced vertical spacing

        self.total_cash_label = tk.Label(breakdown_frame, text="Total Cash: 0", font=("Arial", 12), bg="#ffffff", fg="red")
        self.total_cash_label.grid(row=0, column=0, padx=10)  # Reduced horizontal spacing

        self.total_pos_label = tk.Label(breakdown_frame, text="Total POS Card: 0", font=("Arial", 12), bg="#ffffff", fg="blue")
        self.total_pos_label.grid(row=0, column=1, padx=10)

        self.total_bank_label = tk.Label(breakdown_frame, text="Total Bank Transfer: 0", font=("Arial", 12), bg="#ffffff", fg="purple")
        self.total_bank_label.grid(row=0, column=2, padx=10)

        self.total_label = tk.Label(breakdown_frame, text="Total Amount: 0", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_label.grid(row=0, column=3, padx=10)

    def fetch_event_payments(self, start_date_entry, end_date_entry):
        api_url = "http://127.0.0.1:8000/eventpayment/"
        params = {
            "start_date": start_date_entry.get_date().strftime("%Y-%m-%d"),
            "end_date": end_date_entry.get_date().strftime("%Y-%m-%d"),
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                response_data = response.json()

                # Extract and validate data
                data = response_data.get("payments", [])
                summary = response_data.get("summary", {})

                if not isinstance(data, list):
                    messagebox.showerror("Error", "Unexpected API response format")
                    return

                if not data:
                    self.total_payment_label.config(text="Total Payments: 0.00")
                    messagebox.showinfo("No Results", "No payments found for the selected filters.")
                    return

                self.tree.delete(*self.tree.get_children())
                total_amount_paid = 0

                for payment in data:
                    payment_status = payment.get("payment_status", "").lower()
                    if payment_status != "voided":
                        total_amount_paid += float(payment.get("amount_paid", 0))

                    self.tree.insert("", "end", values=(
                        payment.get("id", ""),
                        payment.get("event_id", ""),
                        payment.get("organiser", ""),
                        f"{float(payment.get('event_amount', 0)):,.2f}",
                        f"{float(payment.get('amount_paid', 0)):,.2f}",
                        f"{float(payment.get('discount_allowed', 0)):,.2f}",
                        f"{float(payment.get('balance_due', 0)):,.2f}",
                        payment.get("payment_method", ""),
                        payment.get("payment_status", ""),
                        payment.get("payment_date", ""),
                        payment.get("created_by", ""),
                    ))

                self.total_payment_label.config(
                    text=f"Total Payments: {total_amount_paid:,.2f}"
                )

                # Update summary labels
                self.total_cash_label.config(text=f"Total Cash: {summary.get('total_cash', 0):,.2f}")
                self.total_pos_label.config(text=f"Total POS Card: {summary.get('total_pos', 0):,.2f}")
                self.total_bank_label.config(text=f"Total Bank Transfer: {summary.get('total_transfer', 0):,.2f}")
                self.total_label.config(text=f"Total Amount: {summary.get('total_payment', 0):,.2f}")

            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve payments."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")





    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()


    def event_debtor_list(self):
        self.clear_right_frame()
        self.current_view = "event_debtors"

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Event Debtor List", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Organizer Name:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.organizer_name_entry = tk.Entry(filter_frame, font=("Arial", 11))
        self.organizer_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.set_date(datetime.today())
        self.end_date.grid(row=0, column=5, padx=5, pady=5)

        fetch_btn = ttk.Button(filter_frame, text="Fetch Debtor List", command=self.fetch_event_debtor_list)
        fetch_btn.grid(row=0, column=6, padx=10, pady=5)

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = (
            "Event ID", "Organizer", "Title", "Start Date", "End Date", "Event Amount",
            "Caution Fee", "Total Paid", "Balance Due","Location", "Phone", "Address", 
             "Created At", "Last Payment Date"
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        self.total_frame = tk.Frame(self.right_frame, bg="#ffffff", pady=2)
        self.total_frame.pack(fill=tk.X)

        self.total_current_label = tk.Label(
            self.total_frame, text="Total Current Debt: 0.00", font=("Arial", 12, "bold"),
            bg="#ffffff", fg="blue"
        )
        self.total_current_label.grid(row=0, column=0, padx=120, pady=2)

        self.total_gross_label = tk.Label(
            self.total_frame, text="Total Gross Debt: 0.00", font=("Arial", 12, "bold"),
            bg="#ffffff", fg="red"
        )
        self.total_gross_label.grid(row=0, column=1, padx=20, pady=2)


    def fetch_event_debtor_list(self):
        api_url = "http://127.0.0.1:8000/eventpayment/event_debtor_list"

        headers = {"Authorization": f"Bearer {self.token}"}

        params = {
            "organiser_name": self.organizer_name_entry.get().strip(),
            "start_date": self.start_date.get_date().strftime("%Y-%m-%d"),
            "end_date": self.end_date.get_date().strftime("%Y-%m-%d"),
        }

        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()

                debtors = data.get("debtors", [])
                total_current_debt = data.get("total_current_debt", 0)
                total_gross_debt = data.get("total_gross_debt", 0)

                self.tree.delete(*self.tree.get_children())

                if not debtors:
                    messagebox.showinfo("Info", "No debtors found.")
                    return

                for debtor in debtors:
                    self.tree.insert("", "end", values=(
                        debtor.get("event_id", ""),
                        debtor.get("organiser", ""),
                        debtor.get("title", ""),
                        debtor.get("start_datetime", ""),
                        debtor.get("end_datetime", ""),
                        f"{float(debtor.get('event_amount', 0)) :,.2f}",
                        f"{float(debtor.get('caution_fee', 0)) :,.2f}",
                        f"{float(debtor.get('total_paid', 0)) :,.2f}",
                        f"{float(debtor.get('balance_due', 0)) :,.2f}",
                        debtor.get("location", ""),
                        debtor.get("phone_number", ""),
                        debtor.get("address", ""),
                        debtor.get("created_at", ""),
                        debtor.get("last_payment_date", ""),
                    ))
                    self.apply_grid_effect(self.tree)

                self.total_current_label.config(text=f"Total Current Debt: {total_current_debt:,.2f}")
                self.total_gross_label.config(text=f"Total Gross Debt: {total_gross_debt:,.2f}")

            else:
                messagebox.showinfo("No Results", "No Debtor found for the selected filters.")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching debtor list: {str(e)}")





    def list_payment_by_status(self):
        """Displays the List Payments by Status UI."""
        self.clear_right_frame()  # Ensure old UI elements are removed

        # Create a new frame for the table with scrollable functionality
        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Payments by Status", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        # Status Dropdown
        tk.Label(filter_frame, text="Status:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)

        status_options = ["pending", "complete", "incomplete", "voided"]
        self.status_var = tk.StringVar(value=status_options[0])  # Default selection

        status_menu = ttk.Combobox(filter_frame, textvariable=self.status_var, values=status_options, state="readonly")
        status_menu.grid(row=0, column=1, padx=5, pady=5)
        #status_menu.bind("<<ComboboxSelected>>", lambda event: self.status_var.set(status_menu.get()))
        
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
        fetch_btn = ttk.Button(filter_frame, text="Fetch Payments", command=self.fetch_payments_by_status)
        fetch_btn.grid(row=0, column=6, padx=10, pady=5)

        

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Total Payment Amount Label
        self.total_cost_label = tk.Label(frame, text="Total Payment Amount: 0.00", 
                                 font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_cost_label.pack(pady=5)

        

        columns = ("Payment ID", "Event ID", "Organiser Name", "Event Amount", "Amount Paid", "Discount Allowed", "Balance Due", "Payment Date", "Status", "Payment Method", "Created By")
        
        if hasattr(self, "tree"):
            self.tree.destroy()

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)


    def fetch_payments_by_status(self):
        """Fetch payments based on status and date filters."""
        api_url = "http://127.0.0.1:8000/eventpayment/status"

        # Ensure only valid query parameters are sent
        params = {
            "status": self.status_var.get().strip().lower(),
            "start_date": self.start_date.get_date().strftime("%Y-%m-%d"),
            "end_date": self.end_date.get_date().strftime("%Y-%m-%d"),
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)
            data = response.json()

            if response.status_code == 200:
                self.tree.delete(*self.tree.get_children())  # Clear existing table data
                total_amount = 0

                if isinstance(data, list):  # Ensure response is a list
                    for payment in data:
                        # Extract values safely
                        event_amount = float(payment.get("event_amount", 0))
                        amount_paid = float(payment.get("amount_paid", 0))  # <-- Update to amount_paid
                        discount_allowed = float(payment.get("discount_allowed", 0))
                        balance_due = float(payment.get("balance_due", 0))

                        total_amount += amount_paid  # Sum total amount paid

                        # Insert data into table
                        self.tree.insert("", "end", values=(
                            payment.get("id", ""),
                            payment.get("event_id", ""),
                            payment.get("organiser", ""),
                            f"{event_amount:,.2f}",
                            f"{amount_paid:,.2f}",
                            f"{discount_allowed:,.2f}",
                            f"{balance_due:,.2f}",
                            payment.get("payment_date", ""),
                            payment.get("payment_status", ""),
                            payment.get("payment_method", ""),
                            payment.get("created_by", ""),
                        ))

                    self.apply_grid_effect()

                    # Update Total Payment Label
                    self.total_cost_label.config(text=f"Total Payment Amount: {total_amount:,.2f}")
                else:
                    messagebox.showinfo("No Results", "No payments found for the selected filters.")
            else:
                messagebox.showerror("Error", data.get("detail", "Failed to retrieve payments."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
            

          
            


    def search_payment_by_id(self):
        """GUI for searching a payment by ID."""
        self.clear_right_frame()

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Search Payment by ID", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Search Input Frame
        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Payment ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.payment_id_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.payment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        search_btn = ttk.Button(
            search_frame, text="Search", command=self.fetch_payment_by_id
        )
        search_btn.grid(row=0, column=2, padx=10, pady=5)

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = (
            "ID", "Event ID", "Organiser", "Event Amount", "Amount Paid", 
            "Discount Allowed", "Balance Due", "Payment Method", "Status", 
            "Payment Date", "Created By"
        )

        if hasattr(self, "tree"):
            self.tree.destroy()

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)


    def fetch_payment_by_id(self):
        """Fetch and display payment details by ID."""
        payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            api_url = f"http://127.0.0.1:8000/eventpayment/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                payment = response.json()

                if payment:
                    self.tree.delete(*self.tree.get_children())

                    # Format amounts
                    event_amount = f"{float(payment.get('event_amount', 0)) :,.2f}"
                    amount_paid = f"{float(payment.get('amount_paid', 0)) :,.2f}"
                    discount_allowed = f"{float(payment.get('discount_allowed', 0)) :,.2f}"
                    balance_due = f"{float(payment.get('balance_due', 0)) :,.2f}"

                    self.tree.insert("", "end", values=(
                        payment.get("id", ""),
                        payment.get("event_id", ""),
                        payment.get("organiser", ""),
                        event_amount,
                        amount_paid,
                        discount_allowed,
                        balance_due,
                        payment.get("payment_method", ""),
                        payment.get("payment_status", ""),
                        payment.get("payment_date", ""),
                        payment.get("created_by", ""),
                    ))

                    self.apply_grid_effect(self.tree)
                else:
                    messagebox.showinfo("No Results", "No payment found with the provided ID.")
            else:
                messagebox.showerror("Error", response.json().get("detail", "No payment found."))
        
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
            






    def void_payment(self):
        self.clear_right_frame()

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Void Event Payment", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        input_frame = tk.Frame(frame, bg="#ffffff")
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Payment ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.payment_id_entry = tk.Entry(input_frame, font=("Arial", 11))
        self.payment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        void_btn = ttk.Button(input_frame, text="Void Payment", command=self.process_void_event_payment)
        void_btn.grid(row=0, column=2, padx=10, pady=5)

        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Payment ID", "Organiser", "Amount Paid", "Discount Allowed", "Balance Due", "Payment Status", "Created By")

        self.void_payment_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.void_payment_tree.heading(col, text=col)
            self.void_payment_tree.column(col, width=80, anchor="center")

        self.void_payment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.void_payment_tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.void_payment_tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.void_payment_tree.xview)
        x_scroll.pack(fill=tk.X)
        self.void_payment_tree.configure(xscroll=x_scroll.set)

    def process_void_event_payment(self):
        payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            check_url = f"http://127.0.0.1:8000/eventpayment/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(check_url, headers=headers)

            if response.status_code == 200:
                payment_data = response.json()
                payment_status = payment_data.get("payment_status", "").lower()

                if payment_status == "voided":
                    messagebox.showerror("Error", f"Payment ID {payment_id} has already been voided.")
                    return
                
                void_url = f"http://127.0.0.1:8000/eventpayment/void/{payment_id}/"
                void_response = requests.put(void_url, headers=headers)

                if void_response.status_code == 200:
                    data = void_response.json()
                    messagebox.showinfo("Success", data.get("message", "Payment voided successfully."))
                    self.fetch_voided_event_payment_by_id(payment_id)
                else:
                    messagebox.showerror("Error", void_response.json().get("detail", "Failed to void payment."))
            else:
                messagebox.showerror("Error", response.json().get("detail", "Payment record not found."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

    def fetch_voided_event_payment_by_id(self, payment_id=None):
        if payment_id is None:
            payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            api_url = f"http://127.0.0.1:8000/eventpayment/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if data:
                    if hasattr(self, "void_payment_tree") and self.void_payment_tree is not None:
                        self.void_payment_tree.delete(*self.void_payment_tree.get_children())

                    self.void_payment_tree.insert("", "end", values=(
                        data.get("id", ""),
                        data.get("organiser", ""),
                        f"{float(data.get('amount_paid', 0)) :,.2f}",
                        f"{float(data.get('discount_allowed', 0)) :,.2f}",
                        f"{float(data.get('balance_due', 0)) :,.2f}",
                        data.get("payment_status", ""),
                        data.get("created_by", ""),
                    ))
                else:
                    messagebox.showinfo("No Results", "No payment found with the provided ID.")
            else:
                messagebox.showerror("Error", response.json().get("detail", "No payment found."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")

    
    



# Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    app = EventManagement(root)
    root.mainloop()    