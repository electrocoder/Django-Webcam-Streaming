import cv2
import base64
import io
import datetime
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_capturing = False

    def __del__(self):
        self.video.release()

    def detect_faces(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    def get_frame(self):
        success, image = self.video.read()
        if success:
            image_with_faces = self.detect_faces(image)  # Yüz tespiti burada yapılıyor
            if self.is_capturing:
                ret, jpeg = cv2.imencode('.jpg', image_with_faces)
                self.is_capturing = False
                return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'
            else:
                ret, jpeg = cv2.imencode('.jpg', image)
                return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'
        return None

    def start_capturing(self):
        self.is_capturing = True


def video_feed(request):
    try:
        camera = VideoCamera()
        return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
    except GeneratorExit:
        pass


def video_monitor(request):
    return render(request, 'monitor.html')


def capture_photo(request):
    camera = VideoCamera()
    camera.start_capturing()

    # Fotoğrafı al ve base64 kodlamasını yap
    success, image = camera.video.read()
    if success:
        image_with_faces = camera.detect_faces(image)
        ret, jpeg = cv2.imencode('.jpg', image_with_faces)
        image_base64 = base64.b64encode(jpeg.tobytes()).decode()

        # Dosya adı ve content type belirle
        current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"photo_{current_time}.jpg"
        content_type = "image/jpeg"

        # HTTP yanıtını hazırla ve fotoğrafı indir
        response = HttpResponse(jpeg.tobytes(), content_type=content_type)
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    return HttpResponse("Fotoğraf çekilemedi.")

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
