from modules import socketio, redis_client, db
from flask import request
from flask_socketio import emit
from modules.global_utils import transactionFail
import json
from modules.models import FriendList


@socketio.on('matchQueue')
def match(Hash):

    redis_client.rpush('matchqueue', Hash)
    redis_client.incr('match_queue_count')


@socketio.on('xenoMessage')
def xenoMessage(message):
    msg = json.loads(message)
    emit('xenoReceipt', msg['id'], room=request.sid)
    receiver = redis_client.get(msg['friendHashID'])
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('xenoMessage', message, room=receiver)
    else:
        emit('xenoLeft', msg['friendHashID'], room=request.sid)


@socketio.on('addOwnFirst')
def firstTimer(timer_data):
    data = json.loads(timer_data)
    receiver = redis_client.get(data['friendHashID'])
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('addOwnFirst', timer_data, room=receiver)
    else:
        emit('xenoLeft', data['friendHashID'], room=request.sid)


@socketio.on('addOwnSecond')
def SecondTimer(timer_data):
    data = json.loads(timer_data)
    receiver = redis_client.get(data['friendHashID'])
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('addOwnSecond', timer_data, room=receiver)
    else:
        emit('xenoLeft', data['friendHashID'], room=request.sid)


@socketio.on('revealConsent')
def consent(data):
    json_data = json.loads(data)
    Hash = json_data['friendHashID']
    receiver = redis_client.get(Hash)
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('revealConsent', data, room=receiver)
    else:
        emit('xenoLeft', data['friendHashID'], room=request.sid)


@socketio.on('revealFinal')
@transactionFail
def final(data):
    json_data = json.loads(data)
    user_receiver = redis_client.get(json_data['userHashID'])
    friend_receiver = redis_client.get(json_data['friendHashID'])
    user_receiver = user_receiver.decode('utf-8')
    friend_receiver = friend_receiver.decode('utf-8')
    if json_data['ownConsent'] is True and json_data['xenoConsent'] is True:
        user_friend = FriendList(user_hashID=json_data['userHashID'],
                                 friend_hashID=json_data['friendHashID'])
        friend_user = FriendList(user_hashID=json_data['friendHashID'],
                                 friend_hashID=json_data['userHashID'])
        db.session.add(user_friend)
        db.session.add(friend_user)
        db.session.commit()
        emit('revealFinal', True, room=user_receiver)
        emit('revealFinal', True, room=friend_receiver)
    else:
        emit('revealFinal', False, room=user_receiver)
        emit('revealFinal', False, room=friend_receiver)

    redis_client.hdel('sessions', user_receiver)
    redis_client.hdel('sessions', friend_receiver)


@socketio.on('xenoLeft')
def xenoLeft(friendHashID):
    sender = redis_client.get(request.sid).decode('utf-8')
    receiver = redis_client.get(friendHashID)
    if receiver is not None:
        receiver = receiver.decode('utf-8')
        emit('xenoLeft', sender, room=receiver)


@socketio.on('notifyMe')
def notifyMe(hashID):

    redis_client.rpush('notifyMe', hashID)
