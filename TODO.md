# TODO: Fix APScheduler Warning and Ensure Reset Password Emails

## Current Status
- [x] Identified APScheduler warning due to sequential email sending taking too long.
- [x] Optimized check_and_send_reminders to send emails in parallel using ThreadPoolExecutor.
- [x] Increased scheduler ThreadPoolExecutor to 20 threads.
- [x] Added ProcessPoolExecutor for better performance.
- [x] Password reset emails are handled: logs to console in dev mode if SYSTEM_SENDER_EMAIL/SYSTEM_APP_PASSWORD not set, otherwise sends via Gmail.
- [x] Ensure SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD are set in .env for actual email sending.

## Next Steps
1. Set SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD in .env if not already set.
2. Run the app and monitor for APScheduler warnings.
3. Test password reset flow to ensure emails are sent or logged.
