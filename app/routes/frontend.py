# app/routes/frontend.py

from flask import Blueprint, render_template, send_from_directory, current_app
import os

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve uploaded files (images, audio)"""
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)


@frontend_bp.route('/')
@frontend_bp.route('/<path:path>')
def index(path=''):
    # Don't catch uploads or api routes
    if path.startswith('uploads/') or path.startswith('api/'):
        from flask import abort
        abort(404)
    return render_template('index.html')
