from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Logging
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
    return {'error': 'Not found', 'message': str(error)}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return {'error': 'Internal server error'}, 500

# -------------------------
# Swagger / API Docs
# -------------------------
api = Api(
    app,
    version="1.0",
    title="AI Backend API",
    description="Auto-generated API documentation for AI Backend",
    doc="/docs"  # Swagger UI at /docs
)

# Root and health namespace
ns_root = api.namespace('', description='Root & Health endpoints')
ns_items = api.namespace('items', description='Item operations', path='/api/items')

# -------------------------
# Models for Swagger
# -------------------------
item_model = api.model('Item', {
    'id': fields.Integer(readOnly=True, description='Item ID'),
    'name': fields.String(required=True, description='Item name'),
    'description': fields.String(description='Item description'),
    'created_at': fields.String(description='Item creation timestamp')
})

item_list_model = api.model('ItemList', {
    'items': fields.List(fields.Nested(item_model)),
    'count': fields.Integer(description='Number of items')
})

# -------------------------
# Root & health endpoints
# -------------------------
@ns_root.route('/')
class Root(Resource):
    def get(self):
        """Root endpoint - system info"""
        return {
            'message': 'Welcome to AI Backend API',
            'version': '1.0.0',
            'status': 'running',
            'environment': os.environ.get('ENVIRONMENT', 'development'),
            'timestamp': datetime.utcnow().isoformat()
        }

@ns_root.route('/health')
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200

# -------------------------
# Items endpoints
# -------------------------
@ns_items.route('/')
class ItemList(Resource):
    @ns_items.marshal_with(item_list_model)
    def get(self):
        """Get all items"""
        items = [
            {'id': 1, 'name': 'Item 1', 'description': 'First example item'},
            {'id': 2, 'name': 'Item 2', 'description': 'Second example item'},
            {'id': 3, 'name': 'Item 3', 'description': 'Third example item'}
        ]
        return {'items': items, 'count': len(items)}

    @ns_items.expect(item_model, validate=True)
    @ns_items.marshal_with(item_model, code=201)
    def post(self):
        """Create a new item"""
        data = request.json
        new_item = {
            'id': 4,
            'name': data['name'],
            'description': data.get('description', 'No description provided'),
            'created_at': datetime.utcnow().isoformat()
        }
        logger.info(f"Created new item: {new_item}")
        return new_item, 201

@ns_items.route('/<int:item_id>')
@ns_items.param('item_id', 'The item identifier')
class Item(Resource):
    @ns_items.marshal_with(item_model)
    def get(self, item_id):
        """Get a single item by ID"""
        items = {
            1: {'id': 1, 'name': 'Item 1', 'description': 'First example item'},
            2: {'id': 2, 'name': 'Item 2', 'description': 'Second example item'},
            3: {'id': 3, 'name': 'Item 3', 'description': 'Third example item'}
        }
        item = items.get(item_id)
        if not item:
            api.abort(404, f"Item {item_id} not found")
        return item

# -------------------------
# Run server
# -------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
