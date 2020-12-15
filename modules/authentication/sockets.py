import json
import random as rd
from flask import request
from .utils import hash_func
from modules import db,mail,socketio,redis_client,MQ_URL
from modules.models import User,UserSchema
from flask_mail import Message
from flask_socketio import emit
import pika

@socketio.on('newUser')
def newUser(new_data):
    print(new_data)
    data = json.loads(new_data)
    url = 'https://res.cloudinary.com/fsduhag8/image/upload/v1601748391/renderDPs/m'+str(rd.randint(1,6))+'.jpg'
    print(url)
    new_user = User(hashID = data['hashID'],username=data['name'],
                    email=data['email'],notif_token=data['token'],
                    phone=data['phone'],verified=data['verified'],imageUrl=url)
    db.session.add(new_user)
    #msg = Message('Xeno',sender='xeno@support.com',recipients=[data['email']])
    #msg.body = 'Your account with username ' + data['name'] + ' has been registered'
    #mail.send(msg)
    print('Sent')
    redis_client.set(request.sid,data['hashID'])
    redis_client.set(data['hashID'],request.sid)
    pika_client = pika.BlockingConnection(pika.URLParameters(MQ_URL))
    channel = pika_client.channel()
    queue_val = hash_func(data['hashID'])
    val = channel.queue_declare(queue=str(queue_val))
    channel.close()
    db.session.commit()

@socketio.on('validatePhone')
def validatePhone(Phone):
    user = User.query.filter_by(phone=Phone).first()
    if user is None:
        emit('validatePhone',True)
    else:
        emit('validatePhone',False)

@socketio.on('validateEmail')
def validateEmail(Email):
    user = User.query.filter_by(email=Email).first()
    if user is None:
        emit('validateEmail',True)
    else:
        emit('validateEmail',False)