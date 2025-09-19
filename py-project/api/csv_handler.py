import os
import csv

TMP_DIR = 'data'
USERS_CSV = os.path.join(TMP_DIR, 'users.csv')
REMINDERS_CSV = os.path.join(TMP_DIR, 'reminders.csv')

def init_csv_files():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'email', 'password_hash'])
    if not os.path.exists(REMINDERS_CSV):
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'user_id', 'reminder_text', 'reminder_time'])

def add_user(username, email, password_hash):
    init_csv_files()
    user_id = get_next_user_id()
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, email, password_hash])
    return user_id

def get_next_user_id():
    if not os.path.exists(USERS_CSV):
        return 1
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['id']) for row in reader]
        return max(ids) + 1 if ids else 1

# Additional functions like get_user_by_email, get_user_by_id, update_user_email_credentials can be added here as needed
