from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    emit('message', "Task received successfully!")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
