"""
Crop Scan Model - stores image analysis results
"""

from app import db
from datetime import datetime


class CropScan(db.Model):
    __tablename__ = 'crop_scans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    crop_name = db.Column(db.String(100), nullable=True)
    disease_detected = db.Column(db.String(200), nullable=True)
    severity = db.Column(db.String(50), nullable=True)   # low, medium, high, none
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    prevention = db.Column(db.Text, nullable=True)
    is_crop_image = db.Column(db.Boolean, default=True)   # False if AI couldn't identify as crop
    raw_ai_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'crop_name': self.crop_name,
            'disease_detected': self.disease_detected,
            'severity': self.severity,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'prevention': self.prevention,
            'is_crop_image': self.is_crop_image,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<CropScan {self.id} - {self.crop_name}>'
