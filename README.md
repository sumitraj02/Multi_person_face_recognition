# Multiperson-face-recognition-
MPFR using yolo model .

Features

1.Face recognition using dlib and face_recognition

2.Supports processing images and videos

3.Dockerized environment for easy setup

4.Email notifications via Gmail API

5.Flask-based web interface

Multi-Person Face Recognition is a deep learning-based system for detecting and recognizing multiple faces in real time from images and videos.
This project leverages dlib and face_recognition libraries for facial embeddings and recognition, with Flask for serving the model.

Installation Guide
Step 1: Clone the Repository
git clone https://github.com/sumitkumar1203/Multi_Person_Face_Recognition.git

cd Multi_Person_Face_Recognition


Step 2: Set Up Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


Step 3: Upgrade Pip
pip install --upgrade pip


Step 4: Install Required Dependencies

pip install -r requirements.txt
Step 5: Install Additional System Libraries (Linux Users Only)

sudo apt update -y && sudo apt install ffmpeg libsm6 libxext6 -y
sudo apt install cmake libboost-all-dev -y
sudo apt install build-essential -y


Step 6: Install Gmail APIs for Email Alerts
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


Step 7: Generate Face Embeddings

python src/dlib_face_embeddings.py
Step 8: Run the Project

python -m flask --app src/app.py run --host=0.0.0.0
