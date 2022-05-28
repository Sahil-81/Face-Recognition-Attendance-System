# Face-Recognition-Attendance-System

## About Project:
Online classses have become imoprtant part of our lives in recent days. A challenge in this system is tracking attendance which can be a hectic task sometimes. So a solution to this problem can be a system which automatically marks your attendane by recognizing your face.

## Technology Used:
Frontend : HTML,CSS.

Backend: Flask.

Databse: SQL.

Libraries: Face Detection (for face recognition),SQLAlchemy (for managing database queries with flask).

## Setup guide:

For using face-recognition you need to follow certain steps.

1. Install Microsoft Visual Studio Commmunity version from [here](https://visualstudio.microsoft.com/).
2. Launch the app and complete setup.
3. Install Desktop development C++ from the app.
4. Open command prompt and install cmake library using command pip install cmake.
5. Install dlib library using command pip install dlib.
6. Finally install face-recognition library using command pip install face-recognintion.

## Insatlling libraries:

All the libraries required for web app to run are mentioned in requirements.txt. To install them follow these steps:
1. Open command prompt.
2. Browse to the folder where the project is located.
3. Use command pip install -r requirements.txt. This will install all libraries mentioned in requirements.txt file.

## Crating database:

1. Open command prompt.
2. Browse to the folder where the project is located.
3. Use following commands to create database files.

python

from app import db

db.create_all()

from app1 import db

db.create_all()

exit()

Database file should appear in your project folder after these steps.

## Setting path to store images:

1. Go the profile_images folder folder under static folder.
2. Copy entire path for this folder.
3. In app_student.py file there is a variable app_config["UPLOAD_FOLDER"]. Assign this link as string to this variable.

## Launch app:
 
After you are done with all steps mentioned above you can run app_student file(for student interface), app_teacher file(for teacher interface). You will get a local host link in the terminal. Just open that link in browser to use the app.

