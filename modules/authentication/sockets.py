import json
import time
from flask import request, current_app, render_template
from .utils import get_confirm_token
from modules import db, mail, socketio, redis_client
from modules.models import User
from modules.global_utils import hash_func, messageHandler, face_verify, convert_base64_to_url, transactionFail
from flask_mail import Message
from flask_socketio import emit
from modules.messages import welcome_msg_1, welcome_msg_2
import pika


@socketio.on('newUser')
@transactionFail
def newUser(new_data):
    data = json.loads(new_data)
    url = convert_base64_to_url(data['dpBase64'], data['hashID'])
    print(url)
    if data['email'] == 'xeno.test434@learner.manipal.edu':
        new_user = User(hashID=data['hashID'], username=data['name'],
                        email=data['email'], notif_token=data['token'],
                        phone=data['phone'], verified=True, imageUrl=url,
                        interest_1=data['interests'][0],
                        interest_2=data['interests'][1],
                        interest_3=data['interests'][2])
    else:
        new_user = User(hashID=data['hashID'], username=data['name'],
                        email=data['email'], notif_token=data['token'],
                        phone=data['phone'], verified=False, imageUrl=url,
                        interest_1=data['interests'][0],
                        interest_2=data['interests'][1],
                        interest_3=data['interests'][2])
    try:
        new_user.interest_4 = data['interests'][3]
    except IndexError:
        new_user.interest_4 = None
    try:
        new_user.interest_5 = data['interests'][4]
    except IndexError:
        new_user.interest_5 = None
    db.session.add(new_user)
    db.session.commit()

    emit('authSucess', True, room=request.sid)

    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": data['hashID'], "content": welcome_msg_1}
    msg = json.dumps(msg)
    emit('message', msg, room=request.sid)

    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": data['hashID'], "content": welcome_msg_2}
    msg = json.dumps(msg)
    emit('message', msg, room=request.sid)

    msg = Message('Xeno', sender='support@getxeno.in',
                  recipients=[data['email']])
    msg.html = render_template(
        'email.html', name=data['name'],
        url="https://www.getxeno.in/token/"+get_confirm_token(data['hashID']))
    mail.send(msg)

    redis_client.set(request.sid, data['hashID'])
    redis_client.set(data['hashID'], request.sid)
    clients = redis_client.incr('connected_clients')
    emit('onlineUsers', clients-1, broadcast=True)
    pika_client = pika.BlockingConnection(
        pika.URLParameters(current_app.config['MQ_URL']))
    channel = pika_client.channel()
    queue_val = hash_func(data['hashID'])
    channel.queue_declare(queue=str(queue_val))
    channel.close()


@socketio.on('deleteUser')
@transactionFail
def deleteUser(delete_json):
    data = json.loads(delete_json)
    user = User.query.filter_by(email=data['email']).first()
    db.session.delete(user)
    db.session.commit()

    if redis_client.exists(request.sid):
        clients = redis_client.decr('connected_clients')
        emit('onlineUsers', clients, broadcast=True)
        user_hash = redis_client.get(request.sid).decode('utf-8')
        redis_client.delete(request.sid)
        redis_client.delete(user_hash)

    msg = Message('Delete', sender='support@getxeno.in',
                  recipients=['support@getxeno.in'])
    msg.body = 'Email: '+data['email'] + '\n\nReason: ' + data['content'] + \
        '\n\nDevice: ' + data['device'] + '\nOS: ' + \
        data['os'] + '\nApp Version: ' + data['appV']
    mail.send(msg)

    delete_msg = "Your friend {} has deleted their account".format(user.username)
    for friend in user.friends:
        friend_delete_msg = {'type': 'deleteFriend',
                             "userHashID": user.hashID,
                             "friendHashID": friend.friend_hashID,
                            }
        friend_msg = {'type': 'message',
                      "userHashID": "42424242424242424242424242424242",
                      "friendHashID": friend.friend_hashID,
                      "content": delete_msg}
        friend_delete_msg_json = json.dumps(friend_delete_msg)
        friend_msg_json = json.dumps(friend_msg)
        messageHandler(message_json=friend_delete_msg_json,
                       message=friend_delete_msg)
        messageHandler(message_json=friend_msg_json,
                       message=friend_msg)


@socketio.on('validatePhone')
def validatePhone(Phone):
    user = User.query.filter_by(phone=Phone).first()
    if user is None:
        emit('validatePhone', True)
    else:
        emit('validatePhone', False)


@socketio.on('validateEmail')
def validateEmail(Email):
    user = User.query.filter_by(email=Email).first()
    if user is None:
        emit('validateEmail', True)
    else:
        emit('validateEmail', False)


@socketio.on('isEmailVerified')
def isEmailVerified(hashID):
    user = User.query.filter_by(hashID=hashID).first()
    if user.verified is True:
        data = {'hashID': hashID}
        data_json = json.dumps(data)
        receiver = redis_client.get(hashID).decode('utf-8')
        emit('emailVerified', data_json, room=receiver)
        message = "Your email has been verified successfully!"
        msg = {'id': int(time.time() * 1000), 'type': 'message',
               "userHashID": "42424242424242424242424242424242",
               "friendHashID": user.hashID, "content": message}
        json_msg = json.dumps(msg)
        messageHandler(message_json=json_msg, message=msg)


@socketio.on('imageForVerification')
def ImageVerification(data):
    image_data = json.loads(data)
    user = User.query.filter_by(hashID=image_data['hashID']).first()
    face_verify_result = face_verify(user.imageUrl, image_data['base64'])
    result = {'type': 'picVerified',
              "userHashID": "42424242424242424242424242424242",
              'friendHashID': image_data['hashID'],
              'content': face_verify_result}
    result_json = json.dumps(result)
    if face_verify_result is True:
        message = "Your image has been verified"
    else:
        message = "Your image didn't match. Please try again"
    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": user.hashID, "content": message}
    json_msg = json.dumps(msg)
    messageHandler(message_json=json_msg, message=msg)
    messageHandler(message_json=result_json, message=result)
