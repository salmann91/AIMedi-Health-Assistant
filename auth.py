import hashlib
import re
import secrets
import json
from datetime import datetime
from config import USERS_FILE

try:
    import database as database_module
    db_create_user = database_module.db_create_user
    db_get_user = database_module.db_get_user
    db_update_user = database_module.db_update_user
    db_update_password = database_module.db_update_password
    db_email_exists = database_module.db_email_exists
    db_user_count = database_module.db_user_count
except Exception:  # pragma: no cover - fallback when database module is unavailable
    database_module = None
    db_create_user = None
    db_get_user = None
    db_update_user = None
    db_update_password = None
    db_email_exists = None
    db_user_count = None


def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_users(users: dict) -> None:
    with open(USERS_FILE, 'w', encoding='utf-8') as fh:
        json.dump(users, fh, indent=2)


def _json_db_create_user(username: str, password_hash: str, email: str = '', full_name: str = '', dob: str = '') -> bool:
    users = _load_users()
    if username in users:
        return False
    users[username] = {
        'password': password_hash,
        'created_at': datetime.utcnow().isoformat(),
        'full_name': full_name,
        'email': email,
        'dob': dob,
    }
    _save_users(users)
    return True


def _json_db_get_user(username: str) -> dict:
    users = _load_users()
    user = users.get(username)
    if not user:
        return {}
    return {'username': username, **user}


def _json_db_update_user(username: str, full_name=None, email=None, dob=None) -> bool:
    users = _load_users()
    if username not in users:
        return False
    if full_name is not None:
        users[username]['full_name'] = full_name
    if email is not None:
        users[username]['email'] = email
    if dob is not None:
        users[username]['dob'] = dob
    _save_users(users)
    return True


def _json_db_update_password(username: str, new_hash: str) -> bool:
    users = _load_users()
    if username not in users:
        return False
    users[username]['password'] = new_hash
    _save_users(users)
    return True


def _json_db_email_exists(email: str, exclude_username: str = '') -> bool:
    users = _load_users()
    for username, info in users.items():
        if username == exclude_username:
            continue
        if info.get('email', '').lower() == email.lower():
            return True
    return False


def _json_db_user_count() -> int:
    return len(_load_users())


def _should_use_json_fallback() -> bool:
    return database_module is None or getattr(database_module, 'mysql', None) is None


def _db_create_user(username: str, password_hash: str, email: str = '', full_name: str = '', dob: str = '') -> bool:
    if _should_use_json_fallback() or db_create_user is None:
        return _json_db_create_user(username, password_hash, email, full_name, dob)
    return db_create_user(username, password_hash, email, full_name, dob)


def _db_get_user(username: str) -> dict:
    if _should_use_json_fallback() or db_get_user is None:
        return _json_db_get_user(username)
    return db_get_user(username)


def _db_update_user(username: str, full_name=None, email=None, dob=None) -> bool:
    if _should_use_json_fallback() or db_update_user is None:
        return _json_db_update_user(username, full_name, email, dob)
    return db_update_user(username, full_name, email, dob)


def _db_update_password(username: str, new_hash: str) -> bool:
    if _should_use_json_fallback() or db_update_password is None:
        return _json_db_update_password(username, new_hash)
    return db_update_password(username, new_hash)


def _db_email_exists(email: str, exclude_username: str = '') -> bool:
    if _should_use_json_fallback() or db_email_exists is None:
        return _json_db_email_exists(email, exclude_username)
    return db_email_exists(email, exclude_username)


def _db_user_count() -> int:
    if _should_use_json_fallback() or db_user_count is None:
        return _json_db_user_count()
    return db_user_count()


def derive_username_from_email(email: str) -> str:
    if not email:
        return ""
    local_part = email.split('@', 1)[0].strip().lower()
    local_part = re.sub(r'[^a-z0-9]+', '_', local_part)
    return local_part.strip('_')


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
    if not email or not password:
        return False, "Email and password required"
    if not validate_email(email):
        return False, "Invalid email address"

    username = (username or derive_username_from_email(email)).strip()
    if not username:
        return False, "Username could not be generated from email"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if _db_get_user(username):
        return False, "Username already exists"
    if email and _db_email_exists(email):
        return False, "Email already registered"

    ok = _db_create_user(username, hash_password(password), email, full_name, dob)
    if ok:
        return True, "Registration successful!"
    return False, "Registration failed. Please try again."


def verify_user(username: str, password: str) -> bool:
    user = _db_get_user(username)
    if not user:
        return False
    stored = user.get('password', '')
    if not verify_password(password, stored):
        return False
    # Migrate legacy unsalted hash
    if ':' not in stored:
        _db_update_password(username, hash_password(password))
    return True


def get_user_info(username: str) -> dict:
    user = _db_get_user(username)
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
    if email and _db_email_exists(email, exclude_username=username):
        return False, "Email already in use"
    ok = _db_update_user(username, full_name=full_name, email=email, dob=dob)
    if ok:
        return True, "Profile updated successfully!"
    return False, "Update failed. Please try again."


def change_password(username: str, old_password: str, new_password: str):
    user = _db_get_user(username)
    if not user:
        return False, "User not found"
    if not verify_password(old_password, user.get('password', '')):
        return False, "Current password is incorrect"
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    ok = _db_update_password(username, hash_password(new_password))
    if ok:
        return True, "Password changed successfully!"
    return False, "Failed to update password."


def create_default_admin():
    if _db_user_count() == 0:
        _db_create_user('admin', hash_password('admin123'), '', 'Administrator', '')
