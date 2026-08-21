import os
from flask import Flask, send_from_directory, jsonify, render_template
from flask_login import LoginManager

from models.user_model import User
from auth.email_service import init_mail
from services.socket_service import init_socketio, socketio

from routes.auth_routes import auth_bp
from routes.api_routes import api_bp
from routes.main_routes import main_bp

app = Flask(__name__)

# Security & Session Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-resume-analyzer-production-secret-key-2026')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Secure Cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'docs/flow-diagram'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'docs/architecture'), exist_ok=True)

# Initialize Flask Extensions
init_mail(app)
init_socketio(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Static Diagram Serving Routes
@app.route('/docs/flow-diagram/<path:filename>')
def serve_flow_diagram(filename):
    return send_from_directory(os.path.join(app.root_path, 'docs', 'flow-diagram'), filename)

@app.route('/docs/architecture/<path:filename>')
def serve_architecture_diagram(filename):
    return send_from_directory(os.path.join(app.root_path, 'docs', 'architecture'), filename)

# Production Error Handlers
@app.errorhandler(400)
def bad_request_error(e):
    return jsonify({"error": "Bad Request", "message": str(e)}), 400

@app.errorhandler(401)
def unauthorized_error(e):
    return jsonify({"error": "Unauthorized", "message": "Authentication required."}), 401

@app.errorhandler(403)
def forbidden_error(e):
    return jsonify({"error": "Forbidden", "message": "Access denied."}), 403

@app.errorhandler(404)
def not_found_error(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not Found", "message": "API endpoint does not exist."}), 404
    return render_template('docs.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected server error occurred."}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
