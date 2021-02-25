from modules import mail, socketio
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
    msg.body = 'Email: '+data['email']+'\nOld Name: '+data['oldName']+'\nNew Name: '+data['newName']
    mail.send(msg)
