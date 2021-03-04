from modules import create_app,redis_client
from celery import Celery
from modules.config import ProductionConfig,DevelopmentConfig
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

if os.environ.get('FLASK_ENV') == 'production':
    async_task = make_celery(create_app(ProductionConfig()))
else:
    async_task = make_celery(create_app(DevelopmentConfig()))
    print("Celery in development config")

from modules.xenoChat.utils import SeemaTaparia
SeemaTaparia.delay()
