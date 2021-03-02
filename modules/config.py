import os

class Config:

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    CONNECT_API_KEY = os.environ.get('CONNECT_API_KEY')

class DevelopmentConfig(Config):

    DEBUG = True
    TESTING = True
    SECRET_KEY = "Not a secret anymore"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory"
    CELERY_BROKER_URL = "redis://127.0.0.1"
    REDIS_URL = "redis://127.0.0.1"
    MQ_URL = "amqp://guest:guest@localhost:5672/%2F"

class ProductionConfig(Config):

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    MQ_URL = os.environ.get('CLOUDAMQP_URL')


