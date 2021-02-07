from modules import socketio,db
from models import Block

@socketio.on('addBlock')
def addBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    new_block = Block(hashId_blocker=block_dict['blocker'],hashId_blockee=block_dict['blockee'])
    db.session.add(new_block)
    db.session.commit()

@socketio.on('removeBlock')
def removeBlock(block_json):
    print(block_json)
    block_dict = json.loads(block_json)
    rem_block = Block.query.filter_by(hashId_blocker=block_dict['blocker'],hashId_blockee=block_dict['blockee']).first()
    db.session.delete(rem_block)
    db.session.commit()