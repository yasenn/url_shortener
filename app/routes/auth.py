from flask import Blueprint, render_template, request, redirect
from flask_jwt_extended import create_access_token, set_access_cookies
from app.models.user import User

auth_bp = Blueprint('auth', __name__)
user_manager = User()

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('register.html', error='Missing username or password')
    
    if not user_manager.create_user(username, password):
        return render_template('register.html', error='Username already exists')
    
    return redirect('/login')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = user_manager.get_user(username)
    if not user or not user_manager.verify_password(user, password):
        return render_template('login.html', error='Invalid credentials'), 401
    
    access_token = create_access_token(identity={
        'username': username,
        'role': user['role']
    })
    response = redirect('/')
    set_access_cookies(response, access_token)
    
    return response