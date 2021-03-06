# export FLASK_APP=app/main.py
#  export FLASK_ENV=development
# flask run

from flask import Flask, request,jsonify, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
from app.utils import face_detector, dog_detector, get_breeds, predict_breed, reset, resize
import os


UPLOAD_FOLDER = "app/static/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMAGE_PATH = str()
filename = str()

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '12345'

#face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')

def allowed_file(filename):
    # xxx.png
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#GET IMAGE AS DIRECT INPUT INTO FILES

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',start_bool = 1, upload_bool=0, classify_bool=0, try_another=0)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('index.html', start_bool = 0, upload_bool=1, classify_bool=0, try_another=0)


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],f))
 
    if request.method == 'POST':
        out = str()
        file = request.files['file']
        filename = file.filename
        session['filename'] = filename

        IMAGE_PATH = os.path.join(app.config['UPLOAD_FOLDER'],filename)

        if file is None or filename == "":
            out = 'no file'
            return render_template('index.html', prediction_text=out)
        if not allowed_file(filename):
            out = 'format not supported.'
            return render_template('index.html', prediction_text=out)
        

        img = Image.open(io.BytesIO(file.read())).convert('RGB') 
        img.save(IMAGE_PATH,'JPEG')
        file_size = os.path.getsize(IMAGE_PATH)
            #out = "failed to save image at {}".format(IMAGE_PATH)
        
        if file_size > 750000:
            img = resize(img)
            img.save(IMAGE_PATH,'JPEG')
            # out = "failed to resave large image at {}".format(IMAGE_PATH)

        return render_template('index.html', upload_bool=0, classify_bool=1, uploaded_image = IMAGE_PATH[4:], try_another=0, prediction_text=out)
    


@app.route('/result', methods=['GET'])
def result():
    if request.method == "GET":
        
        filename = session.pop('filename', None)
        IMAGE_PATH = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        img = Image.open(f"app/static/images/{filename}")

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
            out = f"Sorry! The model doesn't recognize any dogs or humans in this picture. Please try another one!"


        reset()
        img = None
        img_face = None
        file = None
        faces = None
        dogs = None
        breeds = None    
        
        #IMAGE_PATH = None
        return render_template('index.html', upload_bool=0, classify_bool=0, uploaded_image = IMAGE_PATH[4:], 
                                prediction_text=out,try_another=1)