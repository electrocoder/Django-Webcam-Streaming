import cv2
import base64
import io ,json
import datetime
from django.http import HttpResponse

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_capturing = False

    def __del__(self):
        self.video.release()


 
   
    def get_frame(self):
        success, image = self.video.read()
        if success:
            if self.is_capturing:
                image_with_faces = self.yuz_tespit(image)
                ret, jpeg = cv2.imencode('.jpg', image_with_faces)
                self.is_capturing = False
                
                # Veriyi ekleyin (örneğin, fotoğrafın adı veya tarih-saat bilgisi)
                current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                data = {'time': current_time}
                
                # JSON formatına dönüştürün ve base64 ile kodlayın
                data_json = json.dumps(data).encode()
                data_encoded = base64.b64encode(data_json)
                
                return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n' + data_encoded + b'\r\n\r\n'
            else:
                ret, jpeg = cv2.imencode('.jpg', image)
                return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'
        return None

    def start_capturing(self):
        self.is_capturing = True

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
