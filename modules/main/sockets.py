from flask import request
import json
import pika
from flask_socketio import emit
from modules import socketio,redis_client,MQ_URL
from .utils import hash_func

@socketio.on('connect')
def connect():
    print("Connected: ",request.sid)
    emit('authorize',0)

@socketio.on('disconnect')
def disconnect():
    print("Disconnected: ",request.sid)
    if redis_client.exists(request.sid):
        user_hash = redis_client.get(request.sid)
        redis_client.delete(request.sid)
        redis_client.delete(user_hash)

@socketio.on('mapHashID')
def mapHashID(Hash):

    if Hash != None:
        pika_client = pika.BlockingConnection(pika.URLParameters(MQ_URL))
        channel = pika_client.channel()

        if redis_client.exists(Hash):
            redis_client.delete(redis_client.get(Hash))
        redis_client.set(request.sid,Hash)
        redis_client.set(Hash,request.sid)

        queue_val = hash_func(Hash)
        all_msgs = []
        val = channel.queue_declare(queue=str(queue_val),passive=True)
        num_msgs = val.method.message_count
        if num_msgs != 0:
            for method_frame,_,body in channel.consume(str(queue_val)):
                body = body.decode('utf-8')
                user_msg = json.loads(body)
                if user_msg['friendHashID'] == Hash:
                    all_msgs.append(user_msg)
                    channel.basic_ack(method_frame.delivery_tag)
                num_msgs = num_msgs - 1

                if num_msgs == 0:
                    break
            all_msgs = json.dumps(all_msgs)
            emit('unread',all_msgs)
            print(all_msgs)
        channel.close()
    

