from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.groq_service import get_groq_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def chat_message():
    data = request.get_json()
    user_message = data.get('message')
    
    system_prompt = "You are KrishiVani - friendly AI Farmer Assistant. Answer in simple Hinglish with headings, bullets, and clear steps. Always be helpful to Indian farmers."
    
    response = get_groq_response(user_message, system_prompt)
    
    return jsonify({"response": response})