from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from api.csv_handler import add_user, get_user_by_email, get_user_by_id, update_user_email_credentials, generate_reset_token, set_reset_token, clear_reset_token, get_user_by_reset_token, confirm_user_email, is_user_email_confirmed, update_user_password
from api.email_service import send_test_email, send_password_reset_email, send_email_confirmation_otp
import uuid
import random
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def set_auth_notification(message, category='info'):
    """Set authentication notification to be shown only on login page"""
    session['auth_notification'] = {
        'message': message,
        'category': category
    }

def get_auth_notification():
    """Get authentication notification and clear it from session"""
    notification = session.pop('auth_notification', None)
    return notification

class User:
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user_data = get_user_by_email(email)
        if user_data:
            set_auth_notification('Email address already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        password_hash = generate_password_hash(password, method='scrypt')
        user_id = add_user(username, email, password_hash)

        # Confirm email immediately (no OTP required)
        confirm_user_email(user_id)

        set_auth_notification('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user_data = get_user_by_email(email)
        if user_data:
            token = generate_reset_token()
            expiry = datetime.now() + timedelta(hours=1)
            set_reset_token(user_data['id'], token, expiry)
            success = send_password_reset_email(user_data['email'], token, user_data['username'])
            if success:
                set_auth_notification('If the email exists, a reset link has been sent.', 'info')
            else:
                set_auth_notification('Password reset unsuccessful - email not sent.', 'error')
        else:
            set_auth_notification('If the email exists, a reset link has been sent.', 'info')  # Don't reveal if email exists
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        otp = request.form.get('otp')
        
        user_data = get_user_by_email(email)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
            
            # Login directly (email confirmation removed)
            login_user(user)
            return redirect(url_for('reminders.dashboard'))
        else:
            set_auth_notification('Invalid email or password', 'error')
    
    notification = get_auth_notification()
    awaiting_otp = session.get('awaiting_otp', False)
    return render_template('login.html', get_auth_notification=lambda: notification, awaiting_otp=awaiting_otp)



@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_data = get_user_by_reset_token(token)
    if not user_data:
        set_auth_notification('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.login'))
    
    expiry_str = user_data.get('reset_expiry')
    if expiry_str:
        expiry = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry:
            clear_reset_token(user_data['id'])
            set_auth_notification('Reset token expired.', 'error')
            return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            set_auth_notification('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            set_auth_notification('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html', token=token)
        
        password_hash = generate_password_hash(password, method='scrypt')
        success = update_user_password(user_data['id'], password_hash)
        if success:
            clear_reset_token(user_data['id'])
            set_auth_notification('Password reset successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            set_auth_notification('Failed to reset password.', 'error')
            return render_template('reset_password.html', token=token)
    
    return render_template('reset_password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/email_credentials', methods=['GET', 'POST'])
@login_required
def email_credentials():
    from flask import current_app
    user_id = current_user.get_id()
    user_data = get_user_by_id(user_id)
    if request.method == 'POST':
        action = request.form.get('action')
        new_email = request.form.get('email')
        new_app_password = request.form.get('app_password')
        if action == 'test':
            if new_email and new_app_password:
                test_email_sent = send_test_email(new_email, new_app_password, new_email)
                if test_email_sent:
                    set_auth_notification('Test email sent successfully. Check your inbox.', 'success')
                else:
                    set_auth_notification('Failed to send test email. Please check your email and app password.', 'error')
            else:
                set_auth_notification('Please provide both email and app password to test.', 'error')
        elif action == 'save':
            if new_email and new_app_password:
                success = update_user_email_credentials(user_id, new_email, new_app_password)
                if success:
                    set_auth_notification('Email credentials updated successfully.', 'success')
                else:
                    set_auth_notification('Failed to update email credentials.', 'error')
            else:
                set_auth_notification('Please provide both email and app password.', 'error')
        return redirect(url_for('auth.email_credentials'))
    current_email = user_data.get('reminder_email', '') if user_data else ''
    current_app_password = user_data.get('reminder_app_password', '') if user_data else ''
    return render_template('email_credentials.html', current_email=current_email, current_app_password=current_app_password)
