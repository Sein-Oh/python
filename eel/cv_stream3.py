import webbrowser, cv2, eel, base64

host = "localhost"
port = 5000
html = "cv_stream.html"
url = "http://{}:{}/{}".format(host, port, html)

eel.init('web')

@eel.expose
def mouse_event(evt):
    type, x, y = evt.split(",")
    print(x,y)

@eel.expose
def send_img():
    _, frame = cap.read()
    _, jpeg = cv2.imencode('.jpg', frame)
    jpeg_b64 = base64.b64encode(jpeg.tobytes())
    jpeg_str = jpeg_b64.decode()
    return jpeg_str

webbrowser.open(url)
print("Server is running on {}".format(url))
cap = cv2.VideoCapture("pump.mp4")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
eel.start(html, mode=None, port=port, host=host)
