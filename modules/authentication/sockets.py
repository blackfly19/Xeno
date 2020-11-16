import json
import random as rd
from flask import request
from modules import db,mail,socketio,redis_client
from modules.models import User,UserSchema
from flask_mail import Message
from flask_socketio import emit

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
    msg = Message('Xeno',sender='xeno@support.com',recipients=[data['email']])
    msg.body = 'Your account with username ' + data['name'] + ' has been registered'
    mail.send(msg)
    print('Sent')
    redis_client.set(request.sid,data['hashID'])
    redis_client.set(data['hashID'],request.sid)
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

@socketio.on('users')
def existingUser(check):
    data = User.query.filter(User.hashID != redis_client.get(request.sid).decode('utf-8')).all()
    users = UserSchema(many=True)
    details = users.dump(data)
    details_json = {"users":details}
    details_json = json.dumps(details_json)
    emit('users',details_json)