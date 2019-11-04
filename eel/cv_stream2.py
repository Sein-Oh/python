import webbrowser, cv2, eel, base64
host = "localhost"
port = 5000
html = "cv_stream2.html"
url = "http://{}:{}/{}".format(host, port, html)


def imshow(frame):
    ret, jpeg = cv2.imencode('.jpg', frame)
    jpeg_b64 = base64.b64encode(jpeg.tobytes())
    jpeg_str = jpeg_b64.decode()
    eel.js_imshow(jpeg_str)

def loop():
    while True:
        ret, frame = cap.read()
        if mouse_on_down == True:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        imshow(frame)
        eel.sleep(0.03)

mouse_on_down, x1, y1, x2, y2 = False, None, None, None, None

eel.init('web')
@eel.expose
def mouse_handler(evt):
    global mouse_on_down, x1, y1, x2, y2
    if evt[0] == "mousedown":
        mouse_on_down = True
        x1, y1 = evt[1], evt[2]
    elif evt[0] == "mouseup":
        mouse_on_down = False
    x2, y2 = evt[1], evt[2]  

eel.spawn(loop)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
webbrowser.open(url)
print("Server is running on {}".format(url))
eel.start(html, mode=None, port=port, host=host)
