import json
import time
from flask import request, current_app, render_template
from .utils import hash_func, get_confirm_token, convert_base64_to_url,face_verify
from modules import db, mail, socketio, redis_client
from modules.models import User
from flask_mail import Message
from flask_socketio import emit
import pika


@socketio.on('newUser')
def newUser(new_data):
    data = json.loads(new_data)
    url = convert_base64_to_url(data['dpBase64'], data['hashID'])
    print(url)
    new_user = User(hashID=data['hashID'], username=data['name'],
                    email=data['email'], notif_token=data['token'],
                    phone=data['phone'], verified=False, imageUrl=url,
                    interest_1=data['interests'][0], interest_2=data['interests'][1],
                    interest_3=data['interests'][2], interest_4=data['interests'][3],
                    interest_5=data['interests'][4])
    db.session.add(new_user)
    try:
        db.session.commit()
        msg = Message('Xeno', sender='support@getxeno.in',
                  recipients=[data['email']])
        msg.html = render_template('email.html', name=data['name'], url="https://xeno-website.herokuapp.com/"+get_confirm_token(data['hashID']))
        mail.send(msg)
        redis_client.set(request.sid, data['hashID'])
        redis_client.set(data['hashID'], request.sid)
        pika_client = pika.BlockingConnection(
            pika.URLParameters(current_app.config['MQ_URL']))
        channel = pika_client.channel()
        queue_val = hash_func(data['hashID'])
        channel.queue_declare(queue=str(queue_val))
        channel.close()
        msg = {'id': int(time.time() * 1000), "userHashID": "42424242424242424242424242424242",
                   "friendHashID": data['hashID'], "content": "Welcome To Xeno!"}
        msg = json.dumps(msg)
        emit('message',msg,room=request.sid)
    except:
        print("Error adding data to database")
        db.session.rollback()


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
    if user.verified == True:
        data = {'hashID':hashID}
        data_json = json.dumps(data)
        emit('emailVerified',data_json)
        message = "Your email has been verified successfully!"
        msg = {'id': int(time.time() * 1000), "userHashID": "42424242424242424242424242424242",
                   "friendHashID": user.hashID, "content": message}
        msg = json.dumps(msg)
        receiver = redis_client.get(user.hashID)
        if receiver is None:
            pika_client = pika.BlockingConnection(
                pika.URLParameters(current_app.config['MQ_URL']))
            channel = pika_client.channel()
            queue_val = hash_func(user.hashID)
            channel.basic_publish(exchange='', routing_key=str(queue_val), body=msg)
            channel.close()
        else:
            receiver = receiver.decode('utf-8')
            emit('message',msg, room=receiver)

@socketio.on('imageForVerification')
def ImageVerification(data):
    image_data = json.loads(data)
    user = User.query.filter_by(hashID=image_data['hashID']).first()
    face_verify(user.imageUrl,image_data['base64'])
    result = {'hashID':image_data['hashID'],'result':False}
    receiver = redis_client.get('hashID')
    receiver = receiver.decode('utf-8')
    emit('picVerified',result,room=receiver)

"""@socketio.on('users')
def existingUser(check):
    data = User.query.filter(User.hashID != redis_client.get(request.sid).decode('utf-8')).all()
    users = UserSchema(many=True)
    details = users.dump(data)
    details_json = {"users":details}
    details_json = json.dumps(details_json)
    emit('users',details_json)"""
