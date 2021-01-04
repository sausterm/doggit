# export FLASK_APP=app/main.py
#  export FLASK_ENV=development
# flask run

from flask import Flask, request,jsonify, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
from app.utils import face_detector, dog_detector, get_breeds, predict_breed, reset, resize
import os


UPLOAD_FOLDER = "app/static/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



#face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')

def allowed_file(filename):
    # xxx.png
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def file_size(filename):
    os.stat('somefile.txt').st_size

#GET IMAGE AS DIRECT INPUT INTO FILES
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        os.remove(os.path.join(UPLOAD_FOLDER,'image.jpg'))
    except:
        pass

    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file is None or file.filename == "":
            out = 'no file'
            return render_template('index.html', prediction_text=out)
        if not allowed_file(file.filename):
            out = 'format not supported.'
        

        img = Image.open(io.BytesIO(file.read())) #.convert('RGB')
        img = resize(img)
        uploaded_image = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpg')
        img.save(uploaded_image,'JPEG')

        return render_template('index.html', uploaded_image = uploaded_image[4:], prediction_text = uploaded_image[4:])
    


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

        #img = file.read()
        img = Image.open(io.BytesIO(file.read())).convert('RGB')
        img_save = img.save("app/static/images/image.jpg",'JPEG')
        file_size = os.path.getsize("app/static/images/image.jpg")

        if file_size > 600000:
            img.save("app/static/images/image.jpg",'JPEG',optimize = True,  
                 quality = 15) 
        del img
        del img_save 
        del file_size

        file_size = os.path.getsize("app/static/images/image.jpg")

        img = Image.open("app/static/images/image.jpg")
        #os.remove("app/images/image.jpg")

        faces = face_detector(img.convert('RGB'))
        dogs = dog_detector(img)
        breeds = list(reversed(predict_breed(img))) #.split(',')[0][1:-1]
        del img
        breeds = [breed.split(',')[0][1:-1] for breed in breeds]
        
        if faces:
            out = f"Hello Human! You look a lot like a {breeds[0]}!"
        elif dogs:
            out = f"This dog looks like a {breeds[0]}!"
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
