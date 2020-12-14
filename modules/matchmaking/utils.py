from modules import redis_client,REDIS_URL
from flask_socketio import emit
from celery import Celery 

async_task = Celery('tasks',broker=REDIS_URL)


@async_task.task()
def Wait():
    while redis_client.ttl('matchqueue') != -1 and redis_client.ttl('matchqueue') != -2:
        print("In while")
        continue
    print("out of while")

    if redis_client.ttl('matchqueue') == -2:
        emit('matchCancel',1)