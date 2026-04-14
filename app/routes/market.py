from flask import Blueprint, jsonify
from app.services.market_service import get_market_rates

market_bp = Blueprint('market', __name__)

@market_bp.route('/', methods=['GET'])
def market_rates():
    data = get_market_rates("Gorakhpur")
    return jsonify(data)