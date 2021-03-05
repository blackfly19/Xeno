from modules import socketio, db
from modules.models import Block, User
import json


@socketio.on('addBlock')
def addBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    new_block = Block(
        blocker_hashID=block_dict['blocker'], blockee_hashID=block_dict['blockee'])
    db.session.add(new_block)
    db.session.commit()
    user = User.query.filter_by(hashID=block_dict['blocker'])
    print(user.block)


@socketio.on('removeBlock')
def removeBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    rem_block = Block.query.filter_by(
        blocker_hashID=block_dict['blocker'], blockee_hashID=block_dict['blockee']).first()
    db.session.delete(rem_block)
    db.session.commit()
