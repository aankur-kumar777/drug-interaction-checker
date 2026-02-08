"""
Main Flask Application for Drug Interaction Checker
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from routes import api_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend communication
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            'name': 'Drug Interaction Checker API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'check_interactions': '/api/check-interactions',
                'get_drug': '/api/drug/<name>',
                'get_alternatives': '/api/alternatives/<drug>',
                'search': '/api/search',
                'visualize': '/api/visualize'
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info('Starting Drug Interaction Checker API...')
    app.run(host='0.0.0.0', port=5000, debug=True)
