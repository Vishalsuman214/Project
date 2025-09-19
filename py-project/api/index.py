from flask import Flask, redirect, url_for
from flask_login import LoginManager
import os
from auth import User
from csv_handler import get_user_by_id

# Initialize extensions
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates')

    @login_manager.user_loader
    def load_user(user_id):
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
        return None

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Initialize extensions with app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    # Register blueprints
    from auth import auth_bp
    from reminders import reminders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reminders_bp)

    # Note: BackgroundScheduler removed for Vercel deployment
    # Email reminders will need to be handled differently in serverless environment

    return app

# For Vercel deployment
app = create_app()
