from flask import Flask,current_app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from modules.config import ProductionConfig
from flask_marshmallow import Marshmallow
from celery import Celery
import time
from flask_redis import FlaskRedis
import pika
import os

socketio = SocketIO()
db = SQLAlchemy()
mail = Mail()
ma = Marshmallow()
redis_client = FlaskRedis()


def create_app(config_class):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    if os.environ.get('FLASK_ENV') == 'development':
        with app.app_context():
            db.create_all()
            db.session.commit()

    mail.init_app(app)
    ma.init_app(app)
    print(app.config['SOCKETIO_URL'])
    socketio.init_app(app,cors_allowed_origins="*",message_queue=app.config['SOCKETIO_URL'],async_mode='eventlet')
    redis_client.init_app(app)

    redis_client.set('match_queue_count',0)

    from modules.main import main
    from modules.authentication import authentication
    from modules.chat import chat
    from modules.xenoChat import xenoChat
    from modules.dashboard import dashboard
    from modules.block import block
    from modules.feedbackAndChanges import feedbackAndChanges

    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.register_blueprint(chat)
    app.register_blueprint(xenoChat)
    app.register_blueprint(dashboard)
    app.register_blueprint(block)
    app.register_blueprint(feedbackAndChanges)

    return app
