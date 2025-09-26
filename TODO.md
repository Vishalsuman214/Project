# TODO List

## Fix Confirmation Email Issue
- [x] Update api/email_service.py: Add os import and replace hardcoded SYSTEM_SENDER_EMAIL/SYSTEM_APP_PASSWORD with os.environ.get()
- [x] Update api/auth.py: Modify /register route to send OTP immediately after user creation and redirect to login with OTP prompt
- [x] Create .env.example file in root with SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD placeholders
- [x] Test the changes locally (requires setting env vars - copy .env.example to .env and fill in real Gmail credentials)
- [x] Update this TODO.md to mark tasks as completed

Note: Emails will not send until SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD are set in environment variables (e.g., via .env file or deployment platform).
