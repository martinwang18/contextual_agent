"""
Contextual Agent - Main Flask Application
Provides API endpoints for contextual information retrieval
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

from api.routes import api_bp
from utils.config import Config

# Load environment variables
load_dotenv('config/.env')

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Load configuration
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/')
def index():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '0.1.0'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    print(f"\n{'='*60}")
    print(f"🚀 Contextual Agent Server Starting...")
    print(f"{'='*60}")
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
