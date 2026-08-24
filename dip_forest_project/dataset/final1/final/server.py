import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///studysphere.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-flask-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For development

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Import models after db initialization
from models import User, Subject, StudySession, AudioNote

# Import and register blueprints
from auth import auth_bp
from subjects import subjects_bp
from sessions import sessions_bp
from audio import audio_bp
from ai import ai_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(subjects_bp, url_prefix='/api/subjects')
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
app.register_blueprint(audio_bp, url_prefix='/api/audio')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Configure CORS AFTER registering blueprints
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
     expose_headers=["Content-Type", "Authorization"])

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {'error': 'Internal server error'}, 500

# Health check endpoint
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'StudySphere API is running'}

# --- THIS IS THE CORRECTED BLOCK ---
# Create database tables within the application context.
# This replaces the outdated @app.before_first_request decorator.
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)

