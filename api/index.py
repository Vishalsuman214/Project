from flask import Flask, redirect, url_for
from flask_login import LoginManager
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from api.auth import User
from api.csv_handler import get_user_by_id
from api.email_service import check_and_send_reminders

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

    @app.route('/cron/reminders')
    def cron_reminders():
        check_and_send_reminders(app)
        return 'Reminders checked', 200

    # Register blueprints
    from api.auth import auth_bp
    from api.reminders import reminders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reminders_bp)

    # Set up background scheduler for email reminders
    scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(10)})

    # Schedule check_and_send_reminders to run every 5 minutes
    scheduler.add_job(
        func=check_and_send_reminders,
        args=[app],
        trigger=IntervalTrigger(minutes=5),
        id='check_reminders',
        name='Check and send due reminders',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()

    # Shut down the scheduler when exiting the app
    import atexit
    atexit.register(lambda: scheduler.shutdown())

    return app

# For Vercel deployment
app = create_app()
