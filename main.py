import cv2
import pickle
import cvzone
import numpy as np
import mysql.connector
import pandas as pd

# Video feed
cap = cv2.VideoCapture('test1.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 500, 250

prevSpaceCounter = -1

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='qwe26600099',
    database='park'
)
cursor = conn.cursor()
def checkParkingSpace(imgPro):
    global prevSpaceCounter
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)


        if count < 12500:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))


    if spaceCounter != prevSpaceCounter:
        cursor.execute("INSERT INTO parkiinglot (name, capacity, reps, ava) VALUES (%s, %s, %s, %s)",
                       ('殘障車位', 2, spaceCounter, len(posList)-spaceCounter))
        conn.commit()
        prevSpaceCounter = spaceCounter

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    cv2.waitKey(10)

# Clean up
conn.close()
cap.release()
cv2.destroyAllWindows()
