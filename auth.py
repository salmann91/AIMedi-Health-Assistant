import hashlib
import re
import secrets
from datetime import datetime
from database import (
    db_create_user, db_get_user, db_update_user,
    db_update_password, db_email_exists, db_user_count
)


def hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    if ':' in stored_hash:
        salt, _ = stored_hash.split(':', 1)
        return hash_password(password, salt) == stored_hash
    # Legacy unsalted SHA-256
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == stored_hash


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email))


def register_user(username: str, password: str, email: str = '', full_name: str = '', dob: str = ''):
    if not username or not password:
        return False, "Username and password required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if email and not validate_email(email):
        return False, "Invalid email address"
    if db_get_user(username):
        return False, "Username already exists"
    if email and db_email_exists(email):
        return False, "Email already registered"

    ok = db_create_user(username, hash_password(password), email, full_name, dob)
    if ok:
        return True, "Registration successful!"
    return False, "Registration failed. Please try again."


def verify_user(username: str, password: str) -> bool:
    user = db_get_user(username)
    if not user:
        return False
    stored = user.get('password', '')
    if not verify_password(password, stored):
        return False
    # Migrate legacy unsalted hash
    if ':' not in stored:
        db_update_password(username, hash_password(password))
    return True


def get_user_info(username: str) -> dict:
    user = db_get_user(username)
    if not user:
        return {}
    return {
        'username':   username,
        'email':      user.get('email', '') or '',
        'full_name':  user.get('full_name', '') or '',
        'dob':        user.get('dob', '') or '',
        'created_at': str(user.get('created_at', ''))
    }


def update_user_info(username: str, full_name=None, email=None, dob=None):
    if email and not validate_email(email):
        return False, "Invalid email address"
    if email and db_email_exists(email, exclude_username=username):
        return False, "Email already in use"
    ok = db_update_user(username, full_name=full_name, email=email, dob=dob)
    if ok:
        return True, "Profile updated successfully!"
    return False, "Update failed. Please try again."


def change_password(username: str, old_password: str, new_password: str):
    user = db_get_user(username)
    if not user:
        return False, "User not found"
    if not verify_password(old_password, user.get('password', '')):
        return False, "Current password is incorrect"
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    ok = db_update_password(username, hash_password(new_password))
    if ok:
        return True, "Password changed successfully!"
    return False, "Failed to update password."


def create_default_admin():
    if db_user_count() == 0:
        db_create_user('admin', hash_password('admin123'), '', 'Administrator', '')
