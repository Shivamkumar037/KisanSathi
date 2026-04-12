"""
Authentication Routes
- POST /api/auth/register
- POST /api/auth/login
- GET  /api/auth/profile
- PUT  /api/auth/profile
- POST /api/auth/logout
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app import db
from app.models.user import User
from app.utils.validators import validate_phone, validate_required_fields
from app.utils.file_handler import save_profile_image
import os

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new farmer account"""
    data = request.get_json()

    # Validate required fields
    required = ['name', 'phone', 'password']
    error = validate_required_fields(data, required)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # Validate phone
    if not validate_phone(data['phone']):
        return jsonify({'success': False, 'message': 'Invalid phone number format'}), 400

    # Check if phone already exists
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'success': False, 'message': 'Phone number already registered'}), 409

    # Check email uniqueness if provided
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    # Create user
    user = User(
        name=data['name'],
        phone=data['phone'],
        email=data.get('email'),
        state=data.get('state', 'Uttar Pradesh'),
        district=data.get('district', 'Gorakhpur'),
        village=data.get('village'),
        preferred_language=data.get('preferred_language', 'hi')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Generate token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'success': True,
        'message': 'Registration successful! Welcome to KrishiVani.',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with phone + password"""
    data = request.get_json()

    required = ['phone', 'password']
    error = validate_required_fields(data, required)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    user = User.query.filter_by(phone=data['phone']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Invalid phone number or password'}), 401

    if not user.is_active:
        return jsonify({'success': False, 'message': 'Account is deactivated'}), 403

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user.name}!',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get logged-in user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    data = request.get_json()

    # Update allowed fields
    updatable = ['name', 'email', 'state', 'district', 'village', 'preferred_language']
    for field in updatable:
        if field in data:
            setattr(user, field, data[field])

    # Update password if provided
    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'success': False, 'message': 'Current password required'}), 400
        if not user.check_password(data['current_password']):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        user.set_password(data['new_password'])

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile/image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload profile picture"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    result = save_profile_image(file, user_id)
    if not result['success']:
        return jsonify(result), 400

    user.profile_image = result['path']
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile image updated',
        'image_path': result['path']
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Quick check - get current user info"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({'success': True, 'user': user.to_dict()}), 200
