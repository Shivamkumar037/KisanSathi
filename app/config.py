import os
from dotenv import load_dotenv

# .env file ko forcefully load karo (Windows ke liye safe)
load_dotenv(override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'fallback-secret-key-12345'
    
    # Database - yahan fallback bhi daal diya
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///krishivani.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'fallback-jwt-secret-12345'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    
    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/crops')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    PLANTNET_API_KEY = os.getenv('PLANTNET_API_KEY')
    OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')