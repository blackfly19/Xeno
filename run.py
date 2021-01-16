from modules import create_app,socketio

app = create_app(debug=True)
app.app_context().push()

if __name__ == '__main__':
    socketio.run(app)