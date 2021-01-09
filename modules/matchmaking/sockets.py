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

#@socketio.on('matchCancel')
#def cancel(Hash):
#    redis_client.hset('cancel',Hash,1)

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

@socketio.on('syncTime')
def syncTimers():
    emit('syncTime',time.time()*1000)



