import hashlib
import json
import os
import base64
import uuid
from datetime import datetime
from config import USERS_FILE, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
import streamlit as st

def make_hashed_password(password):
    """Create a hashed version of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_password, user_password):
    """Verify a password against its stored hash"""
    return stored_password == make_hashed_password(user_password)

def load_users():
    """Load users from file or create default admin if file doesn't exist"""
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default admin user if no user file exists
        users = {
            DEFAULT_ADMIN_USERNAME: {
                "password": make_hashed_password(DEFAULT_ADMIN_PASSWORD),
                "role": "admin",
                "name": "Administrator",
                "email": "admin@example.com",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": None
            }
        }
        save_users(users)
        return users

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def create_user(username, password, name, email, role="user"):
    """Create a new user"""
    if username in st.session_state.users:
        return False, "Username already exists"
    
    st.session_state.users[username] = {
        "password": make_hashed_password(password),
        "role": role,
        "name": name,
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }
    save_users(st.session_state.users)
    return True, "User created successfully"

def update_user(username, **kwargs):
    """Update user details"""
    if username not in st.session_state.users:
        return False, "User not found"
    
    for key, value in kwargs.items():
        if key == "password" and value:  # Only update password if a new one is provided
            value = make_hashed_password(value)
        if value:  # Only update if a value is provided
            st.session_state.users[username][key] = value
    
    save_users(st.session_state.users)
    return True, "User updated successfully"

def delete_user(username):
    """Delete a user"""
    if username not in st.session_state.users:
        return False, "User not found"
    
    if username == "admin":
        return False, "Cannot delete admin user"
    
    del st.session_state.users[username]
    save_users(st.session_state.users)
    return True, "User deleted successfully"

def authenticate(username, password):
    """Authenticate a user"""
    if username not in st.session_state.users:
        return False, "Invalid username or password"
    
    stored_password = st.session_state.users[username]["password"]
    if check_password(stored_password, password):
        # Update last login time
        st.session_state.users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(st.session_state.users)
        return True, "Authentication successful"
    else:
        return False, "Invalid username or password"

def generate_password():
    """Generate a random secure password"""
    return base64.b64encode(os.urandom(9)).decode('utf-8')

def generate_credentials(n=5):
    """Generate multiple sets of credentials"""
    credentials = []
    for _ in range(n):
        username = f"user_{uuid.uuid4().hex[:6]}"
        password = generate_password()
        credentials.append((username, password))
    return credentials