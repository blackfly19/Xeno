from modules import create_app,redis_client
from celery import Celery
import time

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

async_task = make_celery(create_app())


from modules.matchmaking.utils import SeemaTaparia,keep_redis_active
SeemaTaparia.delay()
keep_redis_active.delay()
