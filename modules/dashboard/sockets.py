from modules import socketio, db
from modules.global_utils import messageHandler, transactionFail, notifications
from modules.models import User
import json
import time


@socketio.on('dashBroadcast')
def broadcast(message):
    users = User.query.all()
    for user in users:
        if user.hashID != "42424242424242424242424242424242":
            msg = {'id': int(time.time() * 1000), 'type': 'message',
                   "userHashID": "42424242424242424242424242424242",
                   "friendHashID": user.hashID, "content": message}
            json_msg = json.dumps(msg)
            messageHandler(message_json=json_msg, message=msg)


@socketio.on('dashNotifBroadcast')
def notifBroadcast(title, message):
    users = User.query.all()
    for user in users:
        try:
            print(user.notif_token)
            notifications(user.notif_token, title, message)
        except Exception:
            pass


@socketio.on('dashNotif')
def notif(email, title, message):
    user = User.query.filter_by(email=email)
    try:
        print(user.notif_token)
        notifications(user.notif_token, title, message)
    except Exception:
        pass


@socketio.on('dashSendMessage')
def sendMessage(email, message):
    user = User.query.filter_by(email=email).first()
    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": user.hashID, "content": message}
    message_json = json.dumps(msg)
    messageHandler(message_json=message_json)


@socketio.on('dashNameChangeAccepted')
@transactionFail
def nameChangeAccepted(name_json):
    data = json.loads(name_json)
    message = "Your request for name change has been processed\
 successfully. Your new name {}.".format(data['newName'])
    user_obj = User.query.filter_by(email=data['email']).first()
    oldName = user_obj.username
    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": user_obj.hashID, "content": message}
    nameChange_msg = {'type': 'nameChange',
                      "userHashID": "42424242424242424242424242424242",
                      "friendHashID": user_obj.hashID,
                      "content": data['newName']}
    json_msg = json.dumps(msg)
    json_nameChange_msg = json.dumps(nameChange_msg)
    user_obj.username = data['newName']
    db.session.commit()
    messageHandler(message_json=json_nameChange_msg, message=nameChange_msg)
    messageHandler(message_json=json_msg, message=msg)

    friend_message = "Your friend {} has changed their\
 name to {}".format(oldName, data['newName'])

    blockees = user_obj.block
    for friend in user_obj.friends:
        if friend not in blockees:
            friend_msg = {'id': int(time.time() * 1000), 'type': 'message',
                          "userHashID": "42424242424242424242424242424242",
                          "friendHashID": friend.friend_hashID,
                          "content": friend_message}
            friend_nameChange_msg = {'type': 'friendNameChange',
                                     "userHashID": user_obj.hashID,
                                     "friendHashID": friend.friend_hashID,
                                     "content": data['newName']}
            friend_nameChange_msg_json = json.dumps(friend_nameChange_msg)
            friend_msg_json = json.dumps(friend_msg)
            messageHandler(message_json=friend_nameChange_msg_json,
                           message=friend_nameChange_msg)
            messageHandler(message_json=friend_msg_json,
                           message=friend_msg)


@socketio.on('dashNameChangeDenied')
def nameChangeDenied(name_json):
    data = json.loads(name_json)
    message = "Your request for name change couldn't be processed, as\
 the name you requested doesn't match the official records.\
 If you believe this is an error from our end, please drop us a\
 feedback regarding this."
    user_obj = User.query.filter_by(email=data['email']).first()
    msg = {'id': int(time.time() * 1000), 'type': 'message',
           "userHashID": "42424242424242424242424242424242",
           "friendHashID": user_obj.hashID, "content": message}
    json_msg = json.dumps(msg)
    messageHandler(message_json=json_msg, message=msg)
