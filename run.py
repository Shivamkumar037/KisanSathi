"""
KrishiVani - AI-Powered Farmer Assistant Platform
Main application entry point
"""

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=8000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
