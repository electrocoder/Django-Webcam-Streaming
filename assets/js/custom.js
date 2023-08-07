// script.js

function toggleFormVisibility() {
    const formElement = document.querySelector('.form');
    formElement.style.display = formElement.style.display === 'none' ? 'block' : 'none';
}




function capturePhoto() {
    const captureUrl = document.getElementById('capture_photo').getAttribute('data-capture-url');
    
    fetch(captureUrl)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // Hata var, hata mesajını göster
                const errorMessage = document.getElementById('error-message');
                errorMessage.style.display = 'block';
                const succsesMessage = document.getElementById('succses-message');
                succsesMessage.style.display = 'none';
            } else {
                // Hata yok, çekilen fotoğrafı video alanında göster
                const video = document.getElementById('video-stream');
                video.style.display = 'none'; // Videoyu gizle
                const capturedImage = document.getElementById('captured-image');
                capturedImage.src = data.image; // Çekilen fotoğrafı görüntüle
                capturedImage.style.display = 'block'; // Fotoğrafı göster
                const errorMessage = document.getElementById('error-message');
                errorMessage.style.display = 'none';
                const succsesMessage = document.getElementById('succses-message');
                succsesMessage.style.display = 'block';

                // "Capture Photo" butonuna tıklanınca formun görünürlüğünü değiştir
                const captureButton = document.getElementById('capture-button');
                captureButton.addEventListener('click', toggleFormVisibility);
            
                document.getElementById('contact_form').style.display ="block"
                document.getElementById('capture_photo').style.display ="none"
                document.getElementById('frame-area').style.height = "86%";

                const imageBase64 = capturedImage.src;
                const textarea = document.getElementById('file-input')
                textarea.value = imageBase64;
            }
        })
        .catch(error => {
            console.error('Hata:', error);
        });
}


document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById('video-stream');
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(error => {
                console.error('Kamera erişimi hatası:', error);
            });
    }
});



