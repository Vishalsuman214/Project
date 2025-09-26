# TODO List

## Fix Confirmation Email Issue
- [x] Update api/email_service.py: Add os import and replace hardcoded SYSTEM_SENDER_EMAIL/SYSTEM_APP_PASSWORD with os.environ.get()
- [x] Update api/auth.py: Modify /register route to send OTP immediately after user creation and redirect to login with OTP prompt
- [x] Create .env.example file in root with SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD placeholders
- [x] Add fallback to console printing of OTP when system credentials not set for development/testing
- [x] Test the changes locally (OTP prints to console without env vars)
- [x] Update this TODO.md to mark tasks as completed

Note: For development, OTP is printed to console if env vars not set. For production, set SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD in environment variables.
