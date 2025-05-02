import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests
from utils import BASE_URL
from datetime import datetime
import pytz
from tkinter import ttk, Tk
import tkinter as tk
import customtkinter as ctk
import os
import pandas as pd
from CTkMessagebox import CTkMessagebox

from tkinter import Tk, Button, messagebox
from utils import export_to_excel, print_excel
import requests
#from bookings_gui import BookingManagement  # Import the Payment GUI

import pytz
from datetime import datetime

# Set Africa/Lagos as default timezone in your Python application
os.environ["TZ"] = "Africa/Lagos"

# Convert UTC to Africa/Lagos
lagos_tz = pytz.timezone("Africa/Lagos")
current_time = datetime.now(lagos_tz)

#print("Africa/Lagos Time:", current_time)


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
        self.width = 120  # Smaller width
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



class PaymentManagement:
    def __init__(self, root, token):
        self.root = tk.Toplevel(root)
        self.root.title("Payment Management")
        self.current_view = None  # or "", default nothing
        self.username = "current_user"
        self.root.state("zoomed")
        self.root.configure(bg="#f0f0f0")
        
        self.token = token
        self.payments_data = []
        self.last_exported_file = None




    # Set application icon
        icon_path = os.path.abspath("frontend/icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)



        # Set window size and position
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
            text="                                                                                               💳Payment Management",
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

        # Payment Action Buttons
        buttons = [
            ("Create Payment", self.create_payment),
            ("List Payment", self.list_payments),
            ("Sort By ID", self.search_payment_by_id),
            ("Sort By Status", self.list_payments_by_status),
            ("Daily Payment", self.list_total_daily_payments),
            ("Debtor List", self.debtor_list),
            ("Void Payment", self.void_payment),
        ]

        for text, command in buttons:
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

    def update_subheading(self, text, command):
        self.subheading_label.config(text=text)
        command()




    
    def apply_grid_effect(self, tree=None):
        if tree is None:
            tree = self.tree  # Default to main tree if none is provided
        
        for i, item in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(item, tags=("evenrow",))
            else:
                tree.item(item, tags=("oddrow",))

        tree.tag_configure("evenrow", background="#d9d9d9")  # medium gray
        #tree.tag_configure("oddrow", background="#f0f0f0")   # light gray
        tree.tag_configure("oddrow", background="white")      # White



    def open_dashboard_window(self):
        from dashboard import Dashboard
        Dashboard(self.root, self.token, self.username)

        self.root.destroy()
    



    def update_subheading(self, text, command):
        self.subheading_label.config(text=text)
        command()


    


    def fetch_and_display_paymentss(self):
        """Fetch booking data from the API"""
        url = "http://127.0.0.1:8000/payments/list"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.payments_data = response.json()
            else:
                self.payments_data = []
                messagebox.showerror("Error", "Failed to fetch payments.")

        except Exception as e:
            self.payments_data = []
            messagebox.showerror("Error", f"API Error: {str(e)}")

    

    

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
            "payments": ("payments_report.xlsx", "Hotel Payment Report"),
            "debtors": ("debtors_report.xlsx", "Hotel Debtor Report"),
            "daily_payments": ("daily_payments_report.xlsx", "Hotel Daily Payment Report")
        }

        mapped = file_name_map.get(self.current_view)
        if not mapped:
            messagebox.showerror("Error", "Unknown view selected.")
            return

        file_name, report_title = mapped
        file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)

        try:
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                sheet_name = self.current_view.replace("_", " ").title()
                df.to_excel(writer, sheet_name=sheet_name, startrow=5, index=False)

                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                worksheet.set_landscape()

                # === Styles ===
                title_format = workbook.add_format({
                    'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 16
                })
                timestamp_format = workbook.add_format({'italic': True, 'font_size': 10})
                header_format = workbook.add_format({
                    'bold': True, 'bg_color': '#DDEBF7', 'border': 1,
                    'align': 'center', 'valign': 'vcenter'
                })
                cell_format = workbook.add_format({'border': 1, 'valign': 'top'})

                # === Merge Title ===
                worksheet.merge_range('A1:E1', report_title, title_format)
                worksheet.write('A3', f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_format)

                
                # Header styling
                for col_num, col_name in enumerate(columns):
                    worksheet.write(5, col_num, col_name, header_format)

                # Data cell styling
                for row_num in range(len(rows)):
                    for col_num in range(len(columns)):
                        worksheet.write(row_num + 6, col_num, rows[row_num][col_num], cell_format)

                # Auto-fit columns
                for i, col in enumerate(columns):
                    col_width = max(len(str(col)), max(len(str(row[i])) for row in rows if row[i] is not None))
                    worksheet.set_column(i, i, col_width + 2)

                # === Summary Section ===
                start_row = len(df) + 8
                col_span = len(columns)
                end_col_letter = chr(64 + col_span) if col_span <= 26 else 'Z'
                summary_range = f"A{start_row+1}:{end_col_letter}{start_row+1}"

                worksheet.merge_range(summary_range, "Summary", header_format)

                def extract_amount(label_widget):
                    if label_widget is None:
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

                if self.current_view == "payments":
                    write_summary_row(2, "Cash", getattr(self, "total_cash_label", None))
                    write_summary_row(3, "POS Card", getattr(self, "total_pos_label", None))
                    write_summary_row(4, "Bank Transfer", getattr(self, "total_bank_label", None))
                    write_summary_row(5, "Total Amount", getattr(self, "total_label", None))

                elif self.current_view == "debtors":
                    write_summary_row(2, "Current Debt", getattr(self, "total_current_label", None))
                    write_summary_row(3, "Gross Debt", getattr(self, "total_gross_label", None))

                elif self.current_view == "daily_payments":
                    write_summary_row(2, "Cash", getattr(self, "cash_label", None))
                    write_summary_row(3, "POS Card", getattr(self, "pos_card_label", None))
                    write_summary_row(4, "Bank Transfer", getattr(self, "bank_transfer_label", None))
                    write_summary_row(5, "Total Amount", getattr(self, "total_label", None))

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

        
    
    def create_payment(self):
        """Opens a modern CTk pop-up window for creating a new payment."""
        create_window = ctk.CTkToplevel(self.root)
        create_window.title("Create Payment")
        create_window.geometry("500x400")
        create_window.resizable(False, False)

        # Set the background color for the window
        create_window.configure(bg="black")

        # Center the window
        window_width = 500
        window_height = 320
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        # Apply geometry
        create_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Make it modal
        create_window.transient(self.root)
        create_window.grab_set()

        # 🔹 Header
        header_label = ctk.CTkLabel(create_window, text="Create Payment", font=("Arial", 16, "bold"), text_color="black")
        header_label.pack(pady=10)

        # 🔹 Form Frame
        form_frame = ctk.CTkFrame(create_window, corner_radius=10, fg_color="gray25")  # Dark background for the frame
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 📌 Payment Fields
        fields = [
            ("Booking ID", ctk.CTkEntry),
            ("Amount Paid", ctk.CTkEntry),
            ("Discount Allowed", ctk.CTkEntry),
            ("Payment Method", ctk.CTkComboBox),
            ("Payment Date", DateEntry),
        ]

        self.entries = {}

        for i, (label, field_type) in enumerate(fields):
            lbl = ctk.CTkLabel(form_frame, text=label, font=("Arial", 12), text_color="white")
            lbl.grid(row=i, column=0, sticky="w", padx=10, pady=5)

            if field_type == ctk.CTkComboBox:
                entry = field_type(form_frame, values=["Cash", "POS Card", "Bank Transfer"], state="readonly", width=200)
            elif field_type == DateEntry:
                entry = field_type(form_frame, width=15, background='darkblue', foreground='white', borderwidth=2)
            else:
                entry = field_type(form_frame, width=200, fg_color="gray20", text_color="white")

            entry.grid(row=i, column=1, pady=5, padx=15, sticky="ew")
            self.entries[label] = entry  # ✅ Store entry reference

        # 🔹 Submit Button
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.grid(row=len(fields), column=1, columnspan=2, pady=15)

        submit_btn = ctk.CTkButton(btn_frame, text="Submit Payment", width=200, command=lambda: self.submit_payment(create_window), fg_color="gray40", hover_color="gray30")
        submit_btn.pack(pady=5)



    
    
    def submit_payment(self, create_window):
        """Handles payment submission to the backend and closes the pop-up window only on success."""
        try:
            errors = []  # Collect all validation errors

            # ✅ Validate Booking ID
            booking_id_str = self.entries["Booking ID"].get().strip()
            if not booking_id_str.isdigit():
                errors.append("Booking ID must be a valid integer.")

            # ✅ Validate Amount Paid
            amount_paid_str = self.entries["Amount Paid"].get().strip()
            if not amount_paid_str.replace(".", "", 1).isdigit():
                errors.append("Amount Paid must be a valid number.")

            # ✅ Validate Discount Allowed (Optional)
            discount_allowed_str = self.entries["Discount Allowed"].get().strip()
            discount_allowed = float(discount_allowed_str) if discount_allowed_str.replace(".", "", 1).isdigit() else 0.0

            # ✅ Validate Payment Method
            payment_method = self.entries["Payment Method"].get().strip()
            if not payment_method:
                errors.append("Payment Method is required.")

            # ✅ Define Africa/Lagos timezone
            lagos_tz = pytz.timezone("Africa/Lagos")

            # ✅ Validate Payment Date
            try:
                payment_date = self.entries["Payment Date"].get_date()

                # Set time to midnight to avoid time drift issues
                # Define Africa/Lagos timezone
                lagos_tz = pytz.timezone("Africa/Lagos")

                # ✅ Get date from the entry and ensure it has the correct time
                payment_date = self.entries["Payment Date"].get_date()

                # ✅ Use the current time in Lagos timezone to set the full timestamp
                current_time_lagos = datetime.now(lagos_tz)

                

                # ✅ Create payment_date with current time instead of midnight (prevents time drift)
                payment_date = datetime(
                    payment_date.year, payment_date.month, payment_date.day, 
                    current_time_lagos.hour, current_time_lagos.minute, current_time_lagos.second
                )

                # ✅ Convert to Africa/Lagos timezone
                payment_date = lagos_tz.localize(payment_date)

                # ✅ Format to ISO 8601 (PostgreSQL compatible)
                payment_date_iso = payment_date.isoformat()

            except Exception:
                errors.append("Invalid Payment Date. Please select a valid date.")

            # ❌ If there are errors, show all in a single messagebox and stop execution
            if errors:
                create_window.grab_release()  # Release grab before showing messagebox
                CTkMessagebox(title="Error", message="\n".join(errors), icon="cancel")
                return  # Stop execution

            # ✅ Convert Booking ID and Amount Paid (since we passed validation)
            booking_id = int(booking_id_str)
            amount_paid = float(amount_paid_str)

            # ✅ Prepare Data
            payload = {
                "amount_paid": amount_paid,
                "discount_allowed": discount_allowed,
                "payment_method": payment_method,
                "payment_date": payment_date_iso,
            }

            # ✅ Send Request
            url = f"http://127.0.0.1:8000/payments/{booking_id}"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            if response.status_code == 200:
                payment_details = data.get("payment_details")
                if payment_details:
                    payment_id = payment_details.get("payment_id")
                    created_by = payment_details.get("created_by")

                    # ✅ Close the pop-up window on success
                    create_window.destroy()

                    # ✅ Show success message with delay
                    self.root.after(100, lambda: CTkMessagebox(
                        title="Success",
                        message=f"Payment created successfully!\nPayment ID: {payment_id}\nCreated By: {created_by}",
                        icon="check"
                    ))
                else:
                    create_window.grab_release()
                    CTkMessagebox(title="Error", message="Payment ID missing in response.", icon="cancel")

            else:
                create_window.grab_release()
                CTkMessagebox(title="Error", message=data.get("detail", "Payment failed."), icon="cancel")

        except Exception as e:
            create_window.grab_release()
            CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")



    def list_payments(self):
        self.clear_right_frame()
        self.current_view = "payments"


        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Payments Report", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        fetch_btn = ttk.Button(filter_frame, text="Fetch Payments", command=self.fetch_payments)
        fetch_btn.grid(row=0, column=4, padx=10, pady=5)

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Payment ID", "Guest Name", "Room Number", "Booking Cost", "Amount Paid", "Discount Allowed",
                "Balance Due", "Payment Method", "Payment Date", "Status", "Void Date", "Booking ID", "Created_by")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=80, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        
        # Payment Breakdown Frame (Closer to Summary Frame)
        breakdown_frame = tk.Frame(frame, bg="#ffffff", padx=5, pady=5)  # Reduced padding
        breakdown_frame.pack(fill=tk.X, pady=5)  # Reduced vertical spacing

        self.total_cash_label = tk.Label(breakdown_frame, text="Total Cash: 0", font=("Arial", 12), bg="#ffffff", fg="red")
        self.total_cash_label.grid(row=0, column=0, padx=10)  # Reduced horizontal spacing

        self.total_pos_label = tk.Label(breakdown_frame, text="Total POS Card: 0", font=("Arial", 12), bg="#ffffff", fg="blue")
        self.total_pos_label.grid(row=0, column=1, padx=10)

        self.total_bank_label = tk.Label(breakdown_frame, text="Total Bank Transfer: 0", font=("Arial", 12), bg="#ffffff", fg="purple")
        self.total_bank_label.grid(row=0, column=2, padx=10)

        self.total_label = tk.Label(breakdown_frame, text="Total Amount: 0", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_label.grid(row=0, column=3, padx=10)


    def fetch_payments(self):
        api_url = "http://127.0.0.1:8000/payments/list"
        params = {
            "start_date": self.start_date.get_date().strftime("%Y-%m-%d"),
            "end_date": self.end_date.get_date().strftime("%Y-%m-%d"),
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", {})
                payments = data.get("payments", []) if isinstance(data, dict) else data

                self.tree.delete(*self.tree.get_children())  # Clear the table

                
                total_cash = 0
                total_pos = 0
                total_bank = 0

                for payment in payments:
                    status = payment.get("status", "").lower()
                    booking_cost = float(payment.get("booking_cost", 0))
                    amount_paid = float(payment.get("amount_paid", 0))
                    discount = float(payment.get("discount_allowed", 0))
                    method = payment.get("payment_method", "").lower()

                    # Exclude voided payments from payment breakdown
                    if status != "voided":
                        if method == "cash":
                            total_cash += amount_paid
                        elif method == "pos card":
                            total_pos += amount_paid
                        elif method == "bank transfer":
                            total_bank += amount_paid

                    # Insert payment into table (lists all payments, including voided ones)
                    self.tree.insert("", "end", values=(
                        payment.get("payment_id", ""),
                        payment.get("guest_name", ""),
                        payment.get("room_number", ""),
                        f"{booking_cost:,.2f}",  # Display booking cost
                        f"{amount_paid:,.2f}",
                        f"{discount:,.2f}",
                        f"{booking_cost - (amount_paid + discount):,.2f}",  # Correct Amount Due
                        payment.get("payment_method", ""),
                        payment.get("payment_date", ""),
                        payment.get("status", ""),
                        payment.get("void_date", ""),
                        payment.get("booking_id", ""),
                        payment.get("created_by", "N/A"),
                    ))

                # Apply the effect to the correct treeview (payment_tree)
                    self.apply_grid_effect(self.tree)
                    
                # Update breakdown labels
                self.total_cash_label.config(text=f"Total Cash: {total_cash:,.2f}")
                self.total_pos_label.config(text=f"Total POS Card: {total_pos:,.2f}")
                self.total_bank_label.config(text=f"Total Bank Transfer: {total_bank:,.2f}")
                self.total_label.config(text=f"Total Amount: {total_cash + total_pos + total_bank:,.2f}")

            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve payments."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")








    def list_payments_by_status(self):
        """Displays the List Payments by Status UI."""
        self.clear_right_frame()

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="List Payments by Status", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)
        
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)
        
        # Payment Status Dropdown
        tk.Label(filter_frame, text="Status:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)

        payment_status_options = ["payment completed", "payment incomplete", "voided"]
        self.payment_status_var = tk.StringVar(value=payment_status_options[0])  # Default selection

        status_menu = ttk.Combobox(filter_frame, textvariable=self.payment_status_var, values=payment_status_options, state="readonly")
        status_menu.grid(row=0, column=1, padx=5, pady=5)

        # Bind the selection event to update self.payment_status_var
        def on_payment_status_change(event):
            #print("Selected Payment Status:", self.payment_status_var.get())  # Debugging: Check what is selected
            self.payment_status_var.set(status_menu.get())  # Ensure value updates

        status_menu.bind("<<ComboboxSelected>>", on_payment_status_change)  # Event binding

        
        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.payment_start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.payment_start_date.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
        self.payment_end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.payment_end_date.grid(row=0, column=5, padx=5, pady=5)
        
        fetch_btn = ttk.Button(filter_frame, text="Fetch Payments", command=self.fetch_payments_by_status)
        fetch_btn.grid(row=0, column=6, padx=10, pady=5)
        
        
        
        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        

        
        columns = ("ID", "Guest Name", "Room Number", "Amount Paid", "Discount", "Balance Due", "Payment Method", "Payment Date", "Status", "Void Date", "Booking ID", "Created_by")
        
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


        api_url = "http://127.0.0.1:8000/payments/by-status"

        selected_status = self.payment_status_var.get().lower()  # Ensure it's lowercase if required by the backend
        start_date = self.payment_start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.payment_end_date.get_date().strftime("%Y-%m-%d")

        params = {
            "status": selected_status,
            "start_date": start_date,
            "end_date": end_date,
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        # Debugging: Print the API request details
        #print("Fetching payments with parameters:", params)

        try:
            response = requests.get(api_url, params=params, headers=headers)
            #print("API Response Status:", response.status_code)  # Debugging

            if response.status_code == 200:
                data = response.json()
                #print("API Response Data:", data)  # Debugging

                if "payments" in data and data["payments"]:
                    self.tree.delete(*self.tree.get_children())  # Clear previous data
                    #self.tree.delete(*self.tree.get_children())
                    
                    total_payment = 0  # Initialize total sum

                    for payment in data["payments"]:
                        is_voided = payment.get("status", "").lower() == "voided"
                        tag = "voided" if is_voided else "normal"

                        amount_paid = float(payment.get("amount_paid", 0))
                        total_payment += amount_paid

                        self.tree.insert("", "end", values=(
                            payment.get("payment_id", ""),
                            payment.get("guest_name", ""),
                            payment.get("room_number", ""),
                            f"{amount_paid:,.2f}",
                            f"{float(payment.get('discount_allowed', 0)):,.2f}",
                            f"{float(payment.get('balance_due', 0)):,.2f}",
                            payment.get("payment_method", ""),
                            payment.get("payment_date", ""),
                            payment.get("status", ""),
                            payment.get("void_date", ""),
                            payment.get("booking_id", ""),
                            payment.get("created_by", ""),
                        ), tags=(tag,))

                    
                    # Apply the effect to the correct treeview (payment_tree)
                    self.apply_grid_effect(self.tree)
                    


                    self.tree.tag_configure("voided", foreground="red")
                    self.tree.tag_configure("normal", foreground="black")

                    # Display total payment sum below the table
                    if hasattr(self, "total_payment_label"):
                        self.total_payment_label.destroy()

                    self.total_payment_label = tk.Label(
                        self.right_frame,
                        text=f"Total Payment: {total_payment:,.2f}",
                        font=("Arial", 12, "bold"),
                        bg="#ffffff", fg="blue"
                    )
                    self.total_payment_label.pack(pady=10)

                    
                    

                else:
                    messagebox.showinfo("No Results", "No payments found for the selected filters.")
            else:
                error_message = response.json().get("detail", "Failed to retrieve payments.")
                messagebox.showerror("Error", f"API Error: {error_message}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")



        
   
    def debtor_list(self):
        self.clear_right_frame()
        self.current_view = "debtors"


        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Debtor List", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(frame, bg="#ffffff")
        filter_frame.pack(pady=5)

        # Debtor Name Search
        tk.Label(filter_frame, text="Debtor Name:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.debtor_name_entry = tk.Entry(filter_frame, font=("Arial", 11))
        self.debtor_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Date Filters
        tk.Label(filter_frame, text="Start Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, font=("Arial", 11))
        self.start_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="End Date:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, font=("Arial", 11))
        self.end_date.set_date(datetime.today())
        self.end_date.grid(row=0, column=5, padx=5, pady=5)

        fetch_btn = ttk.Button(filter_frame, text="Fetch Debtor List", command=self.fetch_debtor_list)
        fetch_btn.grid(row=0, column=6, padx=10, pady=5)

        # Table Frame
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = (
            "Booking ID", "Guest Name", "Room Number", "Room Price", "Number of Days",
            "Total Amount", "Total Paid", "Amount Due", "Booking Date", "Last Payment Date"
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=y_scroll.set)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill=tk.X)
        self.tree.configure(xscroll=x_scroll.set)

        # Total Debt Display
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


    def fetch_debtor_list(self):
        api_url = "http://127.0.0.1:8000/payments/debtor_list"
        headers = {"Authorization": f"Bearer {self.token}"}

        params = {
            "debtor_name": self.debtor_name_entry.get().strip(),  # Get debtor name from input
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
                        debtor.get("booking_id", ""),
                        debtor.get("guest_name", ""),
                        debtor.get("room_number", ""),
                        f"{float(debtor.get('room_price', 0)) :,.2f}",
                        debtor.get("number_of_days", ""),
                        f"{float(debtor.get('total_due', 0)) :,.2f}",
                        f"{float(debtor.get('total_paid', 0)) :,.2f}",
                        f"{float(debtor.get('amount_due', 0)) :,.2f}",
                        debtor.get("booking_date", ""),
                        debtor.get("last_payment_date", ""),
                    ))
                # Apply the effect to the correct treeview (payment_tree)
                    self.apply_grid_effect(self.tree)



                self.total_current_label.config(text=f"Total Current Debt: {total_current_debt:,.2f}")
                self.total_gross_label.config(text=f"Total Gross Debt: {total_gross_debt:,.2f}")



            else:
                messagebox.showerror("Error", f"Failed to fetch debtor list: {response.json().get('detail', 'Unknown error')}")

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching debtor list: {str(e)}")




    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()   
            
            
            

    def list_total_daily_payments(self):
        self.clear_right_frame()
        self.current_view = "daily_payments"

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Total Daily Payments", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        fetch_btn = ttk.Button(
            frame,
            text="Fetch Today's Payments",
            command=self.fetch_total_daily_payments
        )
        fetch_btn.pack(pady=5)

        # Table for payments
        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Guest Name", "Room Number", "Amount Paid", "Discount Allowed", "Balance Due",
                "Payment Method", "Payment Date", "Status", "Booking ID")

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

        # Frame for horizontal display of totals
        totals_frame = tk.Frame(frame, bg="#ffffff")
        totals_frame.pack(fill=tk.X, pady=5)

        self.pos_card_label = tk.Label(totals_frame, text="Total POS Card: 0", font=("Arial", 12), bg="#ffffff", fg="green")
        self.pos_card_label.pack(side=tk.LEFT, padx=20)

        self.bank_transfer_label = tk.Label(totals_frame, text="Total Bank Transfer: 0", font=("Arial", 12), bg="#ffffff", fg="purple")
        self.bank_transfer_label.pack(side=tk.LEFT, padx=20)

        self.cash_label = tk.Label(totals_frame, text="Total Cash: 0", font=("Arial", 12), bg="#ffffff", fg="red")
        self.cash_label.pack(side=tk.LEFT, padx=20)

        # Total Amount Label (Centered Below the Frame)
        self.total_label = tk.Label(frame, text="Total Amount: 0", font=("Arial", 12, "bold"), bg="#ffffff", fg="blue")
        self.total_label.pack(pady=5)

    def fetch_total_daily_payments(self):
        api_url = "http://127.0.0.1:8000/payments/total_daily_payment"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                total_amount = data.get("total_amount", 0)
                total_by_method = data.get("total_by_method", {"POS Card": 0, "Bank Transfer": 0, "Cash": 0})

                # Update labels with total payment breakdown
                self.total_label.config(text=f"Total Amount: {total_amount:,.2f}")
                self.pos_card_label.config(text=f"Total POS Card: {total_by_method.get('POS Card', 0):,.2f}")
                self.bank_transfer_label.config(text=f"Total Bank Transfer: {total_by_method.get('Bank Transfer', 0):,.2f}")
                self.cash_label.config(text=f"Total Cash: {total_by_method.get('Cash', 0):,.2f}")

                
                

                if "payments" in data:
                    payments = data["payments"]
                else:
                    payments = []

                self.tree.delete(*self.tree.get_children())

                for payment in payments:
                    self.tree.insert("", "end", values=(
                        payment.get("payment_id", ""),
                        payment.get("guest_name", ""),
                        payment.get("room_number", ""),
                        f"{float(payment.get('amount_paid', 0)) :,.2f}",
                        f"{float(payment.get('discount_allowed', 0)) :,.2f}",
                        f"{float(payment.get('balance_due', 0)) :,.2f}",
                        payment.get("payment_method", ""),
                        payment.get("payment_date", ""),
                        payment.get("status", ""),
                        payment.get("booking_id", ""),
                    ))

                self.apply_grid_effect(self.tree)
            else:
                messagebox.showerror("Error", response.json().get("detail", "Failed to retrieve payments."))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")



    def search_payment_by_id(self):
        self.clear_right_frame()

        frame = tk.Frame(self.right_frame, bg="#ffffff", padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Search Payment by ID", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        search_frame = tk.Frame(frame, bg="#ffffff")
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Payment ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.payment_id_entry = tk.Entry(search_frame, font=("Arial", 11))
        self.payment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        search_btn = ttk.Button(
            search_frame, text="Search", command=self.fetch_payment_by_id
        )
        search_btn.grid(row=0, column=2, padx=10, pady=5)

        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Guest Name", "Room Number", "Amount Paid", "Discount Allowed", "Balance Due", 
                "Payment Method", "Payment Date", "Status", "Void Date", "Booking ID", "Created_by")
        

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
        payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():  # Ensure input is numeric
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            api_url = f"http://127.0.0.1:8000/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if data:  # Ensure data exists
                    # ✅ Check if the TreeView exists before modifying it
                    if hasattr(self, "tree") and self.tree is not None:
                        self.tree.delete(*self.tree.get_children())

                        # ✅ Extract payment details from the response
                        payment_id = data.get("payment_id", "")
                        guest_name = data.get("guest_name", "")
                        room_number = data.get("room_number", "")
                        amount_paid = f"{float(data.get('amount_paid', 0)) :,.2f}"  # Format amount
                        discount_allowed = f"{float(data.get('discount_allowed', 0)) :,.2f}"  # Format discount
                        balance_due = f"{float(data.get('balance_due', 0)) :,.2f}"  # Format balance
                        payment_method = data.get("payment_method", "")
                        payment_date = data.get("payment_date", "")
                        status = data.get("status", "").lower()  # Normalize status
                        void_date = data.get("void_date", "N/A")  # ✅ Ensure void_date is captured
                        booking_id = data.get("booking_id", "")
                        created_by = data.get("created_by", "")

                        

                        # ✅ Define tag for voided payments
                        tag = "voided" if status == "voided" else "normal"

                        # ✅ Insert data into TreeView
                        self.tree.insert("", "end", values=(
                            payment_id, guest_name, room_number, amount_paid, 
                            discount_allowed, balance_due, payment_method, 
                            payment_date, status, void_date, booking_id, created_by,
                        ), tags=(tag,))


                        # ✅ Apply color formatting
                        self.tree.tag_configure("voided", foreground="red")
                        self.tree.tag_configure("normal", foreground="black")

                        self.apply_grid_effect(self.tree)

                    else:
                        messagebox.showerror("Error", "Payment list is not initialized.")

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

        tk.Label(frame, text="Void Payment", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        input_frame = tk.Frame(frame, bg="#ffffff")
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Payment ID:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.payment_id_entry = tk.Entry(input_frame, font=("Arial", 11))
        self.payment_id_entry.grid(row=0, column=1, padx=5, pady=5)

        void_btn = ttk.Button(
            input_frame, text="Void Payment", command=self.process_void_payment
        )
        void_btn.grid(row=0, column=2, padx=10, pady=5)

        table_frame = tk.Frame(frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Payment ID", "Guest Name", "Room Number", "Amount Paid", "Discount Allowed",
                "Balance Due", "Payment Method", "Payment Date", "Payment Status", "Void Date", "Booking ID", "Created_by")

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


    def process_void_payment(self):
        payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            # Fetch payment details first to check the status
            check_url = f"http://127.0.0.1:8000/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(check_url, headers=headers)

            if response.status_code == 200:
                payment_data = response.json()
                payment_status = payment_data.get("status", "").lower()  # Use "status" instead of "payment_status"

                if payment_status == "void":
                    messagebox.showerror("Error", f"This Payment ID {payment_id} has already been voided before.")
                    return  # Stop further execution
                
                # Proceed with voiding the payment if not already voided
                api_url = f"http://127.0.0.1:8000/payments/void/{payment_id}"
                void_response = requests.put(api_url, headers=headers)

                if void_response.status_code == 200:
                    data = void_response.json()
                    messagebox.showinfo("Success", data.get("message", "Payment has been voided."))
                    
                    # Fetch updated payment and booking data
                    self.fetch_voided_payment_by_id(payment_id)
                else:
                    messagebox.showerror("Error", void_response.json().get("detail", "Failed to void payment."))
            else:
                messagebox.showerror("Error", response.json().get("detail", "Payment record not found."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")




    def fetch_voided_payment_by_id(self, payment_id=None):
        if payment_id is None:
            payment_id = self.payment_id_entry.get().strip()

        if not payment_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric payment ID.")
            return

        try:
            api_url = f"http://127.0.0.1:8000/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {self.token}"}

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if data:
                    if hasattr(self, "void_payment_tree") and self.tree is not None:
                        self.tree.delete(*self.tree.get_children())  

                    # Insert payment details with booking payment_status
                    self.tree.insert("", "end", values=(
                        data.get("payment_id", ""),
                        data.get("guest_name", ""),
                        data.get("room_number", ""),
                        f"{float(data.get('amount_paid', 0)) :,.2f}",
                        f"{float(data.get('discount_allowed', 0)) :,.2f}",
                        f"{float(data.get('balance_due', 0)) :,.2f}",
                        data.get("payment_method", ""),
                        data.get("payment_date", ""),
                        data.get("status", ""),  # Payment status (should be "voided")
                        data.get("void_date", ""),
                        data.get("booking_id", ""),
                        data.get("created_by", ""),
                    ))

                    self.apply_grid_effect(self.tree)
                else:
                    messagebox.showinfo("No Results", "No payment found with the provided ID.")
            else:
                messagebox.showerror("Error", response.json().get("detail", "No payment found."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
        
        

    