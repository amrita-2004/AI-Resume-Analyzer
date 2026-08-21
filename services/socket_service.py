import os
from flask_socketio import SocketIO

IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

def init_socketio(app):
    try:
        socketio.init_app(app)
    except Exception as e:
        print(f"[WebSocket Warning] Could not init socketio: {e}")

def emit_progress(step_pct, message, data=None):
    """Emits live analysis progress to connected WebSocket clients safely."""
    payload = {
        "percentage": step_pct,
        "message": message,
        "data": data or {}
    }
    try:
        socketio.emit('analysis_progress', payload)
        print(f"[WebSocket Progress] {step_pct}% - {message}")
    except Exception as e:
        # Ignore socket emission errors gracefully in serverless environment
        pass
