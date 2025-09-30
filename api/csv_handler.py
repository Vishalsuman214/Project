import os
import csv
import uuid
from datetime import datetime
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

USE_SQLITE = not os.environ.get('VERCEL')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'app.db') if USE_SQLITE else None
DATABASE_URL = os.environ.get('DATABASE_URL') if not USE_SQLITE else None

if os.environ.get('VERCEL'):
    TMP_DIR = '/tmp/data'
else:
    TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_CSV = os.path.join(TMP_DIR, 'users.csv')
REMINDERS_CSV = os.path.join(TMP_DIR, 'reminders.csv')

def init_db():
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            reminder_app_password TEXT,
            reminder_email TEXT,
            is_email_confirmed TEXT,
            reset_token TEXT,
            reset_expiry TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            reminder_time TEXT,
            created_at TEXT,
            is_completed TEXT,
            recipient_email TEXT
        )''')
        conn.commit()
        conn.close()
    else:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            reminder_app_password TEXT,
            reminder_email TEXT,
            is_email_confirmed TEXT,
            reset_token TEXT,
            reset_expiry TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            reminder_time TEXT,
            created_at TEXT,
            is_completed TEXT,
            recipient_email TEXT
        )''')
        conn.commit()
        conn.close()

def init_csv_files():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
    if not os.path.exists(REMINDERS_CSV):
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])

def add_user(username, email, password_hash):
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password_hash, reminder_app_password, reminder_email, is_email_confirmed, reset_token, reset_expiry) VALUES (?, ?, ?, '', ?, 'False', '', '')",
                  (username, email, password_hash, email))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    else:
        init_csv_files()
        user_id = get_next_user_id()
        with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([user_id, username, email, password_hash, '', email, 'False', '', ''])
        return user_id

def get_next_user_id():
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT MAX(id) FROM users")
        max_id = c.fetchone()[0]
        conn.close()
        return (max_id + 1) if max_id else 1
    else:
        if not os.path.exists(USERS_CSV):
            return 1
        with open(USERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ids = [int(row['id']) for row in reader]
            return max(ids) + 1 if ids else 1

def get_next_reminder_id():
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT MAX(id) FROM reminders")
        max_id = c.fetchone()[0]
        conn.close()
        return (max_id + 1) if max_id else 1
    elif DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("SELECT MAX(id) FROM reminders")
        max_id = c.fetchone()[0]
        conn.close()
        return (max_id + 1) if max_id else 1
    else:
        if not os.path.exists(REMINDERS_CSV):
            return 1
        with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ids = [int(row['id']) for row in reader]
            return max(ids) + 1 if ids else 1

def get_user_by_email(email):
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3],
                'reminder_app_password': row[4],
                'reminder_email': row[5],
                'is_email_confirmed': row[6],
                'reset_token': row[7],
                'reset_expiry': row[8]
            }
        return None
    else:
        if not os.path.exists(USERS_CSV):
            return None
        with open(USERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['email'] == email:
                    return row
        return None

def get_user_by_id(user_id):
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password_hash': row[3],
                'reminder_app_password': row[4],
                'reminder_email': row[5],
                'is_email_confirmed': row[6],
                'reset_token': row[7],
                'reset_expiry': row[8]
            }
        return None
    else:
        if not os.path.exists(USERS_CSV):
            return None
        with open(USERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == str(user_id):
                    return row
        return None

def update_user_email_credentials(user_id, email, app_password):
    print(f"🔄 Updating email credentials for user {user_id}")
    if USE_SQLITE:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET reminder_email = ?, reminder_app_password = ? WHERE id = ?",
                  (email, app_password, user_id))
        if c.rowcount > 0:
            conn.commit()
            print(f"✅ Credentials updated in SQLite for user {user_id}")
            conn.close()
            return True
        else:
            print(f"❌ User {user_id} not found in SQLite")
            conn.close()
            return False
    else:
        if not os.path.exists(USERS_CSV):
            print(f"❌ Users CSV not found at {USERS_CSV}")
            return False
        # Read all users
        users = []
        with open(USERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users = list(reader)

        # Update the specific user
        updated = False
        for user in users:
            if user['id'] == str(user_id):
                user['reminder_email'] = email
                user['reminder_app_password'] = app_password
                updated = True
                print(f"✅ Updated credentials for user {user_id}")
                break

        if not updated:
            print(f"❌ User {user_id} not found for credential update")

        if updated:
            # Write back all users
            with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
                writer.writeheader()
                writer.writerows(users)
            print(f"✅ Credentials saved to CSV for user {user_id}")
            return True
        return False

def migrate_csv_to_db():
    """Migrate existing reminders from CSV to database"""
    if not os.path.exists(REMINDERS_CSV):
        print("⚠️ No reminders CSV file found, skipping migration")
        return
    init_db()
    # Check if already migrated
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reminders")
        count = c.fetchone()[0]
        conn.close()
    else:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reminders")
        count = c.fetchone()[0]
        conn.close()
    if count > 0:
        print("✅ Migration already completed")
        return  # Already migrated
    print("🔄 Migrating reminders from CSV to database...")
    # Read CSV and insert
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reminders = list(reader)
    if not reminders:
        print("⚠️ No reminders to migrate")
        return
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for row in reminders:
            c.execute(
                "INSERT INTO reminders (id, user_id, title, description, reminder_time, created_at, is_completed, recipient_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (row['id'], row['user_id'], row['title'], row['description'], row['reminder_time'], row['created_at'], row['is_completed'], row['recipient_email'])
            )
        conn.commit()
        conn.close()
    else:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        for row in reminders:
            c.execute(
                "INSERT INTO reminders (id, user_id, title, description, reminder_time, created_at, is_completed, recipient_email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (row['id'], row['user_id'], row['title'], row['description'], row['reminder_time'], row['created_at'], row['is_completed'], row['recipient_email'])
            )
        conn.commit()
        conn.close()
    print(f"✅ Migrated {len(reminders)} reminders from CSV to database")

def get_all_reminders():
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM reminders")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    else:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        c = conn.cursor()
        c.execute("SELECT * FROM reminders")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def mark_reminder_completed(reminder_id):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE reminders SET is_completed = 'True' WHERE id = ?", (reminder_id,))
        updated = c.rowcount > 0
        if updated:
            conn.commit()
        conn.close()
        return updated
    else:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("UPDATE reminders SET is_completed = 'True' WHERE id = %s", (reminder_id,))
        updated = c.rowcount > 0
        if updated:
            conn.commit()
        conn.close()
        return updated

def add_reminder(user_id, title, description, reminder_time, recipient_email=None):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (user_id, title, description, reminder_time, created_at, is_completed, recipient_email) VALUES (?, ?, ?, ?, ?, 'False', ?)",
            (user_id, title, description, reminder_time.strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), recipient_email or '')
        )
        reminder_id = c.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    elif DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (user_id, title, description, reminder_time, created_at, is_completed, recipient_email) VALUES (%s, %s, %s, %s, %s, 'False', %s) RETURNING id",
            (user_id, title, description, reminder_time.strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), recipient_email or '')
        )
        reminder_id = c.fetchone()[0]
        conn.commit()
        conn.close()
        return reminder_id
    else:
        # Use CSV
        reminder_id = get_next_reminder_id()
        with open(REMINDERS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                reminder_id,
                user_id,
                title,
                description or '',
                reminder_time.strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'False',
                recipient_email or ''
            ])
        return reminder_id

def get_reminders_by_user_id(user_id):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM reminders WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    elif DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            c = conn.cursor()
            c.execute("SELECT * FROM reminders WHERE user_id = %s", (user_id,))
            rows = c.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error connecting to database for reminders: {e}, falling back to CSV")
            # Fall back to CSV
            try:
                if not os.path.exists(REMINDERS_CSV):
                    return []
                with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return [row for row in reader if row.get('user_id') == str(user_id)]
            except Exception as e:
                print(f"Error reading reminders CSV: {e}")
                return []
    else:
        # Use CSV
        try:
            if not os.path.exists(REMINDERS_CSV):
                return []
            with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row for row in reader if row.get('user_id') == str(user_id)]
        except Exception as e:
            print(f"Error reading reminders CSV: {e}")
            return []

def get_reminder_by_id(reminder_id):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    elif DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        c = conn.cursor()
        c.execute("SELECT * FROM reminders WHERE id = %s", (reminder_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    else:
        # Use CSV
        if not os.path.exists(REMINDERS_CSV):
            return None
        with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == str(reminder_id):
                    return row
        return None

def update_reminder(reminder_id, title, description, reminder_time, recipient_email=None):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE reminders SET title = ?, description = ?, reminder_time = ?, recipient_email = ? WHERE id = ?",
            (title, description, reminder_time.strftime('%Y-%m-%d %H:%M:%S'), recipient_email or '', reminder_id)
        )
        updated = c.rowcount > 0
        if updated:
            conn.commit()
        conn.close()
        return updated
    elif DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute(
            "UPDATE reminders SET title = %s, description = %s, reminder_time = %s, recipient_email = %s WHERE id = %s",
            (title, description, reminder_time.strftime('%Y-%m-%d %H:%M:%S'), recipient_email or '', reminder_id)
        )
        updated = c.rowcount > 0
        if updated:
            conn.commit()
        conn.close()
        return updated
    else:
        # Use CSV
        if not os.path.exists(REMINDERS_CSV):
            return False
        # Read all reminders
        reminders = []
        with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reminders = list(reader)

        # Update the specific reminder
        updated = False
        for reminder in reminders:
            if reminder['id'] == str(reminder_id):
                reminder['title'] = title
                reminder['description'] = description or ''
                reminder['reminder_time'] = reminder_time.strftime('%Y-%m-%d %H:%M:%S')
                reminder['recipient_email'] = recipient_email or ''
                updated = True
                break

        if updated:
            # Write back all reminders
            with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])
                writer.writeheader()
                writer.writerows(reminders)
        return updated

def delete_reminder(reminder_id):
    init_db()
    if USE_SQLITE:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        deleted = c.rowcount > 0
        if deleted:
            conn.commit()
        conn.close()
        return deleted
    elif DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE id = %s", (reminder_id,))
        deleted = c.rowcount > 0
        if deleted:
            conn.commit()
        conn.close()
        return deleted
    else:
        # Use CSV
        if not os.path.exists(REMINDERS_CSV):
            return False
        # Read all reminders
        reminders = []
        with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reminders = list(reader)

        # Find and remove the specific reminder
        original_length = len(reminders)
        reminders = [r for r in reminders if r['id'] != str(reminder_id)]

        if len(reminders) < original_length:
            # Write back all reminders
            with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])
                writer.writeheader()
                writer.writerows(reminders)
            return True
        return False

def generate_reset_token():
    return str(uuid.uuid4())

def set_reset_token(user_id, token, expiry):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['id'] == str(user_id):
            user['reset_token'] = token
            user['reset_expiry'] = expiry.strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def clear_reset_token(user_id):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['id'] == str(user_id):
            user['reset_token'] = ''
            user['reset_expiry'] = ''
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def get_user_by_reset_token(token):
    if not os.path.exists(USERS_CSV):
        return None
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['reset_token'] == token:
                return row
    return None

def confirm_user_email(user_id):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['id'] == str(user_id):
            user['is_email_confirmed'] = 'True'
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def is_user_email_confirmed(user_id):
    user = get_user_by_id(user_id)
    return user and user.get('is_email_confirmed') == 'True'

def update_user_password(user_id, new_hash):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['id'] == str(user_id):
            user['password_hash'] = new_hash
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False
