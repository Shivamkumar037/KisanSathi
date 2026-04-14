import os
from werkzeug.utils import secure_filename
from app.config import Config

def allowed_file(filename: str) -> bool:
    """Sirf allowed extensions accept karega"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_temp_crop_image(file, user_id: int) -> str:
    """Crop analysis ke liye temporary local file save karta hai"""
    filename = secure_filename(f"user_{user_id}_{file.filename}")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def delete_temp_image(filepath: str):
    """Analysis complete hone ke baad file delete kar deta hai"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass