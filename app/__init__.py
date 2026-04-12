"""
KrishiVani App Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

# Extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

    # ─── Configuration ───────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'krishivani-dev-secret-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///krishivani.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-krishivani-secret')
    # flask-jwt-extended 4.x requires timedelta, not int
    jwt_expires_seconds = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=jwt_expires_seconds)
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads/crops')

    # Create upload folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('uploads/profiles', exist_ok=True)
    os.makedirs('uploads/community', exist_ok=True)
    os.makedirs('uploads/audio', exist_ok=True)

    # ─── Initialize Extensions ───────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ─── Register Blueprints ─────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.crops import crops_bp
    from app.routes.market import market_bp
    from app.routes.schemes import schemes_bp
    from app.routes.community import community_bp
    from app.routes.chat import chat_bp
    from app.routes.weather import weather_bp
    from app.routes.frontend import frontend_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(crops_bp, url_prefix='/api/crops')
    app.register_blueprint(market_bp, url_prefix='/api/market')
    app.register_blueprint(schemes_bp, url_prefix='/api/schemes')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(frontend_bp)

    # ─── Create Tables ───────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app


def _seed_initial_data():
    """Seed initial data if tables are empty"""
    from app.models.market import MarketRate
    from app.models.scheme import GovernmentScheme
    from app.services.market_service import seed_market_data
    from app.services.scheme_service import seed_scheme_data

    if MarketRate.query.count() == 0:
        seed_market_data()

    if GovernmentScheme.query.count() == 0:
        seed_scheme_data()
