import os
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@aicareerintelligence.com')
    mail.init_app(app)

def send_otp_email(recipient_email, otp_code):
    """Sends OTP verification code via Flask-Mail with fallback logging for local development."""
    subject = f"Your 2FA Verification Code: {otp_code}"
    body = (
        f"Hello,\n\n"
        f"Your 2FA verification code for AI Career Intelligence is: {otp_code}\n\n"
        f"This code will expire in 5 minutes.\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Best regards,\n"
        f"AI Career Intelligence Team"
    )
    
    # Check if SMTP credentials configured
    smtp_user = os.environ.get('MAIL_USERNAME')
    if smtp_user and smtp_user != '':
        try:
            msg = Message(subject=subject, recipients=[recipient_email], body=body)
            mail.send(msg)
            print(f"[Email Service] Sent OTP email to {recipient_email}")
            return True, "OTP email sent successfully."
        except Exception as e:
            print(f"[Email Service Error] Failed to send email: {e}")
            return False, f"Email delivery error: {e}"
    else:
        # Development fallback mode
        print(f"==========================================")
        print(f"[DEV 2FA EMAIL MOCK] Recipient: {recipient_email}")
        print(f"[DEV 2FA EMAIL MOCK] 2FA OTP Code: {otp_code}")
        print(f"==========================================")
        return True, f"[Dev Mode] OTP generated: {otp_code}"
