from modules import async_task,redis_client
from flask_socketio import emit

@async_task.task()
def Wait():
    while redis_client.ttl('matchqueue') != -1 and redis_client.ttl('matchqueue') != -2:
        print("In while")
        continue
    print("out of while")

    if redis_client.ttl('matchqueue') == -2:
        emit('matchCancel',1)