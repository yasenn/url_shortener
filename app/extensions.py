from flask_jwt_extended import JWTManager
from flask import redirect, url_for

jwt = JWTManager()

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    response = redirect(url_for('web.login_page'))
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('csrf_access_token')
    return response

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = redirect(url_for('web.login_page'))
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('csrf_access_token')
    return response

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    response = redirect(url_for('web.login_page'))
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('csrf_access_token')
    return response