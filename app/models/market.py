"""
Market Rate Model - Mandi prices for crops
"""

from app import db
from datetime import datetime


class MarketRate(db.Model):
    __tablename__ = 'market_rates'

    id = db.Column(db.Integer, primary_key=True)
    commodity = db.Column(db.String(100), nullable=False)
    commodity_hindi = db.Column(db.String(100), nullable=True)
    commodity_emoji = db.Column(db.String(10), nullable=True)
    mandi_name = db.Column(db.String(150), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    min_price = db.Column(db.Float, nullable=False)
    max_price = db.Column(db.Float, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='quintal')
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'commodity': self.commodity,
            'commodity_hindi': self.commodity_hindi,
            'commodity_emoji': self.commodity_emoji,
            'mandi_name': self.mandi_name,
            'state': self.state,
            'district': self.district,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'avg_price': self.avg_price,
            'unit': self.unit,
            'date': self.date.isoformat()
        }

    def __repr__(self):
        return f'<MarketRate {self.commodity} @ {self.mandi_name}>'
