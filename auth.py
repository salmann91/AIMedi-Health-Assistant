import hashlib
import json
import os
import re
import secrets
from datetime import datetime

USERS_FILE = "users.json"


def hash_password(password: str, salt: str = None) -> str:
    """Hash password with a random salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salted hash, with legacy (unsalted) support."""
    if ':' in stored_hash:
        salt, _ = stored_hash.split(':', 1)
        return hash_password(password, salt) == stored_hash
    # Legacy: plain SHA-256 without salt — migrate on next login
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == stored_hash


def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_users(users: dict):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None


def register_user(username: str, password: str, email: str = "", full_name: str = "", dob: str = ""):
    if not username or not password:
        return False, "Username and password required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if email and not validate_email(email):
        return False, "Invalid email address"

    users = load_users()
    if username in users:
        return False, "Username already exists"

    if email:
        for u in users.values():
            if u.get("email", "").lower() == email.lower():
                return False, "Email already registered"

    users[username] = {
        "password": hash_password(password),
        "email": email,
        "full_name": full_name,
        "dob": dob,
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return True, "Registration successful!"


def verify_user(username: str, password: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    stored = users[username]["password"]
    if not verify_password(password, stored):
        return False
    # Migrate legacy unsalted hash to salted on successful login
    if ':' not in stored:
        users[username]["password"] = hash_password(password)
        save_users(users)
    return True


def get_user_info(username: str) -> dict:
    users = load_users()
    if username not in users:
        return {}
    u = users[username]
    return {
        "username": username,
        "email": u.get("email", ""),
        "full_name": u.get("full_name", ""),
        "dob": u.get("dob", ""),
        "created_at": u.get("created_at", "")
    }


def update_user_info(username: str, full_name=None, email=None, dob=None):
    users = load_users()
    if username not in users:
        return False, "User not found"
    if email and not validate_email(email):
        return False, "Invalid email address"
    if email:
        for uname, u in users.items():
            if uname != username and u.get("email", "").lower() == email.lower():
                return False, "Email already in use"
    if full_name is not None:
        users[username]["full_name"] = full_name
    if email is not None:
        users[username]["email"] = email
    if dob is not None:
        users[username]["dob"] = dob
    save_users(users)
    return True, "Profile updated successfully!"


def change_password(username: str, old_password: str, new_password: str):
    users = load_users()
    if username not in users:
        return False, "User not found"
    if not verify_password(old_password, users[username]["password"]):
        return False, "Current password is incorrect"
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    users[username]["password"] = hash_password(new_password)
    save_users(users)
    return True, "Password changed successfully!"


def create_default_admin():
    users = load_users()
    if not users:
        users["admin"] = {
            "password": hash_password("admin123"),
            "email": "",
            "full_name": "Administrator",
            "dob": "",
            "created_at": "default"
        }
        save_users(users)
