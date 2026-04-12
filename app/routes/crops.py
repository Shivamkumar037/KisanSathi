"""
Crop Disease Detection Routes
- POST /api/crops/analyze        - Upload image and analyze
- GET  /api/crops/history        - User's scan history
- GET  /api/crops/<id>           - Get single scan result
- GET  /api/crops/diseases       - List known diseases (static)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from app.models.crop import CropScan
from app.services.crop_service import analyze_crop_image
from app.utils.file_handler import save_crop_image

crops_bp = Blueprint('crops', __name__)


@crops_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_crop():
    """
    Analyze uploaded crop image for diseases.
    Accepts: multipart/form-data with 'image' file
    Returns: diagnosis, treatment, prevention details
    """
    user_id = int(get_jwt_identity())

    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image uploaded. Please upload a crop photo.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Save image
    save_result = save_crop_image(file, user_id)
    if not save_result['success']:
        return jsonify(save_result), 400

    image_path = save_result['path']

    # Analyze with AI
    analysis = analyze_crop_image(image_path)

    # Save scan record
    scan = CropScan(
        user_id=user_id,
        image_path=image_path,
        crop_name=analysis.get('crop_name'),
        disease_detected=analysis.get('disease_detected'),
        severity=analysis.get('severity'),
        diagnosis=analysis.get('diagnosis'),
        treatment=analysis.get('treatment'),
        prevention=analysis.get('prevention'),
        is_crop_image=analysis.get('is_crop_image', True),
        raw_ai_response=analysis.get('raw_response')
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify({
        'success': True,
        'scan_id': scan.id,
        'result': scan.to_dict()
    }), 200


@crops_bp.route('/analyze/public', methods=['POST'])
def analyze_crop_public():
    """
    Analyze crop image without login (guest mode - limited).
    For quick demo use. Does NOT save to DB.
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Save temp image
    save_result = save_crop_image(file, user_id='guest')
    if not save_result['success']:
        return jsonify(save_result), 400

    analysis = analyze_crop_image(save_result['path'])

    return jsonify({
        'success': True,
        'result': analysis,
        'note': 'Login to save your scan history'
    }), 200


@crops_bp.route('/history', methods=['GET'])
@jwt_required()
def get_scan_history():
    """Get logged-in user's crop scan history"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    scans = CropScan.query\
        .filter_by(user_id=user_id)\
        .order_by(CropScan.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'scans': [s.to_dict() for s in scans.items],
        'total': scans.total,
        'pages': scans.pages,
        'current_page': page
    }), 200


@crops_bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    """Get single scan details"""
    user_id = int(get_jwt_identity())
    scan = CropScan.query.filter_by(id=scan_id, user_id=user_id).first()

    if not scan:
        return jsonify({'success': False, 'message': 'Scan not found'}), 404

    return jsonify({'success': True, 'scan': scan.to_dict()}), 200


@crops_bp.route('/diseases', methods=['GET'])
def get_diseases():
    """
    Get list of common crop diseases (static reference data).
    Useful for frontend search/filter.
    """
    diseases = [
        {"crop": "Tomato", "disease": "Leaf Spot", "symptoms": "Dark spots on leaves", "emoji": "🍅"},
        {"crop": "Tomato", "disease": "Early Blight", "symptoms": "Concentric ring-shaped spots", "emoji": "🍅"},
        {"crop": "Tomato", "disease": "Late Blight", "symptoms": "Water-soaked lesions", "emoji": "🍅"},
        {"crop": "Wheat", "disease": "Rust", "symptoms": "Orange/brown pustules on leaves", "emoji": "🌾"},
        {"crop": "Wheat", "disease": "Powdery Mildew", "symptoms": "White powdery coating", "emoji": "🌾"},
        {"crop": "Rice", "disease": "Blast", "symptoms": "Diamond-shaped lesions", "emoji": "🌾"},
        {"crop": "Rice", "disease": "Bacterial Blight", "symptoms": "Yellow-white leaf margins", "emoji": "🌾"},
        {"crop": "Potato", "disease": "Late Blight", "symptoms": "Dark water-soaked spots", "emoji": "🥔"},
        {"crop": "Chili", "disease": "Aphid Infestation", "symptoms": "Curling leaves, sticky residue", "emoji": "🌶️"},
        {"crop": "Sugarcane", "disease": "Red Rot", "symptoms": "Red discoloration inside stalk", "emoji": "🎋"},
        {"crop": "Onion", "disease": "Purple Blotch", "symptoms": "Purple spots on leaves", "emoji": "🧅"},
        {"crop": "Maize", "disease": "Northern Corn Blight", "symptoms": "Elongated grey-green lesions", "emoji": "🌽"},
    ]

    return jsonify({'success': True, 'diseases': diseases}), 200
