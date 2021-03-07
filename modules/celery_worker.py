from modules import create_app, redis_client
from celery import Celery
from flask import current_app
from modules.config import ProductionConfig, DevelopmentConfig
import time
import os


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = None
if os.environ.get('FLASK_ENV') == 'production':
    celery_app = create_app(ProductionConfig())
    #async_task = make_celery(create_app(ProductionConfig()))
else:
    celery_app = create_app(DevelopmentConfig())
    #async_task = make_celery(create_app(DevelopmentConfig()))
    print("Celery in development config")


from modules.xenoChat.utils import SeemaTaparia, keep_server_alive
async_task = make_celery(celery_app)
SeemaTaparia.delay(celery_app.config['SOCKETIO_URL'])
keep_server_alive()
