"""
Community Routes - Farmer Community Feed
- GET  /api/community/posts          - Get all posts (feed)
- POST /api/community/posts          - Create a post
- GET  /api/community/posts/<id>     - Get single post with comments
- DELETE /api/community/posts/<id>   - Delete own post
- POST /api/community/posts/<id>/like    - Toggle like
- GET  /api/community/posts/<id>/comments - Get comments
- POST /api/community/posts/<id>/comments - Add comment
- DELETE /api/community/comments/<id>    - Delete own comment
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.community import CommunityPost, Comment, PostLike
from app.utils.file_handler import save_community_image
from sqlalchemy import desc

community_bp = Blueprint('community', __name__)


@community_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get community posts feed"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    crop = request.args.get('crop', '')
    disease = request.args.get('disease', '')

    query = CommunityPost.query.filter_by(is_published=True)

    if crop:
        query = query.filter(CommunityPost.crop_name.ilike(f'%{crop}%'))
    if disease:
        query = query.filter(CommunityPost.disease_name.ilike(f'%{disease}%'))

    posts = query.order_by(desc(CommunityPost.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)

    # Check current user for liked status
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = int(get_jwt_identity())
    except Exception:
        pass

    results = []
    for post in posts.items:
        post_dict = post.to_dict()
        if current_user_id:
            liked = PostLike.query.filter_by(
                post_id=post.id, user_id=current_user_id
            ).first() is not None
            post_dict['is_liked'] = liked
        results.append(post_dict)

    return jsonify({
        'success': True,
        'posts': results,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    }), 200


@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new community post"""
    user_id = int(get_jwt_identity())

    # Handle both JSON and form data (for image uploads)
    if request.content_type and 'multipart' in request.content_type:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        crop_name = request.form.get('crop_name', '')
        disease_name = request.form.get('disease_name', '')
        location = request.form.get('location', '')
        tags = request.form.get('tags', '')
        crop_scan_id = request.form.get('crop_scan_id')
        image_path = None

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                result = save_community_image(file, user_id)
                if result['success']:
                    image_path = result['path']
    else:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        crop_name = data.get('crop_name', '')
        disease_name = data.get('disease_name', '')
        location = data.get('location', '')
        tags = data.get('tags', '')
        crop_scan_id = data.get('crop_scan_id')
        image_path = None

    if not title or not content:
        return jsonify({'success': False, 'message': 'Title and content are required'}), 400

    post = CommunityPost(
        user_id=user_id,
        crop_scan_id=crop_scan_id,
        title=title,
        content=content,
        image_path=image_path,
        crop_name=crop_name,
        disease_name=disease_name,
        location=location,
        tags=tags
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Post created successfully',
        'post': post.to_dict()
    }), 201


@community_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get single post with full details and comments"""
    post = CommunityPost.query.get(post_id)
    if not post or not post.is_published:
        return jsonify({'success': False, 'message': 'Post not found'}), 404

    # Increment view count
    post.views_count += 1
    db.session.commit()

    post_dict = post.to_dict()

    # Get comments (top-level only)
    comments = Comment.query\
        .filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.asc())\
        .all()

    post_dict['comments'] = []
    for c in comments:
        c_dict = c.to_dict()
        # Add replies
        replies = Comment.query.filter_by(parent_id=c.id)\
            .order_by(Comment.created_at.asc()).all()
        c_dict['replies'] = [r.to_dict() for r in replies]
        post_dict['comments'].append(c_dict)

    return jsonify({'success': True, 'post': post_dict}), 200


@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete own post"""
    user_id = int(get_jwt_identity())
    post = CommunityPost.query.filter_by(id=post_id, user_id=user_id).first()
    if not post:
        return jsonify({'success': False, 'message': 'Post not found or unauthorized'}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Post deleted'}), 200


@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    """Toggle like on a post"""
    user_id = int(get_jwt_identity())
    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Post not found'}), 404

    existing = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()

    if existing:
        db.session.delete(existing)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(like)
        post.likes_count += 1
        liked = True

    db.session.commit()

    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count
    }), 200


@community_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """Get paginated comments for a post"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    comments = Comment.query\
        .filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.asc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'comments': [c.to_dict() for c in comments.items],
        'total': comments.total,
        'pages': comments.pages
    }), 200


@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    """Add a comment to a post"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('content', '').strip():
        return jsonify({'success': False, 'message': 'Comment content is required'}), 400

    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Post not found'}), 404

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=data['content'].strip(),
        parent_id=data.get('parent_id')
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Comment added',
        'comment': comment.to_dict()
    }), 201


@community_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete own comment"""
    user_id = int(get_jwt_identity())
    comment = Comment.query.filter_by(id=comment_id, user_id=user_id).first()
    if not comment:
        return jsonify({'success': False, 'message': 'Comment not found or unauthorized'}), 404

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Comment deleted'}), 200
