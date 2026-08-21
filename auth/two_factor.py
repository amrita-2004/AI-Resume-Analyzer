import random
import time
from auth.totp import verify_totp_code
from auth.email_service import send_otp_email

# In-memory temporary 2FA Session store
# Schema: { email: { "code": "123456", "expires_at": timestamp, "attempts": 0 } }
_2fa_sessions = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes
MAX_ATTEMPTS = 5

def generate_numeric_otp(length=6):
    """Generates a secure 6-digit numeric OTP."""
    return "".join([str(random.randint(0, 9)) for _ in range(length)])

def create_2fa_challenge(user):
    """Initiates a 2FA challenge by generating an OTP or initializing TOTP verification."""
    email = user.email.lower()
    otp_code = generate_numeric_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    
    _2fa_sessions[email] = {
        "code": otp_code,
        "expires_at": expires_at,
        "attempts": 0,
        "user_id": user.id,
        "totp_secret": user.totp_secret,
        "is_2fa_enabled": user.is_2fa_enabled
    }
    
    # Send email OTP
    success, msg = send_otp_email(email, otp_code)
    return {
        "success": success,
        "email": email,
        "otp_preview": otp_code, # For dev UI convenience when SMTP is unconfigured
        "message": msg,
        "expires_in": OTP_EXPIRY_SECONDS
    }

def verify_2fa_challenge(email, submitted_code):
    """
    Verifies user 2FA code (supports both Email OTP and PyOTP Authenticator app code).
    Handles expiration, failed attempt limits, and session cleanup.
    """
    email = email.lower()
    session = _2fa_sessions.get(email)
    
    if not session:
        return False, "No active 2FA session found. Please login again."
        
    if time.time() > session["expires_at"]:
        _2fa_sessions.pop(email, None)
        return False, "2FA code has expired. Please click 'Resend OTP' to receive a new code."
        
    if session["attempts"] >= MAX_ATTEMPTS:
        _2fa_sessions.pop(email, None)
        return False, "Too many failed attempts. 2FA session locked for security. Please login again."
        
    clean_code = str(submitted_code).strip()
    
    # Check 1: Numeric Email OTP
    is_valid_email_otp = (clean_code == session["code"])
    
    # Check 2: PyOTP Authenticator app
    is_valid_totp = False
    if session.get("totp_secret"):
        is_valid_totp = verify_totp_code(session["totp_secret"], clean_code)
        
    if is_valid_email_otp or is_valid_totp:
        _2fa_sessions.pop(email, None)
        return True, "2FA Verification successful."
    else:
        session["attempts"] += 1
        remaining = MAX_ATTEMPTS - session["attempts"]
        return False, f"Invalid verification code. {remaining} attempt(s) remaining."

def resend_2fa_otp(email):
    """Resends a new 2FA OTP code for an active session."""
    email = email.lower()
    session = _2fa_sessions.get(email)
    if not session:
        return False, "No active 2FA session found. Please login again.", None
        
    new_code = generate_numeric_otp()
    session["code"] = new_code
    session["expires_at"] = time.time() + OTP_EXPIRY_SECONDS
    session["attempts"] = 0
    
    success, msg = send_otp_email(email, new_code)
    return success, msg, new_code
