from flask import request, current_app
import json
import pika
from flask_socketio import emit, disconnect
from modules import socketio, redis_client
from modules.global_utils import hash_func


@socketio.on('connect')
def Connect():
    if request.args.get('api_key') != current_app.config['CONNECT_API_KEY']:
        return False
    sid = request.sid
    print("Connected: ", sid)
    emit('authorize', 1, room=sid)


@socketio.on('disconnect')
def Disconnect():
    print("Disconnected: ", request.sid)
    if redis_client.exists(request.sid):
        redis_client.decr('connected_clients')
        user_hash = redis_client.get(request.sid).decode('utf-8')
        redis_client.delete(request.sid)
        redis_client.delete(user_hash)


@socketio.on('onlineUsers')
def onlineUsers():
    clients = redis_client.get('connected_clients').decode('utf-8')
    emit('onlineUsers', clients, room=request.sid)


@socketio.on('mapHashID')
def mapHashID(Hash):

    print("Hash: ", Hash)
    if Hash is not None:
        pika_client = pika.BlockingConnection(
            pika.URLParameters(current_app.config['MQ_URL']))
        channel = pika_client.channel()

        if redis_client.exists(Hash):
            sid = redis_client.get(Hash).decode('utf-8')
            redis_client.delete(sid)
            disconnect(sid)
        else:
            redis_client.incr('connected_clients')
        redis_client.set(request.sid, Hash)
        redis_client.set(Hash, request.sid)

        """if redis_client.hexists('NameChange', Hash):
            name_email = redis_client.hget('NameChange', Hash).decode('utf-8')
            name_email = name_email.split(' ')
            name_json = json.dumps(
                {'hashID': Hash, 'newName': name_email[1],
                 'email': name_email[0]})
            emit('nameChange', name_json, room=request.sid)
            redis_client.hdel('NameChange', Hash)"""

        queue_val = hash_func(Hash)
        all_msgs = []
        val = channel.queue_declare(queue=str(queue_val), passive=True)
        num_msgs = val.method.message_count
        if num_msgs != 0:
            for method_frame, _, body in channel.consume(str(queue_val)):
                body = body.decode('utf-8')
                user_msg = json.loads(body)
                if user_msg['friendHashID'] == Hash:
                    if user_msg['type'] != 'message':
                        emit(user_msg['type'], body, room=request.sid)
                    else:
                        all_msgs.append(user_msg)
                    channel.basic_ack(method_frame.delivery_tag)
                num_msgs = num_msgs - 1

                if num_msgs == 0:
                    break

            if len(all_msgs) != 0:
                all_msgs = json.dumps(all_msgs)
                emit('unread', all_msgs, room=request.sid)
        channel.close()
