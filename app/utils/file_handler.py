"""
File Handler Utilities
- Save crop images
- Save profile images
- Save community post images
- Save audio files
"""

import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'webm', 'm4a', 'aac', 'flac'}
MAX_IMAGE_SIZE = (1920, 1080)   # Max dimensions before resize
THUMBNAIL_SIZE = (400, 300)


def allowed_image(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def allowed_audio(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


def _generate_unique_filename(original_filename: str, prefix: str = '') -> str:
    """Generate a unique filename preserving extension"""
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'jpg'
    uid = uuid.uuid4().hex[:12]
    prefix = f"{prefix}_" if prefix else ""
    return f"{prefix}{uid}.{ext}"


def _save_and_optimize_image(file, save_path: str, max_size: tuple = None) -> bool:
    """Save image and optionally resize/optimize it"""
    try:
        img = Image.open(file)

        # Convert RGBA/palette to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if needed
        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save with optimization
        ext = save_path.rsplit('.', 1)[-1].lower()
        if ext in ('jpg', 'jpeg'):
            img.save(save_path, 'JPEG', quality=85, optimize=True)
        elif ext == 'png':
            img.save(save_path, 'PNG', optimize=True)
        elif ext == 'webp':
            img.save(save_path, 'WEBP', quality=85)
        else:
            img.save(save_path)

        return True
    except Exception as e:
        print(f"Image save error: {e}")
        return False


def save_crop_image(file, user_id) -> dict:
    """Save uploaded crop image for analysis"""
    if not allowed_image(file.filename):
        return {
            'success': False,
            'message': f'Invalid file type. Allowed: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        }

    folder = f'uploads/crops/{user_id}'
    os.makedirs(folder, exist_ok=True)

    filename = _generate_unique_filename(file.filename, prefix='crop')
    save_path = os.path.join(folder, filename)

    # Save and optimize
    file.stream.seek(0)
    success = _save_and_optimize_image(file, save_path, max_size=MAX_IMAGE_SIZE)

    if not success:
        # Fallback: save raw
        try:
            file.stream.seek(0)
            file.save(save_path)
        except Exception as e:
            return {'success': False, 'message': f'Failed to save image: {e}'}

    return {
        'success': True,
        'path': save_path,
        'filename': filename
    }


def save_profile_image(file, user_id) -> dict:
    """Save user profile picture"""
    if not allowed_image(file.filename):
        return {'success': False, 'message': 'Invalid image file'}

    folder = 'uploads/profiles'
    os.makedirs(folder, exist_ok=True)

    filename = _generate_unique_filename(file.filename, prefix=f'profile_{user_id}')
    save_path = os.path.join(folder, filename)

    file.stream.seek(0)
    # Profile images: square crop to 400x400
    try:
        img = Image.open(file)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Center crop to square
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        img = img.resize((400, 400), Image.Resampling.LANCZOS)
        img.save(save_path, 'JPEG', quality=90, optimize=True)
    except Exception as e:
        file.stream.seek(0)
        file.save(save_path)

    return {'success': True, 'path': save_path}


def save_community_image(file, user_id) -> dict:
    """Save community post image"""
    if not allowed_image(file.filename):
        return {'success': False, 'message': 'Invalid image file'}

    folder = f'uploads/community'
    os.makedirs(folder, exist_ok=True)

    filename = _generate_unique_filename(file.filename, prefix='post')
    save_path = os.path.join(folder, filename)

    file.stream.seek(0)
    success = _save_and_optimize_image(file, save_path, max_size=(1200, 900))

    if not success:
        file.stream.seek(0)
        file.save(save_path)

    return {'success': True, 'path': save_path}


def save_audio_file(file, user_id) -> dict:
    """Save audio file for voice message"""
    if not allowed_audio(file.filename):
        # Many browsers send blob without extension - accept it
        if file.filename == '' or '.' not in file.filename:
            pass  # Allow blobs
        else:
            return {
                'success': False,
                'message': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'
            }

    folder = f'uploads/audio/{user_id}'
    os.makedirs(folder, exist_ok=True)

    # Handle blob files (browser MediaRecorder output)
    ext = 'webm'
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()

    uid = uuid.uuid4().hex[:12]
    filename = f"voice_{uid}.{ext}"
    save_path = os.path.join(folder, filename)

    try:
        file.save(save_path)
        return {'success': True, 'path': save_path}
    except Exception as e:
        return {'success': False, 'message': f'Failed to save audio: {e}'}


def get_file_url(file_path: str, base_url: str = '') -> str:
    """Convert file path to accessible URL"""
    if not file_path:
        return None
    # Normalize path separators
    path = file_path.replace('\\', '/')
    return f"{base_url}/uploads/{path.split('uploads/')[-1]}" if 'uploads' in path else path
