from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.plantnet_service import analyze_crop_image
from app.services.groq_service import get_groq_response
from app.utils import save_temp_crop_image, delete_temp_image, allowed_file
from app.models import db, CropAnalysis

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/upload', methods=['POST'])
@jwt_required()
def crop_analysis():
    user_id = int(get_jwt_identity())
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filepath = save_temp_crop_image(file, user_id)

    # PlantNet
    plantnet_result = analyze_crop_image(filepath)

    if not plantnet_result.get("success"):
        delete_temp_image(filepath)
        return jsonify({"success": False, "error": plantnet_result.get("message", "Crop not detected")}), 400

    # Groq response
    prompt = f"Crop: {plantnet_result['plant']}. Problem: {request.form.get('problem', 'Crop looks unhealthy')}. Simple Hinglish solution de farmer ke liye."
    ai_response = get_groq_response(prompt)

    # Save in DB
    analysis = CropAnalysis(
        user_id=user_id,
        image_path=filepath,
        problem_description=request.form.get('problem', 'Crop disease'),
        ai_response=ai_response
    )
    db.session.add(analysis)
    db.session.commit()

    delete_temp_image(filepath)

    return jsonify({
        "success": True,
        "plant": plantnet_result["plant"],
        "confidence": plantnet_result["confidence"],
        "ai_response": ai_response
    })