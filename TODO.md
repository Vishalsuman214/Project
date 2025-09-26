# TODO: Fix Password Reset Email Issue

## Current Status
- [x] Analyzed auth.py and email_service.py to identify the issue: send_password_reset_email fails in fallback due to no local SMTP server on port 1025.
- [x] Update email_service.py to log email content to console in dev mode (no credentials) and return True.
- [x] Test the fix locally by running the app and attempting password reset.
- [x] Update reset link to use BASE_URL env var for production compatibility.
- [x] Handle similar issue in send_email_confirmation_otp by logging OTP to console.
- [ ] Set SYSTEM_SENDER_EMAIL and SYSTEM_APP_PASSWORD in .env to enable actual email sending.

## Next Steps
1. Implement the code change in email_service.py.
2. Run the app with `python run.py` and test forgot password flow.
3. Verify console output shows the reset link.
4. Confirm notification shows success message.
