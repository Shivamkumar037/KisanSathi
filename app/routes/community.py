from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, CommunityPost, Comment, Like, User
from app.services.cloudinary_service import upload_to_cloudinary
from app.utils import allowed_file, save_temp_crop_image

community_bp = Blueprint('community', __name__)

@community_bp.route('/post', methods=['POST'])
@jwt_required()
def create_post():
    user_id = int(get_jwt_identity())
    title = request.form.get('title', 'Untitled')
    problem = request.form.get('problem', '')
    solution = request.form.get('solution', '')

    file = request.files.get('image')
    cloudinary_url = None
    if file and allowed_file(file.filename):
        temp_path = save_temp_crop_image(file, user_id)
        try:
            cloudinary_url = upload_to_cloudinary(temp_path, folder="community")
        except:
            pass

    post = CommunityPost(user_id=user_id, title=title, problem=problem, solution=solution, cloudinary_url=cloudinary_url)
    db.session.add(post)
    db.session.commit()
    return jsonify({"message": "Post created", "post_id": post.id}), 201

@community_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).limit(10).all()
    result = []
    for p in posts:
        user = User.query.get(p.user_id)
        likes_count = Like.query.filter_by(post_id=p.id).count()
        comments = Comment.query.filter_by(post_id=p.id).all()
        result.append({
            "id": p.id,
            "title": p.title,
            "problem": p.problem,
            "solution": p.solution,
            "cloudinary_url": p.cloudinary_url,
            "author": user.name if user else "Kisan",
            "time": p.created_at.strftime("%d %b"),
            "likes": likes_count,
            "comments": [{"text": c.text, "author": User.query.get(c.user_id).name if User.query.get(c.user_id) else "Kisan"} for c in comments]
        })
    return jsonify({"posts": result})

@community_bp.route('/like/<int:post_id>', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user_id = int(get_jwt_identity())
    existing = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"message": "Like removed"})
    like = Like(post_id=post_id, user_id=user_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({"message": "Liked"})

@community_bp.route('/comment/<int:post_id>', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    user_id = int(get_jwt_identity())
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "Comment text required"}), 400
    comment = Comment(post_id=post_id, user_id=user_id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"message": "Comment added"})