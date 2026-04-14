from flask import Blueprint, jsonify
voice_bp = Blueprint('voice', __name__)

@voice_bp.route('/listen', methods=['GET'])
def voice_listen():
    return jsonify({"message": "Voice mode ready. Use browser SpeechRecognition on frontend."})