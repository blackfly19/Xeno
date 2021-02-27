from modules import mail, socketio, db
from modules.models import User
from flask_mail import Message
import json


@socketio.on('submitFeedback')
def feedback(feedback_json):
    data = json.loads(feedback_json)
    msg = Message('Feedback', sender='support@getxeno.in', recipients=['support@getxeno.in'])
    msg.body = 'Email: '+data['email'] + '\n\nFeedback: ' + data['content'] + '\n\nDevice: ' + data['device'] + '\nOS: ' + data['os'] + '\nApp Version: ' + data['appV']
    mail.send(msg)

@socketio.on('nameChange')
def nameChange(name_json):
    data = json.loads(name_json)
    msg = Message('Name Change Request', sender='support@getxeno.in', recipients=['support@getxeno.in'])
    msg.body = 'Email: '+data['email']+'\nCurrent Name: '+data['currentName']+'\nNew Name: '+data['newName']
    mail.send(msg)

@socketio.on('newInterests')
def interestChange(newInterests):
    data_interests = json.loads(newInterests)
    user_obj = User.query.filter_by(hashID=data_interests['hashID']).first()
    user_obj.interest_1 = data_interests['interests'][0]
    user_obj.interest_2 = data_interests['interests'][1]
    user_obj.interest_3 = data_interests['interests'][2]
    try:
        user_obj.interest_4 = data_interests['interests'][3]
    except IndexError:
        user_obj.interest_4 = None
    try:
        user_obj.interest_5 = data_interests['interests'][4]
    except IndexError:
        user_obj.interest_5 = None
    db.session.commit()
    print("Interests Changed")