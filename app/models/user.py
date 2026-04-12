"""
User Model
"""

from app import db, bcrypt
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(50), default='Uttar Pradesh')
    district = db.Column(db.String(100), default='Gorakhpur')
    village = db.Column(db.String(100), nullable=True)
    preferred_language = db.Column(db.String(20), default='hi')  # hi, en
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = db.relationship('CommunityPost', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    crop_scans = db.relationship('CropScan', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'profile_image': self.profile_image,
            'state': self.state,
            'district': self.district,
            'village': self.village,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'
