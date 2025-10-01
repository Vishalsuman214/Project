# TODO: Generate Flask backend with CSV database for user authentication

- [x] Update users.csv fields to: id,email,password_hash,email_verified,verification_token,reset_token,reset_expiry
- [x] Update csv_handler.py functions for new user fields
- [x] Add required dependencies: Flask-Mail, itsdangerous
- [x] Implement authentication routes: /signup, /verify, /login, /forgot-password, /reset-password
- [x] Add email sending functionality
- [x] Create HTML forms for signup, login, forgot password, reset password
- [x] Update index.py to include new routes
- [x] Test all functionality
