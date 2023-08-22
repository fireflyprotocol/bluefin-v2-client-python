import socketio 

# Create a Socket.IO client instance
sio = socketio.Client()

# Define an event handler for the 'connect' event
@sio.event
def connect():
    print('Connected to server')
    # Subscribe to the 'message' event
    # sio.emit('subscribeToRoom', "room1")

# Define an event handler for the 'message' event
@sio.event
def roomMessage(data):
    print('Received message:', data)

# Connect to the Socket.IO server
sio.connect('http://localhost:3000')

# Wait for events and keep the connection alive
sio.wait()