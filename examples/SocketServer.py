import socketio
import eventlet
import time

# Create a Socket.IO server instance
sio = socketio.Server()

# Define an event handler for the 'connect' event
@sio.on('connect')
def handle_connect(sid, environ):
    print('Client connected:', sid)
    background_task()
    

# Define an event handler for the 'message' event
@sio.on('message')
def handle_message(sid, data):
    print('Received message:', data)
    # Broadcast the received message to all connected clients
    sio.emit('message', data)

# Define the broadcast task
def broadcast_message():
    message = "Hello from the server!"
    print(message)
    sio.emit('message', message, namespace='/')

# Background task to broadcast messages at an interval
def background_task():
    print("hello")
    while True:
        time.sleep(5)  # Adjust the interval as needed
        broadcast_message()

# Run the Socket.IO server
if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 3051)), app)
    print("hello after")
    

