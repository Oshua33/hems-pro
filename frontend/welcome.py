import tkinter as tk
import random

class WelcomeWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Welcome")
        self.attributes('-fullscreen', True)  # Fullscreen mode
        self.configure(bg="black")  # Background color

        # Create canvas for animation
        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), 
                                bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create falling text with a stylish font
        self.text_id = self.canvas.create_text(
            self.winfo_screenwidth() // 2, 100,  
            text="Welcome to Hotel\nand\nEvent Management",  
            font=("Algerian", 50, "bold"),  # Stylish font
            fill="gold", justify="center"
        )

        # Create falling stars
        self.stars = []
        self.create_stars()

        # Start animations
        self.text_animation = None
        self.stars_animation = None
        self.animate_text()
        self.animate_stars()

        # Skip Button
        self.exit_button = tk.Button(self, text="Skip", command=self.close_welcome, 
                                     font=("Arial", 14, "bold"), bg="red", fg="white")
        self.exit_button.place(relx=0.9, rely=0.9, anchor="center")

        # Bind Escape key to exit
        self.bind("<Escape>", lambda event: self.close_welcome())

        # Auto-close after 10 seconds
        self.auto_close = self.after(10000, self.close_welcome)

    def create_stars(self):
        """Create multiple stars at random positions"""
        colors = ["yellow", "white", "gold", "lightblue", "lightgreen"]
        for _ in range(100):  # Increased number of stars
            x = random.randint(10, self.winfo_screenwidth() - 10)
            size = random.randint(3, 7)
            color = random.choice(colors)
            star = self.canvas.create_oval(x, 0, x + size, size, fill=color, outline="")
            self.stars.append((star, random.randint(2, 5)))  # Store star and speed

    def animate_text(self):
        """Move text downwards like falling effect"""
        x, y = self.canvas.coords(self.text_id)
        if y < self.winfo_screenheight() - 150:  # Adjusted stopping position
            self.canvas.move(self.text_id, 0, 3)
            self.text_animation = self.after(50, self.animate_text)

    def animate_stars(self):
        """Move stars downwards like a falling effect"""
        for star, speed in self.stars:
            x1, y1, x2, y2 = self.canvas.coords(star)
            if y2 < self.winfo_screenheight():
                self.canvas.move(star, 0, speed)
            else:
                # Respawn stars at random x position
                size = x2 - x1
                new_x = random.randint(10, self.winfo_screenwidth() - 10)
                self.canvas.coords(star, new_x, 0, new_x + size, size)

        self.stars_animation = self.after(20, self.animate_stars)

    def close_welcome(self):
        """Stops animations and closes window"""
        if self.text_animation:
            self.after_cancel(self.text_animation)
        if self.stars_animation:
            self.after_cancel(self.stars_animation)
        if self.auto_close:
            self.after_cancel(self.auto_close)
        self.destroy()

# Run the welcome window
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    welcome = WelcomeWindow(root)
    welcome.mainloop()
