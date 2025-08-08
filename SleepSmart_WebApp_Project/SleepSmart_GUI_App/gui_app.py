import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import numpy as np
import joblib
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# Load trained model
model = joblib.load("model/sleep_model.pkl")

# Generate suggestions
def generate_suggestions(screen_time, caffeine, steps, water, stress, device_use):
    suggestions = []
    if screen_time > 6:
        suggestions.append("📵 Reduce screen time before bed.")
    if caffeine > 2:
        suggestions.append("☕ Limit caffeine intake, especially in the evening.")
    if steps < 5000:
        suggestions.append("🚶‍♂️ Increase physical activity during the day.")
    if water < 2:
        suggestions.append("💧 Drink more water to stay hydrated.")
    if stress > 5:
        suggestions.append("🧘 Practice relaxation techniques to manage stress.")
    if device_use == 1:
        suggestions.append("📱 Avoid using electronic devices right before sleeping.")
    if not suggestions:
        suggestions.append("✅ Great job! Your habits support good sleep quality.")
    return suggestions

# Predict function
def predict():
    try:
        screen_time = float(screen_time_entry.get())
        caffeine = float(caffeine_entry.get())
        steps = int(steps_entry.get())
        water = float(water_entry.get())
        stress = int(stress_entry.get())
        device_use = 1 if device_use_var.get() == "Yes" else 0

        features = np.array([[screen_time, caffeine, steps, water, stress, device_use]])
        prediction = model.predict(features)[0]
        sleep_score = round(min(max(prediction, 0), 100))

        suggestions = generate_suggestions(screen_time, caffeine, steps, water, stress, device_use)

        global last_suggestions, last_score
        last_suggestions = suggestions
        last_score = sleep_score

        result_text = f"🛌 Predicted Sleep Quality Score: {sleep_score}/100\n\n📋 Personalized Suggestions:\n" + "\n".join(suggestions)
        result_label.config(text=result_text)
    except Exception as e:
        messagebox.showerror("Input Error", str(e))

# Export to PDF
def download_report():
    if not last_suggestions:
        messagebox.showerror("Error", "Please generate a prediction first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    flowables = []

    flowables.append(Paragraph("🛌 Sleep Quality Report", styles["Title"]))
    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph(f"Predicted Sleep Quality Score: {last_score}/100", styles["Normal"]))
    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph("📋 Personalized Suggestions:", styles["Heading2"]))
    for s in last_suggestions:
        flowables.append(Paragraph(s, styles["Normal"]))
    flowables.append(Spacer(1, 24))
    flowables.append(Paragraph("Thank you for using Sleep Smart!", styles["Italic"]))

    doc.build(flowables)
    messagebox.showinfo("Success", f"Report saved to:\n{file_path}")

# Initialize GUI
root = tk.Tk()
root.title("Sleep Smart – Sleep Quality Predictor")
root.geometry("900x600")
root.resizable(False, False)

# Center window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (900 // 2)
y = (screen_height // 2) - (600 // 2)
root.geometry(f"900x600+{x}+{y}")

# Frames
left_frame = tk.Frame(root, padx=20, pady=20)
left_frame.grid(row=0, column=0, sticky="nsew")

right_frame = tk.Frame(root, padx=20, pady=20)
right_frame.grid(row=0, column=1, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

label_font = ("Arial", 12)
entry_font = ("Arial", 12)

# Input fields
def add_row(label_text, row):
    label = tk.Label(left_frame, text=label_text, font=label_font)
    label.grid(row=row, column=0, sticky="w", pady=5)
    entry = tk.Entry(left_frame, font=entry_font)
    entry.grid(row=row, column=1, pady=5)
    return entry

screen_time_entry = add_row("📱 Screen Time (hrs):", 0)
caffeine_entry = add_row("☕ Caffeine Intake (cups):", 1)
steps_entry = add_row("🚶‍♂️ Steps Walked:", 2)
water_entry = add_row("💧 Water Intake (liters):", 3)
stress_entry = add_row("😰 Stress Level (1–10):", 4)

tk.Label(left_frame, text="📱 Device Use Before Bed:", font=label_font).grid(row=5, column=0, sticky="w", pady=5)
device_use_var = tk.StringVar()
device_use_dropdown = ttk.Combobox(left_frame, textvariable=device_use_var, values=["Yes", "No"], font=entry_font, state="readonly")
device_use_dropdown.grid(row=5, column=1, pady=5)
device_use_dropdown.current(0)

# Buttons
tk.Button(left_frame, text="🔍 Predict Sleep Quality", command=predict, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").grid(row=6, column=0, columnspan=2, pady=15, ipadx=10)
tk.Button(left_frame, text="📄 Download Report", command=download_report, font=("Arial", 12, "bold"), bg="#2196F3", fg="white").grid(row=7, column=0, columnspan=2, ipadx=10)

# Output label
result_label = tk.Label(
    right_frame, 
    text="", 
    wraplength=400, 
    justify="left", 
    anchor="nw", 
    font=("Arial", 13),
    bg="white", 
    relief="groove", 
    padx=10, pady=10
)
result_label.pack(expand=True, fill="both")

# Global vars for report
last_suggestions = []
last_score = None

root.mainloop()
