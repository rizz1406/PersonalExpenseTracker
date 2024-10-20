import firebase_admin
from firebase_admin import credentials, firestore,auth

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Your Firebase credentials file
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Firebase authentication
def create_user_with_email_password(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def sign_in_with_email_password(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Firebase doesn't provide direct sign-in with Python, so simulate it for now.
        return user.uid
    except Exception as e:
        print(f"Error signing in user: {e}")
        return None
