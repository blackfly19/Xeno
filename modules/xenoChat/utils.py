from modules import redis_client, db
from flask_socketio import SocketIO
from modules.celery_worker import async_task
import time
from modules.models import User, Block
import json
import socketio
import os


def checkBlock(hash_user1, hash_user2):
    hash_user1 = hash_user1.decode('utf-8')
    hash_user2 = hash_user2.decode('utf-8')
    check_block = Block.query.filter_by(
        blocker_hashID=hash_user1, blockee_hashID=hash_user2).first()
    check_block = Block.query.filter_by(
        blocker_hashID=hash_user2, blockee_hashID=hash_user1).first()
    return check_block


@async_task.task()
def Wait(socketio_url):

    socket = SocketIO(message_queue=socketio_url)
    Hash = redis_client.lindex('matchqueue', 0)
    Hash = Hash.decode('utf-8')
    while redis_client.ttl('matchqueue') != -1 and redis_client.ttl('matchqueue') != -2:
        continue
    print("out of while")
    print(redis_client.ttl('matchqueue'))

    if redis_client.ttl('matchqueue') == -2:
        redis_client.decr('match_queue_count')
        receiver = redis_client.get(Hash).decode('utf-8')
        socket.emit('matchCancel', Hash, room=receiver)


@async_task.task()
def SeemaTaparia(socketio_url):
    socket = SocketIO(message_queue=socketio_url)
    while 1:

        if int(redis_client.get('match_queue_count').decode('utf-8')) == 1:
            if redis_client.ttl('matchqueue') == -1:
                redis_client.expire('matchqueue', 20)
                Wait.delay(socketio_url)

        while int(redis_client.get('match_queue_count').decode('utf-8')) > 1:

            if redis_client.ttl('matchqueue') != -1:
                redis_client.persist('matchqueue')
                time.sleep(1)

            hash_user1 = redis_client.lpop('matchqueue')
            while redis_client.exists(hash_user1) != True:
                if redis_client.exists('matchqueue') == False:
                    break
                hash_user1 = redis_client.lpop('matchqueue')
                redis_client.decr('match_queue_count')
            redis_client.decr('match_queue_count')

            if redis_client.exists('matchqueue') == False:
                print('Is None')
                redis_client.rpush('matchqueue', hash_user1)
                redis_client.incr('match_queue_count')
                break

            hash_user2 = redis_client.lpop('matchqueue')
            while redis_client.exists(hash_user2) != True:
                if redis_client.exists('matchqueue') == False:
                    redis_client.rpush('matchqueue', hash_user1)
                    redis_client.incr('match_queue_count')
                    hash_user2 = None
                    break
                hash_user2 = redis_client.lpop('matchqueue')
                redis_client.decr('match_queue_count')
            redis_client.decr('match_queue_count')

            if hash_user2 is None:
                break

            print(hash_user1)
            print(hash_user2)

            hash_user1 = hash_user1.decode('utf-8')
            hash_user2 = hash_user2.decode('utf-8')

            db.session.commit()

            user1 = User.query.filter_by(hashID=hash_user1).first()
            user2 = User.query.filter_by(hashID=hash_user2).first()

            user1_json = json.dumps({'name': user1.username, 'hashID': hash_user1, 'imageUrl': user1.imageUrl,
                                     'interests': [user1.interest_1, user1.interest_2, user1.interest_3, user1.interest_4, user1.interest_5]})
            user2_json = json.dumps({'name': user2.username, 'hashID': hash_user2, 'imageUrl': user2.imageUrl,
                                     'interests': [user2.interest_1, user2.interest_2, user2.interest_3, user2.interest_4, user2.interest_5]})

            socket.emit('xenoHashID', user1_json,
                        room=redis_client.get(hash_user2).decode('utf-8'))
            socket.emit('xenoHashID', user2_json,
                        room=redis_client.get(hash_user1).decode('utf-8'))

            print('values emitted')


@async_task.task()
def keep_server_alive():
    sio = socketio.Client()
    while 1:
        time.sleep(300)
        sio.connect('https://xeno-1.herokuapp.com?api_key='+os.environ.get('CONNECT_API_KEY'))
        sio.disconnect()
