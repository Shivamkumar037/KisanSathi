from flask import Blueprint, jsonify

schemes_bp = Blueprint('schemes', __name__)

@schemes_bp.route('/', methods=['GET'])
def get_schemes():
    schemes = [
        {"name": "Pradhan Mantri Kisan Samman Nidhi (PM-Kisan)", "desc": "₹6,000 per year to eligible farmers", "link": "https://pmkisan.gov.in"},
        {"name": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)", "desc": "Improving irrigation facilities", "link": "https://pmksy.gov.in"},
        {"name": "Kisan Credit Card (KCC)", "desc": "Easy credit access for farming needs", "link": "#"},
        {"name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)", "desc": "Crop insurance against loss", "link": "https://pmfby.gov.in"},
        {"name": "National Agriculture Market (e-NAM)", "desc": "Online trading platform", "link": "https://enam.gov.in"}
    ]
    return jsonify({"schemes": schemes})