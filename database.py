try:
    import mysql.connector
    from mysql.connector import Error
except Exception:  # pragma: no cover - fallback when MySQL driver is missing
    mysql = None
    Error = Exception

import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# Railway uses MYSQLHOST/MYSQLUSER/etc, local uses MYSQL_HOST/MYSQL_USER/etc
_host = os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')
_ssl  = {'ssl_disabled': False} if 'aivencloud.com' in _host else {}

DB_CONFIG = {
    'host':     _host,
    'port':     int(os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', 3306)),
    'user':     os.getenv('MYSQLUSER')     or os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'aimedi_db'),
    'autocommit': True,
    **_ssl
}

def get_connection():
    if mysql is None:
        raise Error("MySQL connector is not installed")
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """Create all tables if they don't exist."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                username    VARCHAR(50)  UNIQUE NOT NULL,
                password    VARCHAR(200) NOT NULL,
                email       VARCHAR(100) UNIQUE,
                full_name   VARCHAR(100),
                dob         VARCHAR(20),
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                user_id         INT NOT NULL,
                filename        VARCHAR(255),
                patient_name    VARCHAR(100),
                patient_age     VARCHAR(20),
                patient_gender  VARCHAR(20),
                report_date     VARCHAR(50),
                risk_score      INT,
                risk_level      VARCHAR(20),
                ai_summary      TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS blood_parameters (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                report_id    INT NOT NULL,
                parameter    VARCHAR(50),
                value        FLOAT,
                unit         VARCHAR(30),
                status       VARCHAR(20),
                severity     VARCHAR(20),
                ref_min      FLOAT,
                ref_max      FLOAT,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
            )
        """)

        cur.close()
        conn.close()
        print("Database initialized successfully.")
        return True
    except Error as exc:
        print(f"Database initialization skipped: {exc}")
        return False

# ── User operations ────────────────────────────────────────────────────────────

def db_create_user(username, password_hash, email='', full_name='', dob='') -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, email, full_name, dob) VALUES (%s,%s,%s,%s,%s)",
            (username, password_hash, email or None, full_name, dob)
        )
        cur.close(); conn.close()
        return True
    except Error:
        return False

def db_get_user(username) -> dict:
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return row or {}
    except Error:
        return {}

def db_update_user(username, full_name=None, email=None, dob=None) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        if full_name is not None:
            cur.execute("UPDATE users SET full_name=%s WHERE username=%s", (full_name, username))
        if email is not None:
            cur.execute("UPDATE users SET email=%s WHERE username=%s", (email or None, username))
        if dob is not None:
            cur.execute("UPDATE users SET dob=%s WHERE username=%s", (dob, username))
        cur.close(); conn.close()
        return True
    except Error:
        return False

def db_update_password(username, new_hash) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=%s WHERE username=%s", (new_hash, username))
        cur.close(); conn.close()
        return True
    except Error:
        return False

def db_email_exists(email, exclude_username='') -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s AND username!=%s", (email, exclude_username))
        exists = cur.fetchone() is not None
        cur.close(); conn.close()
        return exists
    except Error:
        return False

def db_user_count() -> int:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        cur.close(); conn.close()
        return count
    except Error:
        return 0

# ── Report operations ──────────────────────────────────────────────────────────

def db_save_report(username, filename, patient_info, analysis, ai_summary) -> int:
    """Save a full report and return report_id."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if not user:
            return None
        user_id = user[0]

        risk = analysis.get('risk_assessment', {})
        cur.execute("""
            INSERT INTO reports
              (user_id, filename, patient_name, patient_age, patient_gender,
               report_date, risk_score, risk_level, ai_summary)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            filename,
            patient_info.get('name', ''),
            str(patient_info.get('age', '')),
            patient_info.get('gender', ''),
            patient_info.get('report_date', ''),
            risk.get('overall_risk_score', 0),
            risk.get('risk_level', ''),
            ai_summary
        ))
        report_id = cur.lastrowid

        for r in analysis.get('results', []):
            cur.execute("""
                INSERT INTO blood_parameters
                  (report_id, parameter, value, unit, status, severity, ref_min, ref_max)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                report_id,
                r.get('parameter', ''),
                r.get('value', 0),
                r.get('unit', ''),
                r.get('status', ''),
                r.get('severity', ''),
                r.get('reference_min', 0),
                r.get('reference_max', 0)
            ))

        cur.close(); conn.close()
        return report_id
    except Error as e:
        print(f"Error saving report: {e}")
        return None

def db_get_user_reports(username) -> list:
    """Get all reports for a user (summary only)."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT r.id, r.filename, r.patient_name, r.patient_age,
                   r.patient_gender, r.report_date, r.risk_score,
                   r.risk_level, r.created_at
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE u.username = %s
            ORDER BY r.created_at DESC
        """, (username,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows
    except Error:
        return []

def db_get_report_detail(report_id) -> dict:
    """Get full report with blood parameters."""
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM reports WHERE id=%s", (report_id,))
        report = cur.fetchone()
        if not report:
            return {}
        cur.execute("SELECT * FROM blood_parameters WHERE report_id=%s", (report_id,))
        report['parameters'] = cur.fetchall()
        cur.close(); conn.close()
        return report
    except Error:
        return {}

def db_delete_report(report_id) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM reports WHERE id=%s", (report_id,))
        cur.close(); conn.close()
        return True
    except Error:
        return False
