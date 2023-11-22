import cv2
import easyocr
import os
import csv
import re
import time
from datetime import datetime

""" Writing Number plates recognised into List.csv (Resident dataset file) """

def markCars(name):
    with open('D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\List.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

""" REGEX and processing """

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
    string = string[:2] + re.sub(r"[ITOLZ]", replace, string[2:4]) + string[4:]

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
    string = string[:6] + re.sub(r"[ITOLZ]", replace, string[6:])
    return string


""" Residents dataset pre-processing using Cascade classifier """

plateCascade = cv2.CascadeClassifier("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\List.csv")
minArea = 500
count = 0
path = 'D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\CarsDataset'

for cl in os.listdir(path):
    img = cv2.imread(os.path.join(path, cl))
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

    for (x, y, w, h) in numberPlates:
        area = w * h
        if area > minArea:
            imgRoi = img[y:y + h, x:x + w]

    cv2.imwrite("D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\NumplateCropped_Sample\\" + str(count) + ".jpg", imgRoi)
    cv2.waitKey(500)
    count += 1

""" EasyOCR recognition model and CSV file creation """

path = 'D:\\SEM 7\\CSE4015 HCI PROJECT\\SMART ACCESS CONTROL FOR RESIDENT WITH TRANSFER LEARNING AND EASYOCR\\NumberPlateCropped'

for cl in os.listdir(path):
    img = cv2.imread(os.path.join(path, cl))

    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)
    if len(result) > 0:                     # Printing the result
        text = result[0][-2]
        res = numberplate(text)             # Apply regex to remove whitespaces and special characters
        print(res)
        if res != 0:
            markCars(res)                   # Add the list of cars dataset in the CSV file List
    else:
        print('No text found.')
    time.sleep(1)
