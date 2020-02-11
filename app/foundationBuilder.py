import cv2, os
import numpy as np
face_cascade = cv2.CascadeClassifier("D:/Client_Project/foundationFindr/final_app_cv/haarcascade_frontalface_default.xml")

import cognitive_face as CF

# Replace with a valid subscription key (keeping the quotes in place).
KEY = '27bf9fa5f3c04f34b463006bb757ab67'
CF.Key.set(KEY)

# Replace with your regional Base URL
BASE_URL = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0'
CF.BaseUrl.set(BASE_URL)

def processImg(IMG_PATH):
    #print("[info] Recognizing face in image")
    image = cv2.imread(IMG_PATH)
    faces = face_cascade.detectMultiScale(image, 1.3, 5)
    if len(faces) < 1:
        #print("[info] No Face found. Please retry capturing image")
        imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        for (x,y,w,h) in faces:
            roi_color = image[y:y+h, x:x+w]
        imgGray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    
    #print("[info] Getting best products for this face")
    
    h,w = imgGray.shape
    avg_color_per_row = np.average(imgGray, axis=0)
    avg_color = int(np.average(avg_color_per_row, axis=0))
    return avg_color

def findProducts(IMG_PATH):
    print("[info] Recognizing face in image")
    image = cv2.imread(IMG_PATH)
    #image = face_recognition.load_image_file(IMG_PATH)
    #small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    h, w, c = image.shape
    if h < 800 and w < 800:
        factor = 1
        small_frame = image.copy()
    elif h < 1500 and w < 1500:
        factor = 2
        small_frame = cv2.resize(image, (0, 0), fx=0.50, fy=0.50)
    elif h < 2500 and w < 2500:
        factor = 4
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    else:
        factor = 5
        small_frame = cv2.resize(image, (0, 0), fx=0.20, fy=0.20)
    face_locations = face_recognition.face_locations(small_frame, number_of_times_to_upsample=0, model="cnn")

    if len(face_locations) == 0:
        print("[info] Found 0 faces. Try Capturing again")
        return
    else:
        print("[info] Found a face")

    for top, right, bottom, left in face_locations:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= factor
        right *= factor
        bottom *= factor
        left *= factor
        # Extract the region of the image that contains the face
        face_image = image[top:bottom, left:right]
        image[top:bottom, left:right] = face_image
        #cv2.rectangle(image, (left, top), (right, bottom), (255,0,0), 2)
    #cv2.imwrite("img.jpg", image)
    print("[info] Getting best products for this face")
    imgGray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    h,w = imgGray.shape
    avg_color_per_row = numpy.average(imgGray, axis=0)
    avg_color = int(numpy.average(avg_color_per_row, axis=0))
    return avg_color

def processAzure(img_url):
    print(img_url)
    result = CF.face.detect(img_url)
    img = cv2.imread(img_url)
    print(result)
    top = result[0]["faceRectangle"]["top"]
    print(top)
    left = result[0]["faceRectangle"]["left"]
    width = result[0]["faceRectangle"]["width"]
    height = result[0]["faceRectangle"]["height"]
    print(img.shape)
    img = img[top:top+width,left:left+height]
    print(img.shape)
    print("[info] Getting best products for this face")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h,w = imgGray.shape
    avg_color_per_row = np.average(imgGray, axis=0)
    avg_color = int(np.average(avg_color_per_row, axis=0))
    return avg_color

def processData(dataList):
    data = []
    for d in dataList:
        avgColor = processImg(d[1]) 
        data.append((d[0], avgColor))
    data  =sorted(data,key=lambda l:l[1])
    return data