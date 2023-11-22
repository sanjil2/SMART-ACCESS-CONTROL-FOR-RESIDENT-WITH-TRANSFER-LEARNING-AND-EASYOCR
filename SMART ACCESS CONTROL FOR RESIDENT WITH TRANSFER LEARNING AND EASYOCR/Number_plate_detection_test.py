import time
import cv2
import easyocr
import re
import csv
from datetime import datetime
import pyfirmata

def markCarsLogbook(name):
    with open('D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\LogBookFile.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%d-%m-%Y %H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

def numberplate(string):
    # Convert the string into uppercase and remove special characters and whitespaces
    string = re.sub(r"[^A-Z0-9]", "", string.upper())

    # Check if the string is of length 10
    if len(string) != 10:
        return 0

    def repl(match):
        if match.group() == "I":
            return "T"

    string = re.sub(r"[I]", repl, string[0:2]) + string[2:]

    # Replace the 3rd and 4th characters using mapping
    def replace(match):
        if match.group() == "I":
            return "1"
        elif match.group() == "T":
            return "1"
        elif match.group() == "O":
            return "0"
        elif match.group() == "L":
            return "4"
        elif match.group() == "Z":
            return "2"

    string = string[:2] + re.sub(r"[IOLZ]", replace, string[2:4]) + string[4:]

    # Replace the 5th and 6th characters using mapping
    def repl56(match):
        if match.group() == "0":
            return "D"
        elif match.group() == "4":
            return "L"
        elif match.group() == "2":
            return "Z"
        elif match.group() == "1":
            return "I"

    string = string[:4] + re.sub(r"[0421]", repl56, string[4:6]) + string[6:]

    # Replace the last 4 characters using mapping
    string = string[:6] + re.sub(r"[IOLZ]", replace, string[6:])
    return string

""" Open camera to capture the test car image """

plateCascade = cv2.CascadeClassifier("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\haarcascade_russian_plate_number.xml")
videoCaptureObject = cv2.VideoCapture(0)
minArea = 500
flag1 = True

while flag1:
    ret, frame = videoCaptureObject.read()
    cv2.putText(frame, 'Press q to capture', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_4)


    imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)
    for (x, y, w, h) in numberPlates:
        area = w * h
        if area > minArea:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            imgRoi = frame[y:y + h, x:x + w]
    cv2.imshow("Number plate detection", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\SingleSampleTestBeforeCropping\\NewPicture.jpg", frame)
        flag1 = False
        videoCaptureObject.release()
        cv2.destroyAllWindows()

""" Apply Cascade Classifier for the test image """

frameWidth = 640  # Frame Width
franeHeight = 480  # Frame Height
minArea = 500

img = cv2.imread("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\SingleSampleTestBeforeCropping\\NewPicture.jpg")
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

for (x, y, w, h) in numberPlates:
    area = w * h
    if area > minArea:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        imgRoi = img[y:y + h, x:x + w]

cv2.imwrite("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\SingleSampleTest\\Testimg" + ".jpg", imgRoi)

""" EasyOCR recognition for test image """

reader = easyocr.Reader(['en'])
result = reader.readtext(imgRoi)
s = ""
if len(result) > 0:                     # Store the result
    text = result[0][-2]
    print(text)
    s = numberplate(text)               # Call the regex function to correct the output
    print(s)
    if s!=0:
        markCarsLogbook(s)                  # Entry of cars in the Logbook CSV file List
else:
    print('No text found.')

""" Integrating ARDUINO """

from pyfirmata import Arduino, SERVO
from time import sleep

port = 'COM12'
servo_pin = 10
board = Arduino(port)
board.digital[servo_pin].mode = SERVO

def rotateservo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)

flag_gate = 0

""" Compare with the resident dataset """

reader1 = csv.reader(open('D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\List.csv', 'r'))

while True:
    try:
        row1 = next(reader1)
        if row1[0] == s:
            print("WELCOME HOME! Open the gate")
            flag_gate = 1
    except StopIteration:
        break

led_pin1 = 8      # Green light
led_pin2 = 11     # Red light

# Set up the pins as outputs
board.digital[led_pin1].mode = pyfirmata.OUTPUT
board.digital[led_pin2].mode = pyfirmata.OUTPUT

# Initially red light
board.digital[led_pin1].write(0)          # Turn LED 1 off
board.digital[led_pin2].write(1)          # Turn LED 2 on (Red)

if flag_gate == 1:
    board.digital[led_pin1].write(1)      # Turn LED 1 on (Green)
    board.digital[led_pin2].write(0)      # Turn LED 2 off
    for i in range(0, 90):
        rotateservo(servo_pin, i)               # Rotate the servo motor if match found (GATE OPEN)

    time.sleep(4)

    board.digital[led_pin1].write(0)      # Turn LED 1 off
    board.digital[led_pin2].write(1)      # Turn LED 2 on (Red)

    for i in range(90, 0, -1):            # GATE CLOSE
        rotateservo(servo_pin, i)
else:
    board.digital[led_pin1].write(0)      # Turn LED 1 off
    board.digital[led_pin2].write(1)      # Turn LED 2 on (Red)
    print("Not a Resident")







