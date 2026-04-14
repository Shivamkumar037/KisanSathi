import cloudinary
import cloudinary.uploader
from app.config import Config

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_to_cloudinary(file_path: str, folder: str = "community") -> str:
    """Community post ke photo ko Cloudinary pe upload karta hai"""
    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder=f"krishivani/{folder}",
            resource_type="image"
        )
        return result['secure_url']
    except Exception as e:
        raise Exception(f"Cloudinary upload fail: {str(e)}")