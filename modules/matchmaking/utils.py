from modules import redis_client,REDIS_URL
from flask_socketio import SocketIO
from celery import Celery 
from flask import request

async_task = Celery('tasks',broker=REDIS_URL)
socket = SocketIO(message_queue=REDIS_URL)

@async_task.task()
def Wait(Hash):
    while redis_client.ttl('matchqueue') != -1 and redis_client.ttl('matchqueue') != -2:
        continue
    print("out of while")

    if redis_client.ttl('matchqueue') == -2:
        redis_client.decr('match_queue_count')
        socket.emit('matchCancel',1,room=redis_client.get(Hash))