import sys, webbrowser, cv2, eel, base64

host = "localhost"
port = 5000
html = sys.argv[0].replace("py", "html")
url = "http://{}:{}/{}".format(host, port, html)

eel.init('web')
cap = cv2.VideoCapture(0)

@eel.expose
def setup(width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print("Video : {}, {}x{}".format(video_source, width, height))

@eel.expose
def py_send():
    _, frame = cap.read()
    _, jpeg = cv2.imencode('.jpg', frame)
    jpeg_b64 = base64.b64encode(jpeg.tobytes())
    jpeg_str = jpeg_b64.decode()
    eel.js_show(jpeg_str)

webbrowser.open(url)
print("Server is running on {}".format(url))
eel.start(html, mode=None, port=port, host=host)
