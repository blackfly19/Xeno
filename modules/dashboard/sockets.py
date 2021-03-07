from flask_socketio import emit
from flask import current_app
from modules import socketio, redis_client, db
import pika
from modules.global_utils import hash_func, messageHandler
from modules.models import User
import json
import time


@socketio.on('dashBroadcast')
def broadcast(message):
    print(message)
    users = User.query.all()
    #jsons = []
    for user in users:
        if user.hashID != "42424242424242424242424242424242":
            msg = {'id': int(time.time() * 1000), 'type': 'message',
                   "userHashID": "42424242424242424242424242424242",
                   "friendHashID": user.hashID, "content": message}
            json_msg = json.dumps(msg)
            messageHandler(message_json=json_msg, message=msg)
            # jsons.append(json_msg)

    """for i, user in enumerate(users):
        receiver = redis_client.get(user.hashID)
        if receiver is None:
            pika_client = pika.BlockingConnection(
                pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(user.hashID)
            # channel.queue_declare(queue=str(queue_val))
            channel.basic_publish(
                exchange='', routing_key=str(queue_val), body=jsons[i])
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit('message', jsons[i], room=receiver)"""


@socketio.on('dashNameChangeAccepted')
def nameChangeAccepted(name_json):
    data = json.loads(name_json)
    message = """Your request for name change has been processed
                 successfully. Your new name {}.""".format(data['newName'])
    user_obj = User.query.filter_by(email=data['email']).first()
    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": user_obj.hashID, "content": message}
    json_msg = json.dumps(msg)
    user_obj.username = data['newName']
    receiver = messageHandler(message_json=json_msg, message=msg)
    if receiver is None:
        redis_client.hset('NameChange', user_obj.hashID,
                          data['email']+' '+data['newName'])
    else:
        data['hashID'] = user_obj.hashID
        name_json = json.dumps(data)
        emit('nameChange', name_json, room=receiver)
    db.session.commit()

    for friend in user_obj.friends:
        friend_msg = {'type': 'nameChange',
                      "userHashID": user_obj.hashID,
                      "friendHashID": friend.friend_hashID,
                      "content": data['newName']}
        friend_msg_json = json.dumps(friend_msg)
        messageHandler(message_json=friend_msg_json, message=friend_msg)


@socketio.on('dashNameChangeDenied')
def nameChangeDenied(name_json):
    data = json.loads(name_json)
    message = "Your request for name change couldn't be processed, as the name you requested doesn't match the official records. If you believe this is an error from our end, please drop us a feedback regarding this."
    user_obj = User.query.filter_by(email=data['email']).first()
    msg = {'id': int(time.time() * 1000), "userHashID": "42424242424242424242424242424242",
           "friendHashID": user_obj.hashID, "content": message}
    json_msg = json.dumps(msg)
    messageHandler(message_json=json_msg, message=msg)
