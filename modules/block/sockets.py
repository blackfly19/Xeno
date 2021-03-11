from modules import socketio, db
from modules.models import Block, User
from modules.global_utils import messageHandler
import json


@socketio.on('addBlock')
def addBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    new_block = Block(
        blocker_hashID=block_dict['blocker'],
        blockee_hashID=block_dict['blockee'])
    db.session.add(new_block)
    db.session.commit()
    url = "https://res.cloudinary.com/fsduhag8/image/upload/v1615465702/defaultUser_uodzbq.jpg"
    friend_msg = {'type': 'friendDpChange',
                  "userHashID": block_dict['blocker'],
                  "friendHashID": block_dict['blockee'],
                  "content": url}
    friend_msg_json = json.dumps(friend_msg)
    messageHandler(message_json=friend_msg_json, message=friend_msg)


@socketio.on('removeBlock')
def removeBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    rem_block = Block.query.filter_by(
        blocker_hashID=block_dict['blocker'],
        blockee_hashID=block_dict['blockee']).first()
    user = User.query.filter_by(hashID=block_dict['blocker']).first()
    db.session.delete(rem_block)
    db.session.commit()
    friend_msg = {'type': 'friendDpChange',
                  "userHashID": block_dict['blocker'],
                  "friendHashID": block_dict['blockee'],
                  "content": user.imageUrl}
    friend_msg_json = json.dumps(friend_msg)
    messageHandler(message_json=friend_msg_json, message=friend_msg)
