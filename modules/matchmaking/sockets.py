from modules import socketio,redis_client
from modules.models import User
from flask_socketio import emit
from .utils import Wait
import json
import time

@socketio.on('matchQueue')
def match(Hash):

    redis_client.rpush('matchqueue',Hash)
    redis_client.incr('match_queue_count')

    if int(redis_client.get('match_queue_count').decode('utf-8')) == 1:
        redis_client.expire('matchqueue',20)
        Wait.delay(Hash)

    while int(redis_client.get('match_queue_count').decode('utf-8')) > 1:

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
            redis_client.rpush('matchqueue',hash_user1)
            redis_client.incr('match_queue_count')
            redis_client.expire('matchqueue',15)
            break

        hash_user2 = redis_client.lpop('matchqueue')
        while redis_client.exists(hash_user2) != True:
            if redis_client.exists('matchqueue') == False:
                redis_client.rpush('matchqueue',hash_user1)
                redis_client.incr('match_queue_count')
                redis_client.expire('matchqueue',15)
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

        #redis_client.decrby('match_queue_count',2)

        user1 = User.query.filter_by(hashID=hash_user1).first()
        user2 = User.query.filter_by(hashID=hash_user2).first()

        user1_json = json.dumps({'name':user1.username,'hashID':hash_user1,'imageUrl':user1.imageUrl})
        user2_json = json.dumps({'name':user2.username,'hashID':hash_user2,'imageUrl':user2.imageUrl})
        
        #json - dp url,name, hashid,interest list
        emit('xenoHashID',user1_json,room=redis_client.get(hash_user2).decode('utf-8'))
        emit('xenoHashID',user2_json,room=redis_client.get(hash_user1).decode('utf-8'))

@socketio.on('matchCancel')
def cancel(Hash):
    redis_client.hset('cancel',Hash,1)

@socketio.on('addOwnFirst')
def firstTimer(timer_data):
    print('First timer')
    data = json.loads(timer_data)
    receiver = redis_client.get(data['friendHashID'])
    receiver = receiver.decode('utf-8')
    emit('addOwnFirst',timer_data,room=receiver)

@socketio.on('addOwnSecond')
def firstTimer(timer_data):
    print('Second timer')
    data = json.loads(timer_data)
    receiver = redis_client.get(data['friendHashID'])
    receiver = receiver.decode('utf-8')
    emit('addOwnSecond',timer_data,room=receiver)

@socketio.on('revealConsent')
def consent(data):
    print('RevealConsent')
    json_data = json.loads(data)
    Hash = json_data['friendHashID']
    receiver = redis_client.get(Hash)
    print(receiver)
    receiver = receiver.decode('utf-8')
    emit('revealConsent',data,room=receiver)

@socketio.on('revealFinal')
def final(data):
    print('RevealFinal')
    json_data = json.loads(data)
    user_receiver = redis_client.get(json_data['userHashID'])
    friend_receiver = redis_client.get(json_data['friendHashID'])
    user_receiver = user_receiver.decode('utf-8')
    friend_receiver = friend_receiver.decode('utf-8')
    print(user_receiver)
    print(friend_receiver)
    if json_data['ownConsent'] == True and json_data['xenoConsent'] == True:
        emit('revealFinal',True,room=user_receiver)
        emit('revealFinal',True,room=friend_receiver)
    else:
        emit('revealFinal',False,room=user_receiver)
        emit('revealFinal',False,room=friend_receiver)



