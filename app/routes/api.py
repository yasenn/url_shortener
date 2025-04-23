from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.url_shortener import URLShortener
from app.storage.postgresql import PostgreSQLURLStorage

api_bp = Blueprint('api', __name__)
storage = PostgreSQLURLStorage()
shortener = URLShortener(storage)

@api_bp.route('/api/shorten', methods=['POST'])
@jwt_required()
def api_shorten():
    current_user = get_jwt_identity()
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    original_url = data['url']
    
    try:
        short_code = shortener.shorten_url(original_url, current_user['username'])
        short_url = f"{request.host_url}{short_code}"
        
        return jsonify({
            'short_url': short_url,
            'original_url': original_url,
            'short_code': short_code
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Log the error here
        return jsonify({'error': 'Internal server error'}), 500

