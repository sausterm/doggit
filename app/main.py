# export FLASK_APP=app/main.py
#  export FLASK_ENV=development
# flask run

from flask import Flask, request,jsonify, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
from app.utils import face_detector, dog_detector, get_breeds, predict_breed, reset

app = Flask(__name__, static_url_path='/static')
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
#face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')

def allowed_file(filename):
    # xxx.png
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def file_size(filename):
    os.stat('somefile.txt').st_size

#GET IMAGE AS DIRECT INPUT INTO FILES
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

   
    


@app.route('/classify', methods=['POST'])
def classify():
    if request.method == 'POST':
        file = request.files['file']
        if file is None or file.filename == "":
            out = 'no file'
            return render_template('index.html', prediction_text=out)
        if not allowed_file(file.filename):
            out = 'format not supported.'
            return render_template('index.html', prediction_text=out)
        
        #try:

        img = file.read()
        img_face = Image.open(io.BytesIO(img))
        img_dog = Image.open(io.BytesIO(img)).convert('RGB')
        del img

        img_save = img_dog.save("app/images/image.jpg",'JPEG')
        file_size = os.path.getsize("app/images/image.jpg")

        if file_size > 800000:
            img_dog.save("app/images/image.jpg",'JPEG',optimize = True,  
                 quality = 8) 

        img_dog = Image.open("app/images/image.jpg")
        faces = face_detector(img_face)
        del img_face

        dogs = dog_detector(img_dog)
        
        breeds = list(reversed(predict_breed(img_dog))) #.split(',')[0][1:-1]
        del img_dog
        breeds = [breed.split(',')[0][1:-1] for breed in breeds]
        
        if faces:
            out = f"Hello Hooman! You look a lot like a {breeds[0]}!"
        elif dogs:
            out = f"This doggo looks like a {breeds[0]}!"
        else:
            out = f"Hmm, I dont see a Hooman or Doggo in this picture. Try another one!"

        #return_dict = {'file_name': str(file.filename), 'out':out}
        reset()
        img = None
        img_face = None
        file = None
        faces = None
        dogs = None
        breeds = None
        return render_template('index.html', prediction_text=out)
        #    return jsonify({'error': 'error during prediction'})
