import pyotp
import qrcode
import io
import base64

def generate_totp_secret():
    """Generates a random 32-character base32 secret key for PyOTP."""
    return pyotp.random_base32()

def get_totp_uri(secret, email, app_name="AI Career Intelligence"):
    """Generates provisioning URI for authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=app_name)

def generate_qr_code_base64(secret, email, app_name="AI Career Intelligence"):
    """Generates a base64 encoded PNG QR code for quick scanning in authenticator apps."""
    uri = get_totp_uri(secret, email, app_name)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0d9488", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def verify_totp_code(secret, code):
    """Verifies a 6-digit TOTP code with PyOTP."""
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    # valid_window=1 allows 30s clock drift
    return totp.verify(str(code).strip(), valid_window=1)
