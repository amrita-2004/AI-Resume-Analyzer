from models.user_model import User
from auth.two_factor import create_2fa_challenge, verify_2fa_challenge, resend_2fa_otp

def register_user(email, password):
    """Registers a new user account."""
    if not email or not password:
        return None, "Email and password are required."
    if len(password) < 6:
        return None, "Password must be at least 6 characters long."
        
    user, err = User.create_user(email, password)
    return user, err

def authenticate_user(email, password):
    """
    Verifies user credentials. If valid, initiates a 2FA challenge.
    Returns (user, challenge_info, error_message).
    """
    if not email or not password:
        return None, None, "Email and password are required."
        
    user = User.get_by_email(email)
    if not user:
        return None, None, "Invalid email or password."
        
    if not user.check_password(password):
        return None, None, "Invalid email or password."
        
    # Initiate 2FA challenge
    challenge_info = create_2fa_challenge(user)
    return user, challenge_info, None

def verify_2fa(email, code):
    """Verifies 2FA challenge code and returns user if valid."""
    success, msg = verify_2fa_challenge(email, code)
    if not success:
        return None, msg
        
    user = User.get_by_email(email)
    return user, None
