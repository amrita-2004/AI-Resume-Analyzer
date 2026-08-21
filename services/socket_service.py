from flask_socketio import SocketIO, emit

socketio = SocketIO(cors_allowed_origins="*")

def init_socketio(app):
    socketio.init_app(app)

def emit_progress(step_pct, message, data=None):
    """Emits live analysis progress to connected WebSocket clients."""
    payload = {
        "percentage": step_pct,
        "message": message,
        "data": data or {}
    }
    try:
        socketio.emit('analysis_progress', payload)
        print(f"[WebSocket Progress] {step_pct}% - {message}")
    except Exception as e:
        print(f"[WebSocket Error] Could not emit event: {e}")
