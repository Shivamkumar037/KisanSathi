from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .models import db

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Upload folder
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # ==================== ALL BLUEPRINTS ====================
    from .routes.auth import auth_bp
    from .routes.home import home_bp
    from .routes.analysis import analysis_bp
    from .routes.community import community_bp
    from .routes.chat import chat_bp
    from .routes.voice import voice_bp
    from .routes.schemes import schemes_bp
    from .routes.market import market_bp
    from .routes.profile import profile_bp
    from .routes.frontend import frontend_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(home_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    app.register_blueprint(schemes_bp, url_prefix='/api/schemes')
    app.register_blueprint(market_bp, url_prefix='/api/market')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(frontend_bp)   # yeh sab HTML pages ke liye hai
    
    # Database recreate (dev mode ke liye safe)
    with app.app_context():
        db.drop_all()      # purana table delete
        db.create_all()    # naya table with is_admin column ke saath
    
    return app