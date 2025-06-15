import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import csv
import logging
import turtle

# --- Configuration ---
FEEDBACK_FILE = "super_metro_feedback.csv"
RESET_DELAY_MS = 3000 # 3 seconds total for the thank you + animation
EMOJI_DISPLAY_DURATION_MS = 1500 # Duration the emoji is visible before clearing

# *** NEW CONFIGURATION: Vehicle Number Plate ***
VEHICLE_NUMBER_PLATE = "KDE 569D" # Replace with actual number plate for each bus

# --- Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("feedback_app_log.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- GUI Setup ---
root = tk.Tk()
root.title("Super Metro Feedback")
root.geometry("800x480")
root.attributes('-fullscreen', True)

# Define colors
COLOR_PRIMARY_BG = "#30475E"
COLOR_ACCENT_1 = "#E5DDC8"
COLOR_ACCENT_2 = "#F05454"
COLOR_BUTTON_GOOD = "#4CAF50"
COLOR_BUTTON_NEUTRAL = "#FFC107"
COLOR_BUTTON_BAD = "#F44336"
COLOR_TEXT_LIGHT = "white"

root.config(bg=COLOR_PRIMARY_BG)

# --- Welcome/Instruction Label ---
welcome_label = tk.Label(
    root,
    text="Welcome to SuperMetro,\nHow was your ride?",
    font=("Arial", 36, "bold"),
    fg=COLOR_TEXT_LIGHT,
    bg=COLOR_PRIMARY_BG,
    pady=20
)
welcome_label.pack(pady=40)

# --- Feedback Options ---
feedback_options = [
    {"text": "Excellent! ⭐⭐⭐⭐⭐", "value": "Excellent", "color": COLOR_BUTTON_GOOD, "emoji": "😊"},
    {"text": "Good ⭐⭐⭐⭐", "value": "Good", "color": COLOR_BUTTON_GOOD, "emoji": "🙂"},
    {"text": "Neutral ⭐⭐⭐", "value": "Neutral", "color": COLOR_BUTTON_NEUTRAL, "emoji": "😐"},
    {"text": "Bad ⭐⭐", "value": "Bad", "color": COLOR_BUTTON_BAD, "emoji": "🙁"},
    {"text": "Terrible! ⭐", "value": "Terrible", "color": COLOR_BUTTON_BAD, "emoji": "😠"},
]

buttons = []

# --- Turtle Setup ---
turtle_canvas = tk.Canvas(root, width=800, height=250, bg=COLOR_PRIMARY_BG, highlightthickness=0)
turtle_canvas.pack(pady=10)

screen = turtle.TurtleScreen(turtle_canvas)
screen.bgcolor(COLOR_PRIMARY_BG)

feedback_pen = turtle.RawTurtle(screen)
feedback_pen.hideturtle()
feedback_pen.penup()
feedback_pen.speed(0)
screen.tracer(0)

# --- Functions ---

def animate_emoji_feedback(emoji_char, emoji_color):
    """
    Displays and animates an emoji using turtle graphics.
    """
    logger.info(f"Animating emoji: {emoji_char} with color {emoji_color}")
    feedback_pen.clear()
    feedback_pen.goto(0, -40) # Position to ensure full emoji display

    feedback_pen.color(emoji_color)
    feedback_pen.write(emoji_char, align="center", font=("Arial", 80, "bold"))
    screen.update()

    screen.ontimer(feedback_pen.clear, EMOJI_DISPLAY_DURATION_MS)
    screen.ontimer(screen.update, EMOJI_DISPLAY_DURATION_MS + 50)

    root.after(EMOJI_DISPLAY_DURATION_MS + 200, show_thank_you_screen)


def record_feedback(rating, emoji_char, emoji_color):
    """
    Records the feedback, logs it, and initiates the emoji animation.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # *** CHANGE 1: Include VEHICLE_NUMBER_PLATE in feedback_data ***
    feedback_data = [timestamp, VEHICLE_NUMBER_PLATE, rating]

    # Log to console and file, including the plate number
    logger.info(f"Feedback received from '{VEHICLE_NUMBER_PLATE}': '{rating}' at {timestamp}")

    for btn in buttons:
        btn.config(state=tk.DISABLED)

    # Append to CSV file
    try:
        with open(FEEDBACK_FILE, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(feedback_data)
        logger.info(f"Feedback successfully written to {FEEDBACK_FILE}")
    except IOError as e:
        logger.error(f"Failed to write feedback to CSV: {e}")
        messagebox.showerror("Error", "Could not save feedback. Please check file permissions.")
        for btn in buttons:
            btn.config(state=tk.NORMAL)
        return

    animate_emoji_feedback(emoji_char, emoji_color)


def show_thank_you_screen():
    """
    Shows a thank you message and schedules app reset.
    """
    welcome_label.config(text="Thank you for your feedback!", font=("Arial", 40, "bold"))
    
    root.after(RESET_DELAY_MS - EMOJI_DISPLAY_DURATION_MS, reset_app_state)
    logger.info(f"Thank you screen shown. Resetting in {RESET_DELAY_MS/1000} seconds.")

def reset_app_state():
    """
    Resets the app to its initial state, ready for new feedback.
    """
    welcome_label.config(text="Welcome to SuperMetro,\nHow was your ride?", font=("Arial", 36, "bold"))
    
    feedback_pen.clear()
    screen.update()

    for btn in buttons:
        btn.config(state=tk.NORMAL)
        btn.pack(fill=tk.X, pady=5)

    logger.info("App state reset. Ready for next feedback.")

# --- Create Buttons ---
for option in feedback_options:
    btn = tk.Button(
        root,
        text=option["text"],
        command=lambda val=option["value"], emoji=option["emoji"], color=option["color"]: record_feedback(val, emoji, color),
        font=("Arial", 20, "bold"),
        bg=option["color"],
        fg=COLOR_TEXT_LIGHT,
        activebackground=option["color"],
        activeforeground=COLOR_TEXT_LIGHT,
        bd=0,
        padx=30,
        pady=15
    )
    btn.pack(fill=tk.X, pady=5)
    buttons.append(btn)

# --- Initial CSV Header (Run once) ---
try:
    with open(FEEDBACK_FILE, 'x', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # *** CHANGE 2: Updated CSV Header to include Vehicle_Plate ***
        csv_writer.writerow(["Timestamp", "Vehicle_Plate", "Feedback_Rating"])
    logger.info(f"Created new CSV file: {FEEDBACK_FILE} with headers.")
except FileExistsError:
    logger.info(f"CSV file {FEEDBACK_FILE} already exists. Appending to it.")
except IOError as e:
    logger.error(f"Error checking/creating CSV file: {e}")

# --- Run the application ---
if __name__ == "__main__":
    logger.info("Super Metro Feedback App started.")
    root.mainloop()
    logger.info("Super Metro Feedback App closed.")