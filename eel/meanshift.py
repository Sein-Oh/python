import webbrowser, cv2, eel, base64
import numpy as np

host = "localhost"
port = 8000
html = "index.html"
url = "http://{}:{}/{}".format(host, port, html)

streaming, tracking, tracking_first = False, False, True
mouse_on_down, x1, y1, x2, y2 = False, None, None, None, None

eel.init('web')
@eel.expose
def mouse_handler(evt):
    global mouse_on_down, x1, y1, x2, y2, tracking, tracking_fitst
    if evt[0] == "mousedown":
        mouse_on_down = True
        tracking = False
        tracking_fitst = True
        x1, y1 = evt[1], evt[2]

    elif evt[0] == "mouseup":
        mouse_on_down = False
        tracking = True

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
    global tracking_fitst
    while True:
        ret, frame = cap.read()
        if mouse_on_down == True and streaming == True:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        if streaming == True:
            if tracking == True:
                if tracking_fitst == True:
                    tracking_fitst = False
                    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
                    xmin, xmax = min(x1, x2), max(x1, x2)
                    ymin, ymax = min(y1, y2), max(y1, y2)
                    track_window = (xmin, ymin, xmax-xmin, ymax-ymin)
                    roi = frame[ymin:ymax, xmin:xmax]
                    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    roi_hist = cv2.calcHist([roi],[0],None,[180],[0,180])
                    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
                    
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
                ret, track_window = cv2.meanShift(dst, track_window, term_crit)
                x,y,w,h = track_window
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

            imshow(frame)
        eel.sleep(0.03)

eel.spawn(loop)

mode = 0 # 0: pc / 1: mobile / 2: mobile webserver

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