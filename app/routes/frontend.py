from flask import Blueprint, render_template, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

frontend_bp = Blueprint('frontend', __name__)

# ==================== PUBLIC PAGES ====================
@frontend_bp.route('/login')
def login_page():
    return render_template('login.html')

@frontend_bp.route('/signup')
def signup_page():
    return render_template('login.html')

@frontend_bp.route('/')
def home_redirect():
    return redirect('/login')

# ==================== NORMAL USER PAGES ====================
@frontend_bp.route('/home')
def home_page():
    return render_template('home.html')

@frontend_bp.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@frontend_bp.route('/chat')
def chat_page():
    return render_template('chat.html')

@frontend_bp.route('/voice')
def voice_page():
    return render_template('voice.html')

@frontend_bp.route('/schemes')
def schemes_page():
    return render_template('schemes.html')

@frontend_bp.route('/market')
def market_page():
    return render_template('market.html')

@frontend_bp.route('/community')
def community_page():
    return render_template('community.html')

@frontend_bp.route('/profile')
def profile_page():
    return render_template('profile.html')

# ==================== ADMIN ONLY DASHBOARD ====================
@frontend_bp.route('/dashboard')
@jwt_required()
def dashboard_page():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return redirect('/home')
    return render_template('dashboard.html')