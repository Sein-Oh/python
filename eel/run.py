import eel, io, base64
import numpy as np
from PIL import Image

eel.init('web')
@eel.expose
def send_image(msg):
    img = io.BytesIO(np.fromstring(base64.b64decode(msg.split(',')[1]), np.uint8))
    im = Image.open(img)
    buff = io.BytesIO()
    gray = im.convert('L')
    #gray = gray.resize((50, 50))
    gray.save(buff, format="JPEG")
    out = str(base64.b64encode(buff.getvalue()))
    out = out[2:-1]
    eel.sendTo(out)

eel.start('rtc.html')
