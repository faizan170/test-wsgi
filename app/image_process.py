from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2, os, time, csv

# Load face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


def rgbToGray(col):
    rgbToGrayVal = 0.2989 * col[0] + 0.5870 * col[1] + 0.1140 * col[2]
    return rgbToGrayVal


def averageColor(img):
    # RGB average to Gray
    avg_color_per_row = np.average(img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return int(rgbToGray(avg_color))


def resizeImage(image):
    h, w, c = image.shape
    if h < 800 and w < 800:
        factor = 1
        small_frame = image.copy()
    elif h < 1500 and w < 1500:
        small_frame = cv2.resize(image, (0, 0), fx=0.50, fy=0.50)
    elif h < 2500 and w < 2500:
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    else:
        small_frame = cv2.resize(image, (0, 0), fx=0.20, fy=0.20)
    return small_frame
# Detect face
def detectFace(imgPath):
    # Load image from path
    print("img path in detect face:", imgPath)
    image = cv2.imread(imgPath)
    print("IMG:SHAPE:", image.shape)
    image = resizeImage(image)
    img = image.copy()
    print("ImageShape:", image.shape)
    # Convert to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale image
    rects = detector(gray, 1)

    rectsN = []
    # loop over the face detections
    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # convert dlib's rectangle to a OpenCV-style bounding box
        # [i.e., (x, y, w, h)], then draw the face bounding box
        (x, y, w, h) = face_utils.rect_to_bb(rect)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        for i in range(0, 27):
            cv2.circle(image,(shape[i][0], shape[i][1]), 2, (0,255,0), -1)
            rectsN.append((shape[i][0], shape[i][1]))

        # Convert points list to numpy array
        pts = np.array(rectsN)

        # Get bounding reactangle for points
        rect = cv2.boundingRect(pts)
        x,y,w,h = rect
        # Crop rectangle
        croped = img[y:y+h, x:x+w].copy()

        ## (2) make mask
        pts = pts - pts.min(axis=0)

        mask = np.zeros(croped.shape[:2], np.uint8)
        cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
        


        ## (3) do bit-op
        dst = cv2.bitwise_and(croped, croped, mask=mask)
        return {"status" : "found", "img" : dst}
    return {"status" : "failed"}


def getAvgColor(imgPath):
    print("Img Path in Get AVG:", imgPath)
    face = detectFace(imgPath)
    # If no face found. Return None
    if face["status"] == "failed":
        print("No face found")
        return None
    else:
        face = face["img"]
    # If face exists, continue processing
    avgColor = averageColor(face)
    return avgColor