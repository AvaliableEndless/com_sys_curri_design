import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:302163@localhost:3306/community'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours 