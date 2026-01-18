from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def root():
    return jsonify({
        'message': 'Welcome to AI Backend API',
        'version': '1.0.0',
        'status': 'running',
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/items', methods=['GET'])
def get_items():
    items = [
        {'id': 1, 'name': 'Item 1', 'description': 'First example item'},
        {'id': 2, 'name': 'Item 2', 'description': 'Second example item'},
        {'id': 3, 'name': 'Item 3', 'description': 'Third example item'}
    ]
    return jsonify({'items': items, 'count': len(items)}), 200

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    items = {
        1: {'id': 1, 'name': 'Item 1', 'description': 'First example item'},
        2: {'id': 2, 'name': 'Item 2', 'description': 'Second example item'},
        3: {'id': 3, 'name': 'Item 3', 'description': 'Third example item'}
    }

    item = items.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    return jsonify(item), 200

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    new_item = {
        'id': 4,
        'name': data['name'],
        'description': data.get('description', 'No description provided'),
        'created_at': datetime.utcnow().isoformat()
    }

    logger.info(f"Created new item: {new_item}")
    return jsonify(new_item), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
