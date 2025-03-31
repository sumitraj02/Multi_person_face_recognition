import os
import cv2
import torch
from flask import Flask, render_template, request, Response
from send_mail import prepare_and_send_email


cv2.setNumThreads(0)
cv2.ocl.setUseOpenCL(False)
# Initialize Flask app
app = Flask(__name__)
app.config["VIDEO_UPLOADS"] = "static/video"
app.config["ALLOWED_VIDEO_EXTENSIONS"] = ["MP4", "MOV", "AVI", "WMV", "WEBM"]

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Global variables
frames_buffer = []
vid_path = app.config["VIDEO_UPLOADS"] + '/input.mp4'
video_frames = cv2.VideoCapture(vid_path)
alert_sent = False

# Helper function to check video file
def allowed_video(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1]
    return extension.upper() in app.config["ALLOWED_VIDEO_EXTENSIONS"]

# Generate raw video frames
def generate_raw_frames():
    global video_frames
    while True:
        success, frame = video_frames.read()
        if success:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Generate processed frames with YOLOv5 detection
def generate_processed_frames():
    global video_frames, alert_sent
    while True:
        success, frame = video_frames.read()
        if success:
            results = model(frame,size=320)
            people_count = sum(1 for *xyxy, conf, cls in results.xyxy[0] if int(cls) == 0)

            # Draw bounding boxes
            for *xyxy, conf, cls in results.xyxy[0]:
                if int(cls) == 0:
                    cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 0, 0), 2)

            # Display people count
            cv2.putText(frame, f'Persons Detected: {people_count}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)

            # Send email alert if count > 3
            if people_count > 3 and not alert_sent:
                prepare_and_send_email(sender='it22064glbitm.ac.in',
                                       recipient='sumitkumar918403@gmail.com',
                                       subject='3 or more  people detected',
                                       message_text='More than 3 are people detected in video.',
                                       im0=frame)
                alert_sent = True

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_raw')
def video_raw():
    return Response(generate_raw_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_processed')
def video_processed():
    return Response(generate_processed_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit', methods=['POST'])
def submit_form():
    global vid_path, video_frames, frames_buffer, alert_sent
    if request.method == 'POST':
        if request.files:
            video = request.files['video']
            if video.filename == '' or not allowed_video(video.filename):
                return 'Invalid video file.'
            video.save(os.path.join(app.config['VIDEO_UPLOADS'], 'vid3.mp4'))
            video_frames = cv2.VideoCapture(vid_path)
            frames_buffer.clear()
            alert_sent = False
            return 'Video uploaded successfully.'
    return 'Error.'


#cv2.setNumThreads(0)


if __name__ == '__main__':
    app.run(debug=True)
    
 