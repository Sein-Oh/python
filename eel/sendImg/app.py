import eel, io, base64, cv2
import numpy as np
from PIL import Image

eel.init('web')

cap = cv2.VideoCapture(0)

@eel.expose
def say(msg):
    _, frame = cap.read()
    frame = cv2.resize(frame, (213, 120), interpolation = cv2.INTER_AREA)
    __, jpeg = cv2.imencode('.jpg', frame)
    jpeg = base64.b64encode(jpeg.tobytes())
    jpeg_str = jpeg.decode()
    eel.sendTo(jpeg_str)
    
    

eel.start('index.html')
