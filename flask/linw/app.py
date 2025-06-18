from flask import Flask, Response, render_template, jsonify

import base64
import cv2
import dxcam
import json
import numpy as np
import os
import requests
import threading
import time

app = Flask(__name__)

if not os.path.isdir("capture"):
    os.system("mkdir capture")


def parse_txt(path):
  with open(path, "r", encoding="utf-8") as f:
    file = f.read()

  userdata = {}
  for line in file.split("\n"):
    split_idx = line.find(":")
    key = line[:split_idx].strip()
    value = line[split_idx+1:].strip()
    userdata[key] = value
  return userdata


def load_img(path):
    img_np = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    return img


def b64_to_cv(data):
    return cv2.imdecode(np.frombuffer(base64.b64decode(data.split(",")[1]), np.uint8), cv2.IMREAD_COLOR)


def cv_to_b64(img):
    ret, buffer = cv2.imencode(".png", img)
    buffer_b = buffer.tobytes()
    im_b64 = base64.b64encode(buffer_b)
    return str(im_b64)


def find_img(background, target):
    h, w, _ = target.shape
    background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(background, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x, y = max_loc
    max_val = round(max_val, 2)
    return x, y, w, h, max_val


def calc_hp(img_hp, thres_min=210):
    hpSplit = cv2.split(img_hp)[2]  # hp바의 BGR색상 중 R값만 가져오기
    hpBlur = cv2.blur(hpSplit, (5, 5))  # 블러 처리
    hpThres = cv2.threshold(hpBlur, thres_min, 255, cv2.THRESH_BINARY)[1]
    hpThres_img = cv2.cvtColor(hpThres, cv2.COLOR_GRAY2BGR)
    hpPoint = np.flip(hpThres).argmax()
    hpPoint = 100 if hpPoint >= hpThres.shape[1] else int((1-(np.flip(hpThres).argmax() / hpThres.shape[1])) * 100)
    return hpPoint, hpThres_img


def cool_down(key):
    cooling[key] = False


def cool_run(key, sec):
    cooling[key] = True
    threading.Timer(sec, cool_down, args=(key,)).start()


def tele_send_msg(msg):
    try:
        url = f'https://api.telegram.org/bot{telegram["token"]}/sendMessage?chat_id={telegram["chat_id"]}&text={msg}'
        requests.get(url)
    except:
        print("텔레그램 메세지 보내기 실패.")


def tele_send_photo(filename, caption):
    try:
        data = {"chat_id": {telegram["chat_id"]}, "caption": caption}
        url = f'https://api.telegram.org/bot{telegram["token"]}/sendphoto?chat_id={telegram["chat_id"]}'
        with open(filename, "rb") as f:
            requests.post(url, data=data, files={"photo": f})
    except:
        print("텔레그램 사진 보내기 실패")


def send_req(url):
    requests.get(url)

def send_keys(keys, frame):
    key_ary = keys.split(" ")
    for key in key_ary:
        if "-" in key:
            time.sleep(float(key[1:]))
        elif "noti" in key:
            msg = key.split("(")[1].split(")")[0]
            threading.Thread(target=tele_send_msg, args=[msg,], daemon=True).start()
        elif "photo" in key:
            msg = key.split("(")[1].split(")")[0]
            cv2.imwrite("capture/event.jpg", frame)
            threading.Thread(target=tele_send_photo, args=["capture/event.jpg", msg,], daemon=True).start()
        elif key == "capture":
            cv2.imwrite(f"capture/{time.strftime('%y%m%d_%H%M%S')}.jpg", frame)
        elif "," in key:
            if use_server:
                url = f'{server["input"]}/{key}'
                # requests.get(url, timeout=1)
                threading.Thread(target=send_req, args=(url,), daemon=True).start()
            else:
                x, y = list(map(int, key.split(",")))
                mx = int(x / frame.shape[1] * 1000)
                my = int(y / frame.shape[0] * 1000)
                cmd = f"{mx},{my}"
                ser.write(cmd.encode())
        else:
            if use_server:
                url = f'{server["input"]}/{key}'
                threading.Thread(target=send_req, args=(url,), daemon=True).start()
                # requests.get(url)
            else:
                ser.write(key.encode())


def update_frame():
    global frame
    while True:
        if not pause:
            try:
                frame = cam.read()[1] if use_server else cam.get_latest_frame()
                data = {}
                
                for name in timer:
                    if run[name] and not cooling[name]:
                        key = timer[name]["key"]
                        cooltime = float(timer[name]["cooltime"])
                        send_keys(key, frame)
                        cool_run(name, cooltime)

                for name in hp:
                    if run[name] and not cooling[name]:
                        key = hp[name]["key"]
                        cooltime = float(hp[name]["cooltime"])
                        x1 = int(hp[name]["x1"])
                        y1 = int(hp[name]["y1"])
                        x2 = int(hp[name]["x2"])
                        y2 = int(hp[name]["y2"])
                        thres = float(hp[name]["threshold"])
                        min_hp = int(hp[name]["min range"])
                        max_hp = int(hp[name]["max range"])
                        roi = frame[y1:y2, x1:x2]
                        hp_calc, thres_img = calc_hp(roi, thres)
                        data[name] = hp_calc
                        if hp_calc >= min_hp and hp_calc <= max_hp:
                            send_keys(key, frame)
                            cool_run(name, cooltime)
                
                for name in img:
                    if run[name] and not cooling[name]:
                        key = img[name]["key"]
                        cooltime = float(img[name]["cooltime"])
                        x1 = int(img[name]["x1"])
                        y1 = int(img[name]["y1"])
                        x2 = int(img[name]["x2"])
                        y2 = int(img[name]["y2"])
                        thres = float(img[name]["threshold"])
                        roi = frame[y1:y2, x1:x2]
                        _x, _y, _w, _h, max_val = find_img(roi, img[name]["mat"])
                        data[name] = max_val
                        if max_val >= thres:
                            send_keys(key, frame)
                            cool_run(name, cooltime)


                thumbnail = cv2.resize(frame, dsize=(0,0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
                thumbnail_b64 = cv_to_b64(thumbnail)
                data["imgdata"] = thumbnail_b64
                yield f"""event: stream\ndata: {json.dumps(data)}\n\n"""
            except GeneratorExit:
                print("Client disconnected.")
                os._exit(0)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    return Response(update_frame(), mimetype="text/event-stream")


@app.route("/get_run_slots")
def get_slots():
    return jsonify(run)


@app.route("/pause")
def pause_stream():
    global pause
    pause = not pause
    print(pause)
    return jsonify(True if pause else False)


@app.route("/toggle/<name>")
def toggle_slot(name):
    run[name] = not run[name]
    return Response(status=204)



userdata = {}
txt_ary = [j for j in os.listdir("slots") if ".txt" in j]
for txt in txt_ary:
    name = txt.split(".")[0]
    userdata[name] = parse_txt(f"slots/{txt}")

telegram = {}
server = {}
timer = {}
hp = {}
img = {}
cooling = {}
run = {}
pause = False

for data in userdata:
    if userdata[data]["type"] == "telegram":
        telegram["token"] = userdata[data]["token"]
        telegram["chat_id"] = userdata[data]["chat_id"]
    elif userdata[data]["type"] == "server":
        server["input"] = userdata[data]["input"]
        server["stream"] = userdata[data]["stream"]
    elif userdata[data]["type"] == "timer":
        timer[data] = userdata[data]
        run[data] = False
        cooling[data] = False
    elif userdata[data]["type"] == "hp":
        hp[data] = userdata[data]
        run[data] = False
        cooling[data] = False
    elif userdata[data]["type"] == "img":
        img[data] = userdata[data]
        img[data]["mat"] = load_img(f"slots/{userdata[data]['img']}")
        run[data] = False
        cooling[data] = False


use_telegram = True if "token" in telegram and "chat_id" in telegram else False
print(f"Telegram: {'Enabled' if use_telegram else 'Disabled'}")

use_server = True if "input" in server and "stream" in server else False
print(f"Server: {'Enabled' if use_server else 'Disabled'}")


if use_server:
    cam = cv2.VideoCapture(server["stream"])
    ret, frame = cam.read()
else:
    cam = dxcam.create(output_color="BGR")
    cam.start(target_fps=10)
    frame = cam.get_latest_frame()
print("Capture start.")
print(f"Resolution : {frame.shape[1]}x{frame.shape[0]}")

if not use_server:
    import serial
    import serial.tools.list_ports
    print("Serial connect")
    ports = serial.tools.list_ports.comports()
    port_list = []
    for port in ports:
        port_list.append(port.device)
    if len(port_list) < 1:
        print("There are no abailable serial port.")
        os._exit(0)
    else:
        for port in port_list:
            try:
                ser = serial.Serial(port, baudrate=9600, timeout=1)
                ser.write(b"check")
                if ser.readline() == b"OK\r\n":
                    print(f"Serial connected at {port}.")
            except:
                print("Serial connection failed.")
                os._exit(0)


port = 5000
os.system(f"start msedge --app=http://localhost:{port}")
app.run(host="localhost", port=5000, debug=False, threaded=True)
