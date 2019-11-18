import webbrowser, cv2, eel, base64
host = "localhost"
port = 8000
html = "index.html"
url = "http://{}:{}/{}".format(host, port, html)

streaming = False
mouse_on_down, x1, y1, x2, y2 = False, None, None, None, None

mode = 0 # 0: pc / 1: mobile / 2: mobile webserver

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

@eel.expose
def toggle_stream():
    global streaming
    streaming = not streaming
    if streaming == True:
        print("Streaming start.")
    else:
        print("Streaming stopped.")

@eel.expose
def setup_cam(width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    eel.setup_img(width, height)

def imshow(frame):
    ret, jpeg = cv2.imencode('.jpg', frame)
    jpeg_b64 = base64.b64encode(jpeg.tobytes())
    jpeg_str = jpeg_b64.decode()
    eel.js_imshow(jpeg_str)

def loop():
    while True:
        ret, frame = cap.read()
        if mouse_on_down == True & streaming == True:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if streaming == True:
            imshow(frame)
        eel.sleep(0.03)

eel.spawn(loop)
if mode == 0:
    print("Server is running on desktop")
    cap = cv2.VideoCapture(0)
    setup_cam(640, 480)
    eel.start(html, size=(680, 600))

elif mode == 1 or mode == 2:
    if mode == 1:
        webbrowser.open(url)
    cap = cv2.VideoCapture(0)
    setup_cam(240, 320)
    print("Server is running on {}".format(url))
    eel.start(html, mode=None, port=port, host=host)
