from modules import mail, socketio, db
from modules.models import User
from flask_mail import Message
import json
import io


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

@socketio.on('reportFriend')
def reportFriend(data_json):
    data = json.loads(data_json)
    reporter_hashid = data['ownHashID']
    reported_hashid = data['friendHashID']
    reporter = User.query.filter_by(hashID=reporter_hashid).first()
    reported = User.query.filter_by(hashID=reported_hashid).first()
    chats = []
    print(data['content'])
    for i in data['chatRepo']:
        chats.append(json.dumps(i))
    chat_data = io.StringIO('\n'.join(chats))
    
    msg = Message('Report', sender='support@getxeno.in', recipients=['support@getxeno.in'])
    msg.attach("chat.json","application/json",chat_data.read())
    msg.body = 'Reporter HashID: '+reporter_hashid+"\nReporter Email: "+reporter.email+'\n\nReported HashID: '+reported_hashid+"\nReporter Email: "+reported.email+ '\n\nReport: ' + data['content']
    mail.send(msg)
