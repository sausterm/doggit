import io
import os
import torch
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
import cv2
import numpy as np
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True



face_cascade = cv2.CascadeClassifier('app/opencv-front-face-default.xml')
face_cascade2 = cv2.CascadeClassifier('app/haarcascade_frontalface_alt.xml')

def resize(img):
    img = cv2.resize(np.float32(img), (300, 300))
    img = Image.fromarray(np.uint8(img)).convert('RGB')
    return img


def reset():
    face_cascade = None
    face_cascade2 = None
    BREEDS = None
    NUM_BREEDS = None
    model = None
    img = None
    img_t = None
    batch_t = None
    out = None
    breeds = None


transform = transforms.Compose([            
    transforms.Resize(256),                    
    transforms.CenterCrop(224),               
    transforms.ToTensor(),                   
    transforms.Normalize(                      
    mean=[0.485, 0.456, 0.406],               
    std=[0.229, 0.224, 0.225]                  
          )])



def get_breeds():
    file = open("app/breeds.txt")
    breeds = list(file)
    file.close()
    return breeds

BREEDS = get_breeds()
NUM_BREEDS = len(get_breeds())


def face_detector(img):
    gray = cv2.cvtColor(np.float32(img), cv2.COLOR_BGR2GRAY)
    gray = np.array(gray, dtype='uint8')
    faces = face_cascade.detectMultiScale(gray)
    faces2 = face_cascade2.detectMultiScale(gray)
    return min(int(len(faces)), int(len(faces2))) > 0 

def dog_detector(img):
    ## : Complete the function.

    '''
    Use pre-trained VGG-16 model to obtain index corresponding to 
    predicted ImageNet class for image at specified path
    Args:
        img_path: path to an image  
    Returns:
        Index corresponding to VGG-16 model's prediction
    '''
    squeezenet = models.squeezenet1_1(pretrained=True)
    squeezenet.eval()
    transform = transforms.Compose([            
    transforms.Resize(256),                    
    transforms.CenterCrop(224),               
    transforms.ToTensor(),                   
    transforms.Normalize(                      
    mean=[0.485, 0.456, 0.406],               
    std=[0.229, 0.224, 0.225]                  
          )])
    
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    out = squeezenet(batch_t)
    out = torch.nn.functional.softmax(out, dim=1)[0] * 100
    return 150 < int(out.argmax()) < 269 # true/false

def predict_breed(img):
    # load the image and return the predicted breed
    
    model = models.densenet121(pretrained=True)
 
    model.classifier=nn.Sequential(nn.Linear(1024,512),
                                        nn.ReLU(),
                                        nn.Dropout(0.2),
                                       nn.Linear(512,133))


    PATH = "app/model.pth"
    model.load_state_dict(torch.load(PATH, map_location=torch.device('cpu') ))
    model.eval()
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    out = model(batch_t)
    probs = torch.nn.functional.softmax(out, dim=1)[0] * 100
    args = probs.argsort()[-3:]
    
    return list(BREEDS[int(arg)] for arg in args)
    #return out
