import cv2
import base64
import io
import datetime
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from json_response import JsonResponse

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
        if len(faces) == 0:
            return False
        return frame

    def get_frame(self):
        success, image = self.video.read()
        if success:
            image_with_faces = self.detect_faces(image)
            if image_with_faces is False:
                return None
            if self.is_capturing:
                ret, jpeg = cv2.imencode('.jpg', image_with_faces)
                self.is_capturing = False
            else:
                ret, jpeg = cv2.imencode('.jpg', image)

            # Videoyu yatay olarak düzelt
            #image_flipped = cv2.flip(jpeg, 1)  # 1 yatay döndürme

            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + image_flipped.tobytes() + b'\r\n\r\n'
        return None

    def start_capturing(self):
        self.is_capturing = True


def video_monitor(request):
    return render(request, 'monitor.html')

def capture_photo(request):
    camera = VideoCamera()
    camera.start_capturing()

    # Fotoğrafı al ve base64 kodlamasını yap
    success, image = camera.video.read()
    if success:
        image_with_faces = camera.detect_faces(image)
        if image_with_faces is False:
            ret, jpeg = cv2.imencode('.jpg', image_with_faces)
            image_base64 = base64.b64encode(jpeg.tobytes()).decode()
            return JsonResponse({'error': 'Yüz tespit edilemedi.','image': 'data:image/jpeg;base64,' + image_base64})


        ret, jpeg = cv2.imencode('.jpg', image_with_faces)
        image_base64 = base64.b64encode(jpeg.tobytes()).decode()

        # Base64 formatında çekilen fotoğrafı JSON formatında döndür
        return JsonResponse({'image': 'data:image/jpeg;base64,' + image_base64})

    return HttpResponse("Fotoğraf çekilemedi.")