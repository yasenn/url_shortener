import os

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY','some_other key') # default value should not be used, but i decided to leave it just in case
    JWT_TOKEN_LOCATION = ['cookies']
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True 