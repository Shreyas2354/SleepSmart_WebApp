import pyrebase
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Firebase configuration from environment variables
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Sign up a new user
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        raise ValueError(f"Signup failed: {e}")

# Log in an existing user
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        raise ValueError(f"Login failed: {e}")

# Upload sleep data to Firebase Realtime Database
def upload_sleep_data(user, data):
    try:
        db.child("users").child(user['localId']).child("sleep_data").push(data, user['idToken'])
    except Exception as e:
        raise ValueError(f"Data upload failed: {e}")

# Retrieve sleep data for a logged-in user
def get_sleep_data(user):
    try:
        records = db.child("users").child(user['localId']).child("sleep_data").get(user['idToken'])
        return [r.val() for r in records.each()] if records.each() else []
    except Exception as e:
        raise ValueError(f"Fetching sleep data failed: {e}")
