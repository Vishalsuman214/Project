import os
import csv
import uuid
import hashlib
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer

if os.environ.get('VERCEL'):
    TMP_DIR = '/tmp/data'
else:
    TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
USERS_CSV = os.path.join(TMP_DIR, 'users.csv')
REMINDERS_CSV = os.path.join(TMP_DIR, 'reminders.csv')

# For token generation
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
serializer = URLSafeTimedSerializer(SECRET_KEY)



def init_csv_files():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'email', 'password_hash', 'reminder_app_password', 'reminder_email', 'is_email_confirmed', 'verification_token', 'reset_token', 'reset_expiry'])
    if not os.path.exists(REMINDERS_CSV):
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email'])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_verification_token(email):
    return serializer.dumps(email, salt='email-verification')

def generate_reset_token(email):
    return serializer.dumps(email, salt='password-reset')

def verify_verification_token(token, max_age=86400):  # 24 hours
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except:
        return None

def verify_reset_token(token, max_age=3600):  # 1 hour
    try:
        email = serializer.loads(token, salt='password-reset', max_age=max_age)
        return email
    except:
        return None

def add_user(email, password, verification_token=''):
    init_csv_files()
    password_hash = hash_password(password)
    user_id = get_next_user_id()
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, email, email, password_hash, '', '', 'False', verification_token, '', ''])
    return user_id

def set_verification_token(email, token):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['email'] == email:
            user['verification_token'] = token
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'password_hash', 'email_verified', 'verification_token', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def verify_email(token):
    email = verify_verification_token(token)
    if not email:
        return False
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['email'] == email:
            user['email_verified'] = 'True'
            user['verification_token'] = ''
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'password_hash', 'email_verified', 'verification_token', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def set_reset_token(email, token):
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['email'] == email:
            user['reset_token'] = token
            user['reset_expiry'] = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'password_hash', 'email_verified', 'verification_token', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def reset_password(token, new_password):
    email = verify_reset_token(token)
    if not email:
        return False
    password_hash = hash_password(new_password)
    if not os.path.exists(USERS_CSV):
        return False
    users = []
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    updated = False
    for user in users:
        if user['email'] == email:
            user['password_hash'] = password_hash
            user['reset_token'] = ''
            user['reset_expiry'] = ''
            updated = True
            break

    if updated:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'password_hash', 'email_verified', 'verification_token', 'reset_token', 'reset_expiry'])
            writer.writeheader()
            writer.writerows(users)
        return True
    return False

def get_next_user_id():
    if not os.path.exists(USERS_CSV):
        return 1
    with open(USERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['id']) for row in reader]
        return max(ids) + 1 if ids else 1

def get_next_reminder_id():
    if not os.path.exists(REMINDERS_CSV):
        return 1
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
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
    print(f"🔄 Updating email credentials for user {user_id}")
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



def add_reminder(user_id, title, description, reminder_time, recipient_email=None, attachment=None):
    reminder_id = get_next_reminder_id()
    attachment_filename = None
    if attachment:
        # Save attachment to a folder
        attachments_dir = os.path.join(TMP_DIR, 'attachments')
        if not os.path.exists(attachments_dir):
            os.makedirs(attachments_dir)
        # Use unique filename to avoid collisions
        ext = os.path.splitext(attachment.filename)[1]
        attachment_filename = f"{reminder_id}_{uuid.uuid4().hex}{ext}"
        attachment_path = os.path.join(attachments_dir, attachment_filename)
        attachment.save(attachment_path)
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
            recipient_email or '',
            attachment_filename or ''
        ])
    return reminder_id

def get_reminders_by_user_id(user_id):
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
    if not os.path.exists(REMINDERS_CSV):
        return None
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == str(reminder_id):
                return row
    return None

def update_reminder(reminder_id, title, description, reminder_time, recipient_email=None, attachment=None):
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
            if attachment:
                # Save attachment to a folder
                attachments_dir = os.path.join(TMP_DIR, 'attachments')
                if not os.path.exists(attachments_dir):
                    os.makedirs(attachments_dir)
                ext = os.path.splitext(attachment.filename)[1]
                attachment_filename = f"{reminder_id}_{uuid.uuid4().hex}{ext}"
                attachment_path = os.path.join(attachments_dir, attachment_filename)
                attachment.save(attachment_path)
                reminder['attachment'] = attachment_filename
            updated = True
            break

    if updated:
        # Write back all reminders
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'title', 'description', 'reminder_time', 'created_at', 'is_completed', 'recipient_email', 'attachment'])
            writer.writeheader()
            writer.writerows(reminders)
    return updated

def delete_reminder(reminder_id):
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

def get_all_reminders():
    """Get all reminders from CSV"""
    if not os.path.exists(REMINDERS_CSV):
        return []
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def mark_reminder_completed(reminder_id):
    """Mark a reminder as completed in CSV"""
    if not os.path.exists(REMINDERS_CSV):
        return False
    reminders = []
    with open(REMINDERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reminders = list(reader)

    updated = False
    for reminder in reminders:
        if reminder['id'] == str(reminder_id):
            reminder['is_completed'] = 'True'
            updated = True
            break

    if updated:
        with open(REMINDERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'title', 'description', 'reminder_time', 'recipient_email', 'is_completed'])
            writer.writeheader()
            writer.writerows(reminders)
        return True
    return False
