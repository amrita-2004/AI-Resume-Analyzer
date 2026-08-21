from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import register_user, authenticate_user, verify_2fa
from auth.two_factor import resend_2fa_otp
from auth.totp import generate_totp_secret, generate_qr_code_base64

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', email=email)
            
        user, err = register_user(email, password)
        if err:
            flash(err, "danger")
            return render_template('register.html', email=email)
            
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user, challenge, err = authenticate_user(email, password)
        if err:
            flash(err, "danger")
            return render_template('login.html', email=email)
            
        session['pending_2fa_email'] = email
        session['otp_preview'] = challenge.get('otp_preview') # For local dev UI helper
        flash(f"2FA Code sent to {email}. Check your email or authenticator app.", "info")
        return redirect(url_for('auth.verify_2fa_page'))
        
    return render_template('login.html')

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa_page():
    email = session.get('pending_2fa_email')
    otp_preview = session.get('otp_preview')
    
    if not email:
        flash("No active login session. Please login.", "warning")
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        code = request.form.get('otp_code', '').strip()
        user, err = verify_2fa(email, code)
        if err:
            flash(err, "danger")
            return render_template('verify_2fa.html', email=email, otp_preview=otp_preview)
            
        login_user(user, remember=True)
        session.pop('pending_2fa_email', None)
        session.pop('otp_preview', None)
        flash("Authentication successful! Welcome to your dashboard.", "success")
        return redirect(url_for('main.dashboard'))
        
    return render_template('verify_2fa.html', email=email, otp_preview=otp_preview)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('pending_2fa_email')
    if not email:
        return jsonify({"success": False, "message": "No active 2FA session."}), 400
        
    success, msg, new_code = resend_2fa_otp(email)
    if success:
        session['otp_preview'] = new_code
        return jsonify({"success": True, "message": "New OTP sent!", "otp_preview": new_code})
    return jsonify({"success": False, "message": msg}), 400

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'enable':
            secret = session.get('temp_totp_secret')
            code = request.form.get('code', '').strip()
            from auth.totp import verify_totp_code
            if verify_totp_code(secret, code):
                current_user.totp_secret = secret
                current_user.is_2fa_enabled = True
                current_user.save()
                session.pop('temp_totp_secret', None)
                flash("Authenticator App (PyOTP) 2FA successfully enabled!", "success")
                return redirect(url_for('main.dashboard'))
            else:
                flash("Invalid code from authenticator app. Please try again.", "danger")
                
    secret = generate_totp_secret()
    session['temp_totp_secret'] = secret
    qr_code = generate_qr_code_base64(secret, current_user.email)
    return render_template('setup_2fa.html', secret=secret, qr_code=qr_code)

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
