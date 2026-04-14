from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.services.weather_service import get_10_day_weather

home_bp = Blueprint('home', __name__)

@home_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found. Please login again."}), 401
        
        weather = get_10_day_weather(user.district)
        
        return jsonify({
            "user": {"name": user.name, "district": user.district},
            "weather": weather
        })
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500