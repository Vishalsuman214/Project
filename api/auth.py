from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from api.csv_handler import add_user, get_user_by_email, verify_password, generate_verification_token, set_verification_token, verify_email, generate_reset_token, set_reset_token, reset_password
from flask_mail import Mail, Message
import os

auth_bp = Blueprint('auth', __name__)

mail = Mail()

def send_verification_email(email, token):
    domain = os.environ.get('DOMAIN', 'http://localhost:5000')
    verify_url = f"{domain}/verify?token={token}"
    msg = Message('Verify Your Email', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f'Click the link to verify your email: {verify_url}'
    mail.send(msg)
    return True

def send_reset_email(email, token):
    domain = os.environ.get('DOMAIN', 'http://localhost:5000')
    reset_url = f"{domain}/reset-password?token={token}"
    msg = Message('Reset Your Password', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f'Click the link to reset your password: {reset_url}'
    mail.send(msg)
    return True

class User:
    def __init__(self, id, email, password_hash):
        self.id = id
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

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user_data = get_user_by_email(email)
        if user_data:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.signup'))

        # Create new user
        token = generate_verification_token(email)
        user_id = add_user(email, password, token)
        set_verification_token(email, token)

        # Send verification email
        try:
            send_verification_email(email, token)
            flash('Account created! Please check your email to verify your account.', 'success')
        except Exception as e:
            flash('Account created but failed to send verification email.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/verify')
def verify():
    token = request.args.get('token')
    if not token:
        flash('Invalid verification link', 'error')
        return redirect(url_for('auth.login'))
    
    if verify_email(token):
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Invalid or expired verification link', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user_data = get_user_by_email(email)
        if user_data:
            token = generate_reset_token(email)
            from datetime import datetime, timedelta
            expiry = datetime.now() + timedelta(hours=1)
            set_reset_token(user_data['id'], token, expiry)
            try:
                send_reset_email(email, token)
                flash('If the email exists, a reset link has been sent.', 'info')
            except Exception as e:
                flash('Password reset unsuccessful - email not sent.', 'error')
        else:
            flash('If the email exists, a reset link has been sent.', 'info')  # Don't reveal if email exists
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = get_user_by_email(email)
        
        if user_data and verify_password(password, user_data['password_hash']) and user_data['is_email_confirmed'] == 'True':
            user = User(
                id=user_data['id'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
            
            login_user(user)
            return redirect(url_for('reminders.dashboard'))
        else:
            flash('Invalid email or password, or email not verified', 'error')
    
    return render_template('login.html')



@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_route():
    token = request.args.get('token') or request.form.get('token')
    if not token:
        flash('Invalid reset link', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('reset_password.html', token=token)

        if reset_password(token, password):
            flash('Password reset successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired reset token.', 'error')
            return render_template('reset_password.html', token=token)

    return render_template('reset_password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
