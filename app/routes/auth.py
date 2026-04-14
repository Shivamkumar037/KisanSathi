from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    district = data.get('district')
    password = data.get('password')

    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already registered"}), 400

    user = User(
        name=name,
        phone=phone,
        district=district,
        password_hash=generate_password_hash(password),
        is_admin=False
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Signup successful",
        "token": token,
        "redirect": "/home"          # ← Normal user ko home pe bhej rahe hain
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    user = User.query.filter_by(phone=phone).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid phone or password"}), 401

    token = create_access_token(identity=str(user.id))
    redirect_url = "/dashboard" if user.is_admin else "/home"

    return jsonify({
        "message": "Login successful",
        "token": token,
        "redirect": redirect_url
    }), 200