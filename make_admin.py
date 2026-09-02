import os
import sys
import getpass
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'victoria.db')
AUTH_SALT = os.environ.get('AUTH_SALT', 'vic_college_salt_2026')

def hash_pass(password: str) -> str:
    return hashlib.sha256((password + AUTH_SALT).encode('utf-8')).hexdigest()

def main():
    email = sys.argv[1] if len(sys.argv) > 1 else 'mack.chen@viccollege.com'
    
    if len(sys.argv) > 2:
        password = sys.argv[2]
    else:
        password = os.environ.get('ADMIN_PASSWORD')
        if not password:
            password = getpass.getpass(f"Enter password for admin account ({email}): ")

    if len(password) < 6:
        print("[ERROR] Password must be at least 6 characters.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    password_hash = hash_pass(password)

    cursor.execute('SELECT id, name FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        cursor.execute('''
            UPDATE users 
            SET role = 'admin', status = 'active', password_hash = ?
            WHERE email = ?
        ''', (password_hash, email))
        print(f'[SUCCESS] Updated admin password and ensured active admin role for {email} (ID: {row[0]}) in SQLite DB!')
    else:
        name = email.split('@')[0].replace('.', ' ').title() + ' (Admin)'
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, provider, avatar_url, role, status, created_at, last_login_at)
            VALUES (?, ?, ?, 'email', 'images/avatar_admin.jpg', 'admin', 'active', ?, ?)
        ''', (name, email, password_hash, now_str, now_str))
        print(f'[SUCCESS] Created new Admin account {email} with secure password stored in SQLite DB!')

    conn.commit()

    cursor.execute("SELECT id, name, email, role, status, provider FROM users WHERE role = 'admin'")
    admins = cursor.fetchall()
    print('\nCurrent Active Administrators in SQLite DB:')
    for a in admins:
        print(f" - ID: {a[0]} | Name: {a[1]} | Email: {a[2]} | Role: {a[3]} | Status: {a[4]}")
    conn.close()

if __name__ == '__main__':
    main()
