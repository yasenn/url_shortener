from werkzeug.security import generate_password_hash, check_password_hash
from app.storage.app_storage import PostgreSQLUserStorage

class User:
    def __init__(self):
        self.storage = PostgreSQLUserStorage()

    def create_user(self, username, password, role='user'):
        password_hash = generate_password_hash(password)
        return self.storage.create_user(username, password_hash, role)

    def get_user(self, username):
        return self.storage.get_user(username)

    def verify_password(self, user, password):
        return check_password_hash(user['password_hash'], password)