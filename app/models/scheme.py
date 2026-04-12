"""
Government Scheme Model
"""

from app import db
from datetime import datetime


class GovernmentScheme(db.Model):
    __tablename__ = 'government_schemes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=False)
    description_hindi = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=False)       # JSON string
    eligibility = db.Column(db.Text, nullable=False)    # JSON string
    documents_required = db.Column(db.Text, nullable=True)  # JSON string
    how_to_apply = db.Column(db.Text, nullable=True)
    official_website = db.Column(db.String(255), nullable=True)
    helpline = db.Column(db.String(50), nullable=True)
    icon_emoji = db.Column(db.String(10), nullable=True)
    category = db.Column(db.String(50), nullable=True)  # financial, insurance, irrigation, credit, market
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'description': self.description,
            'description_hindi': self.description_hindi,
            'benefits': json.loads(self.benefits) if self.benefits else [],
            'eligibility': json.loads(self.eligibility) if self.eligibility else [],
            'documents_required': json.loads(self.documents_required) if self.documents_required else [],
            'how_to_apply': self.how_to_apply,
            'official_website': self.official_website,
            'helpline': self.helpline,
            'icon_emoji': self.icon_emoji,
            'category': self.category,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<GovernmentScheme {self.short_name or self.name}>'
