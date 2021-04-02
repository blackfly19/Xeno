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
    mainSid = request.sid
    disconnect(mainSid)
    print("Disconnected: ", mainSid)
    if redis_client.exists(mainSid):
        clients = redis_client.decr('connected_clients')
        emit('onlineUsers', clients-1, broadcast=True)
        user_hash = redis_client.get(mainSid).decode('utf-8')
        if redis_client.hexists('sessions', mainSid):
            sid = redis_client.hget('sessions', mainSid)
            sid = sid.decode('utf-8')
            emit('xenoLeft', user_hash, room=sid)
            redis_client.hdel('sessions', mainSid)
            redis_client.hdel('sessions', sid)
        redis_client.delete(mainSid)
        redis_client.delete(user_hash)


@socketio.on('onlineUsers')
def onlineUsers():
    clients = redis_client.get('connected_clients').decode('utf-8')
    emit('onlineUsers', int(clients)-1, broadcast=True)


@socketio.on('mapHashID')
def mapHashID(Hash):

    print("Hash: ", Hash)
    if Hash is not None:
        if redis_client.exists(Hash):
            sid = redis_client.get(Hash).decode('utf-8')
            redis_client.delete(sid)
            disconnect(sid)
        else:
            clients = redis_client.incr('connected_clients')
            emit('onlineUsers', clients-1, broadcast=True)
        redis_client.set(request.sid, Hash)
        redis_client.set(Hash, request.sid)

        pika_client = pika.BlockingConnection(
            pika.URLParameters(current_app.config['MQ_URL']))
        channel = pika_client.channel()

        queue_val = hash_func(Hash)
        #all_msgs = []
        val = channel.queue_declare(queue=str(queue_val), passive=True)
        num_msgs = val.method.message_count
        if num_msgs != 0:
            for method_frame, _, body in channel.consume(str(queue_val)):
                body = body.decode('utf-8')
                user_msg = json.loads(body)
                if user_msg['friendHashID'] == Hash:
                    emit(user_msg['type'], body, room=request.sid)
                    channel.basic_ack(method_frame.delivery_tag)
                num_msgs = num_msgs - 1

                if num_msgs == 0:
                    break

            """if len(all_msgs) != 0:
                all_msgs = json.dumps(all_msgs)
                emit('unread', all_msgs, room=request.sid)"""
        channel.close()
