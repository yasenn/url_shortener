from flask import Blueprint, render_template, request, redirect, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_csrf_token
from app.services.url_shortener import URLShortener
from app.storage.postgresql import PostgreSQLURLStorage
from app.services.kafka_service import KafkaClickProducer
import datetime,os

web_bp = Blueprint('web', __name__)
storage = PostgreSQLURLStorage()
shortener = URLShortener(storage)

click_producer = KafkaClickProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
)

@web_bp.route('/favicon.ico')
def favicon():
    return '', 404

@web_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@web_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@web_bp.route('/')
def index():
    encoded_token = request.cookies.get('access_token_cookie')
    csrf_token = get_csrf_token(encoded_token) if encoded_token else ''
    return render_template('index.html', csrf_token=csrf_token)

@web_bp.route('/shorten', methods=['POST'])
@jwt_required()
def handle_shorten():
    current_user = get_jwt_identity()
    original_url = request.form.get('url')
    if not original_url:
        return "Missing URL", 400
    
    short_code = shortener.shorten_url(original_url, current_user['username'])
    short_url = request.host_url + short_code
    return render_template('result.html', short_url=short_url)

@web_bp.route('/<short_code>')
def redirect_to_original(short_code):
    original_url = shortener.get_original_url(short_code)
    if original_url:
        click_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'ip': request.remote_addr
        }
        click_producer.send_click_event(short_code, click_data)
        return redirect(original_url)
    return "URL not found", 404

@web_bp.route('/stats')
@jwt_required()
def user_stats():
    current_user = get_jwt_identity()
    target_user = current_user['username']
    
    if current_user['role'] == 'admin' and 'username' in request.args:
        target_user = request.args.get('username')
        if target_user not in users:
            if request.accept_mimetypes.accept_json:
                return jsonify({'error': 'User not found'}), 404
            return render_template('stats.html', error='User not found'), 404
    
    user_urls = storage.get_urls_by_user(target_user)
    stats = [{
        'short_code': url['short_code'],
        'original_url': url['original_url'],
        'clicks': len(url['clicks'])
    } for url in user_urls]
    
    if request.accept_mimetypes.accept_json:
        return jsonify({'stats': stats, 'user': target_user})
    
    return render_template('stats.html', 
                         stats=stats,
                         username=target_user,
                         is_admin=(current_user['role'] == 'admin'))



@web_bp.route('/api/stats', methods=['GET'])
@jwt_required()
def api_stats():
    current_user = get_jwt_identity()
    target_user = current_user['username']
    
    if current_user['role'] == 'admin' and 'username' in request.args:
        target_user = request.args.get('username')
        if target_user not in users:
            return jsonify({'error': 'User not found'}), 404
    
    user_urls = storage.get_urls_by_user(target_user)
    stats = [{
        'short_code': url['short_code'],
        'original_url': url['original_url'],
        'clicks': len(url['clicks']),
        'click_details': url['clicks']
    } for url in user_urls]
    
    return jsonify({'stats': stats, 'user': target_user})