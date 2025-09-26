import os
import csv
from datetime import datetime

TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_CSV = os.path.join(TMP_DIR, 'users.csv')
REMINDERS_CSV = os.path.join(TMP_DIR, 'reminders.csv')

def init_csv_files():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'email', 'password_hash', 'app_password'])
    if not os.path.exists(REMINDERS_CSV):
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])

def add_user(username, email, password_hash):
    init_csv_files()
    user_id = get_next_user_id()
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, email, password_hash, ''])
    return user_id

def get_next_user_id():
    if not os.path.exists(USERS_CSV):
        return 1
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['id']) for row in reader]
        return max(ids) + 1 if ids else 1

def get_user_by_email(email):
    if not os.path.exists(USERS_CSV):
        return None
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                return row
    return None

def get_user_by_id(user_id):
    if not os.path.exists(USERS_CSV):
        return None
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == str(user_id):
                return row
    return None

def update_user_email_credentials(user_id, email, app_password):
    if not os.path.exists(USERS_CSV):
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
            user['email'] = email
            user['app_password'] = app_password
            updated = True
            break

    if updated:
        # Write back all users
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'username', 'email', 'password_hash', 'app_password'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def get_all_reminders():
    if not os.path.exists(REMINDERS_CSV):
        return []
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def mark_reminder_completed(reminder_id):
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
            reminder['is_completed'] = 'True'
            updated = True
            break

    if updated:
        # Write back all reminders
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])
            writer.writeheader()
            writer.writerows(reminders)
        return True
    return False

def add_reminder(user_id, title, description, reminder_time, recipient_email=None):
    init_csv_files()
    reminder_id = get_next_reminder_id()
    with open(REMINDERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([reminder_id, user_id, title, description, reminder_time.strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'False', recipient_email or ''])
    return reminder_id

def get_next_reminder_id():
    if not os.path.exists(REMINDERS_CSV):
        return 1
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['id']) for row in reader]
        return max(ids) + 1 if ids else 1

def get_reminders_by_user_id(user_id):
    if not os.path.exists(REMINDERS_CSV):
        return []
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row['user_id'] == str(user_id)]

def get_reminder_by_id(reminder_id):
    if not os.path.exists(REMINDERS_CSV):
        return None
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == str(reminder_id):
                return row
    return None

def update_reminder(reminder_id, title, description, reminder_time, recipient_email=None):
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
            reminder['description'] = description
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
        return True
    return False

def delete_reminder(reminder_id):
    if not os.path.exists(REMINDERS_CSV):
        return False
    # Read all reminders
    reminders = []
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reminders = list(reader)

    # Remove the specific reminder
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
