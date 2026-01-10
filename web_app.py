# Web application entry point
# This is a wrapper around server.py for web deployment
from server import app, socketio

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("Starting Chess Game Web Application...")
    print(f"Web interface available at http://localhost:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
