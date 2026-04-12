"""
Community Post and Comment Models
"""

from app import db
from datetime import datetime


class CommunityPost(db.Model):
    __tablename__ = 'community_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_scan_id = db.Column(db.Integer, db.ForeignKey('crop_scans.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    crop_name = db.Column(db.String(100), nullable=True)
    disease_name = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    tags = db.Column(db.String(300), nullable=True)        # comma-separated
    likes_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_author=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'crop_scan_id': self.crop_scan_id,
            'title': self.title,
            'content': self.content,
            'image_path': self.image_path,
            'crop_name': self.crop_name,
            'disease_name': self.disease_name,
            'location': self.location,
            'tags': self.tags.split(',') if self.tags else [],
            'likes_count': self.likes_count,
            'views_count': self.views_count,
            'comments_count': len(self.comments),
            'created_at': self.created_at.isoformat()
        }
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
                'profile_image': self.author.profile_image,
                'district': self.author.district
            }
        return data

    def __repr__(self):
        return f'<CommunityPost {self.id} by User {self.user_id}>'


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # nested comments
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def to_dict(self, include_author=True):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'likes_count': self.likes_count,
            'replies_count': len(self.replies),
            'created_at': self.created_at.isoformat()
        }
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
                'profile_image': self.author.profile_image
            }
        return data

    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'


class PostLike(db.Model):
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )

    def __repr__(self):
        return f'<PostLike Post={self.post_id} User={self.user_id}>'
