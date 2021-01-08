from modules import redis_client,REDIS_URL
from flask_socketio import SocketIO
from modules import async_task
from flask import request,current_app
import time


async_task = Celery(current_app.name,broker=REDIS_URL)
socket = SocketIO(message_queue=REDIS_URL)

@async_task.task()
def Wait(Hash):
    while redis_client.ttl('matchqueue') != -1 and redis_client.ttl('matchqueue') != -2:
        continue
    print("out of while")
    print(redis_client.ttl('matchqueue'))

    if redis_client.ttl('matchqueue') == -2:
        redis_client.decr('match_queue_count')
        socket.emit('matchCancel',Hash,room=redis_client.get(Hash))

@async_task.task()
def tryCheck():
    while 1:
        time.sleep(5)
        print("Celery value")