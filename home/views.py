import cv2
import base64
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.shortcuts import render
from json_response import JsonResponse
from django.core.mail import EmailMultiAlternatives
from .forms import EmailForm
from django.core.files.base import ContentFile
import mimetypes
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
            image_flipped = cv2.flip(jpeg, 1)  # 1 yatay döndürme

            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + image_flipped.tobytes() + b'\r\n\r\n'
        return None

    def start_capturing(self):
        self.is_capturing = True


def video_monitor(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            image_base64 = form.cleaned_data['image']
            
            # Base64 verisini jpg dosyasına dönüştürme
            format, image_data = image_base64.split(';base64,')
            extension = format.split('/')[-1]
            image = ContentFile(base64.b64decode(image_data), name=f'image.{extension}')

            # HTML içeriğini oluşturuyoruz
            html_content = render_to_string('email_template.html', {'name': name, 'email': email, 'phone': phone})
            plain_content = strip_tags(html_content)

            email_subject = 'New Contact Form Submission'
            email_from = 'info@esthetichairturkey.com'
            email_to = ['rojtoy@gmail.com']

            # E-posta gönderme işlemi
            email = EmailMultiAlternatives(email_subject, plain_content, email_from, email_to)
            email.attach(image.name, image.read(), mimetypes.guess_type(image.name)[0])
            email.attach_alternative(html_content, "text/html")
            email.send()

            return render(request, "thank-you.html")
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