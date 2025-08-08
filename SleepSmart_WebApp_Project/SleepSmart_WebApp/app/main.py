import streamlit as st
import numpy as np
import pandas as pd
import joblib
import datetime
import matplotlib.pyplot as plt
import os

from firebase_auth import signup, login, upload_sleep_data, get_sleep_data
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# Load ML model from correct path
model_path = os.path.join(os.path.dirname(__file__), ".", "model", "sleep_model.pkl")
model_path = os.path.normpath(model_path)
model = joblib.load(model_path)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

# Suggestion generator
def generate_suggestions(screen_time, caffeine, steps, water, stress, device_use_binary):
    suggestions = []
    if screen_time > 6:
        suggestions.append("📱 Reduce screen time to under 6 hours.")
    if caffeine > 3:
        suggestions.append("☕ Limit caffeine to 1-2 cups, especially after 4 PM.")
    if steps < 5000:
        suggestions.append("🚶 Aim for at least 7000 steps/day.")
    if water < 2:
        suggestions.append("💧 Increase water intake to 2+ liters.")
    if stress > 7:
        suggestions.append("🧘 Reduce stress with breathing or meditation.")
    if device_use_binary == 1:
        suggestions.append("📵 Avoid devices 30 mins before bed.")
    if not suggestions:
        suggestions.append("✅ Great job! Keep up the healthy habits.")
    return suggestions

# PDF Report Generator
def create_pdf_report(prediction, suggestions):
    filepath = "sleep_report.pdf"
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"<b>🛌 Sleep Quality Score:</b> {prediction:.2f}/10", styles['Title']),
        Spacer(1, 12),
        Paragraph("<b>📋 Personalized Suggestions:</b>", styles['Heading2']),
        Spacer(1, 6)
    ]
    for s in suggestions:
        elements.append(Paragraph(f"- {s}", styles['BodyText']))
        elements.append(Spacer(1, 6))
    doc.build(elements)
    return filepath

# Page config
st.set_page_config(layout="wide")
st.title("😴 Sleep Smart – Sleep Quality Dashboard")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# --- LOGIN ---
if choice == "Login":
    st.sidebar.subheader("🔐 Login")

    login_email = st.sidebar.text_input("Email")
    login_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        try:
            user = login(login_email, login_password)
            st.session_state.user = user
            st.success("✅ Logged in successfully!")
            st.rerun()

        except ValueError as e:
            if "INVALID_LOGIN_CREDENTIALS" in str(e):
                st.error("❌ Invalid email or password.")
            else:
                st.error("Login failed: " + str(e))

# --- SIGN UP ---
elif choice == "Sign Up":
    st.sidebar.subheader("📝 Sign Up")

    signup_email = st.sidebar.text_input("Email")
    signup_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Sign Up"):
        try:
            user = signup(signup_email, signup_password)
            st.success("✅ Account created. Please log in.")
            st.rerun()

        except ValueError as e:
            st.error("Signup failed: " + str(e))

# --- MAIN APP ---
if st.session_state.user:
    tab1, tab2 = st.tabs(["📝 Enter Data", "📊 Dashboard"])

    # --- Data Entry Tab ---
    with tab1:
        st.subheader("Enter Your Daily Habits")

        col1, col2 = st.columns(2)
        with col1:
            screen_time = st.slider("Screen Time (hours/day)", 0, 12, 5)
            caffeine = st.slider("Caffeine Intake (cups/day)", 0, 10, 2)
            steps = st.number_input("Steps Per Day", 0, 30000, 6000)
        with col2:
            water = st.slider("Water Intake (L)", 0.0, 5.0, 2.0)
            stress = st.slider("Stress Level (1-10)", 1, 10, 5)
            device_use = st.radio("Device Use Before Bed", ["Yes", "No"])

        if st.button("Predict Sleep Quality"):
            device_use_binary = 1 if device_use == "Yes" else 0
            features = np.array([[screen_time, caffeine, steps, water, stress, device_use_binary]])
            prediction = model.predict(features)[0]
            st.success(f"🛌 Predicted Sleep Quality Score: {prediction:.2f}/10")

            suggestions = generate_suggestions(screen_time, caffeine, steps, water, stress, device_use_binary)
            st.write("### 💡 Personalized Suggestions")
            for s in suggestions:
                st.markdown(f"- {s}")

            # Upload to Firebase
            entry = {
                "date": str(datetime.date.today()),
                "screen_time": screen_time,
                "caffeine": caffeine,
                "steps": steps,
                "water": water,
                "stress": stress,
                "device_use": device_use_binary,
                "prediction": float(prediction)
            }
            upload_sleep_data(st.session_state.user, entry)
            st.success("✅ Data saved to cloud!")

            # PDF Download
            pdf_path = create_pdf_report(prediction, suggestions)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download Report (PDF)", f, file_name="sleep_report.pdf")

    # --- Dashboard Tab ---
    with tab2:
        st.subheader("📊 Your Sleep Dashboard")
        data = get_sleep_data(st.session_state.user)

        if data:
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            st.write("### 📅 Weekly Averages")
            st.dataframe(df[["screen_time", "caffeine", "steps", "water", "stress", "prediction"]].mean().round(2))

            st.write("### 📈 Progress Over Time")
            st.line_chart(df.set_index("date")[["prediction", "screen_time", "stress"]])

            st.write("### 📊 Average Daily Habit Metrics (Bar Chart)")
            avg_values = df[["screen_time", "caffeine", "steps", "water", "stress"]].mean()
            labels = ['Screen Time', 'Caffeine', 'Steps (x1000)', 'Water (L)', 'Stress']
            values = [
                avg_values["screen_time"],
                avg_values["caffeine"],
                avg_values["steps"] / 1000,
                avg_values["water"],
                avg_values["stress"]
            ]

            fig, ax = plt.subplots()
            ax.barh(labels, values)
            ax.set_xlabel("Average Value")
            ax.set_title("📊 Average Daily Habit Metrics")
            st.pyplot(fig)
        else:
            st.info("No data yet. Please enter some habits first.")
