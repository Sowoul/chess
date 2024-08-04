from flask import Flask, render_template
from flask_socketio import SocketIO
from chess import Board,Piece
import json
def make_board(arr):
    temp=Board()
    for i,row in enumerate(arr):
        for j,elem in enumerate(row):
            if elem:
                temp.board[i][j]=Piece(elem['val'] , elem['color'], elem['type'])
    return temp

board=Board()
board.setup()

app=Flask(__name__)
socket = SocketIO(app=app)

@app.route('/')
def index():
    try:
        with open('state.json' , 'r') as file:
            global board
            board=make_board(json.loads(file.read()))
    except:
        render_template('index.html', board=board.to_dict())
    return render_template('index.html', board=board.to_dict())

@socket.on('connect')
def aa():
    print(board)
    socket.emit('getboard' , {'board' : board.to_dict()})

@socket.on('move')
def mv(msg):
    temp = make_board(msg["board"])
    if not temp.getpiece(msg["start"]):
        socket.emit('failure' , {'reason' : 'No Piece Selected'})
        return
    temp.move(msg["start"] , msg["to"])
    print(temp)
    store = temp.to_dict()
    with open('state.json' , 'w') as file:
        json.dump(store, file)
    file.close()
    socket.emit('getboard', {"board":store})

@socket.on('resetboard')
def reset():
    global board
    board =  Board()
    board.setup()
    store=board.to_dict()
    with open('state.json','w') as file:
        json.dump( store, file)
    print(store)
    socket.emit('getboard', {'board':store})

if __name__ == '__main__':
    socket.run(app=app, debug=True, port=8080)