import json
from flask import request, current_app
from .utils import hash_func, get_confirm_token, convert_base64_to_url
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
                    phone=data['phone'], verified=data['verified'], imageUrl=url,
                    interest_1=data['interests'][0], interest_2=data['interests'][1],
                    interest_3=data['interests'][2], interest_4=data['interests'][3],
                    interest_5=data['interests'][4])
    db.session.add(new_user)
    msg = Message('Xeno', sender='support@getxeno.in',
                  recipients=[data['email']])
    # msg.body = "Hey " + data['name']+",\nThank you for registering with Xeno.\nYour verification link is: https://xeno-website.herokuapp.com/" + \
    #    get_confirm_token(data['hashID']) + \
    #    "\n\n Have fun, and keep xeno-ing.\nTeam Xeno"
    msg.html = """<html >
  <head>
    <title>Xeno | Verification</title>
  </head>
  <body>
    <main style="margin-top: 15%;
    margin-left:25%;
    ">
      <h2 style=>Hey {},</h2>
      <span>Thank you for registering with Xeno. </span>
      <p>
        Just one step remains before you ecperience Xeno.<br />
        Click on the link below to verify your account.
      </p>
      <a href ="{}">
      <button style='width: 400px;

      height:50px; background-color: #0f44C7;
      ; color:white; font-weight: bold;'>VERIFY EMAIL</button>
      </a>
      <footer style='position:absolute;
      bottom: 30px;
      font-size:15px;
      color:grey;
        text-align: center;'   >
          This is a system generated email from Xeno. Do not reply to this.<br/>
          ~ Team Xeno
      </footer>
    </main>
  </body>
</html>""".format(data['name'], "https://xeno-website.herokuapp.com/" + get_confirm_token(data['hashID']))
    mail.send(msg)
    print('Sent')
    redis_client.set(request.sid, data['hashID'])
    redis_client.set(data['hashID'], request.sid)
    pika_client = pika.BlockingConnection(
        pika.URLParameters(current_app.config['MQ_URL']))
    channel = pika_client.channel()
    queue_val = hash_func(data['hashID'])
    channel.queue_declare(queue=str(queue_val))
    channel.close()
    db.session.commit()


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


"""@socketio.on('users')
def existingUser(check):
    data = User.query.filter(User.hashID != redis_client.get(request.sid).decode('utf-8')).all()
    users = UserSchema(many=True)
    details = users.dump(data)
    details_json = {"users":details}
    details_json = json.dumps(details_json)
    emit('users',details_json)"""
