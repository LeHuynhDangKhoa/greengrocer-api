import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    # SECRET_KEY = '57e19ea558d4967a552d03deece34a70'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_AVATAR = "images/avatar/" 
    UPLOAD_PRODUCT = "images/product/" 

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL')

class DevelopmentConfig(Config):
    ENV="development"
    DEVELOPMENT=True
    DEBUG=True
    DATABASE_URL="host=db.tdibbpoblindfigtbcqo.supabase.co user=postgres password=flask_postgres_20521025 dbname=postgres port=6543"