import os

class Config(object):
    """
    Thông tin cấu hình chung
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_AVATAR = "images/avatar/" 
    UPLOAD_PRODUCT = "images/product/" 

class ProductionConfig(Config):
    """
    Thông tin cấu hình cho môi trường product
    """
    DEBUG = False
    # DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASE_URL="host=db.tdibbpoblindfigtbcqo.supabase.co user=postgres password=flask_postgres_20521025 dbname=postgres port=6543"

class DevelopmentConfig(Config):
    """
    Thông tin cấu hình cho môi trường development
    """
    ENV="development"
    DEVELOPMENT=True
    DEBUG=True
    DATABASE_URL="host=db.tdibbpoblindfigtbcqo.supabase.co user=postgres password=flask_postgres_20521025 dbname=postgres port=6543"