import cv2
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from threading import Thread, Event

# Set up logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = 'dashcam.log'
log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

# Add console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
logger.addHandler(console_handler)

# Verify logging is working
logger.debug("Logging initialized")

app = Flask(__name__)

class DashCam:
    def __init__(self):
        self.is_recording = False
        self.stop_event = Event()
        self.camera = None
        self.output = None
        self.clip_duration = 3 * 60  # 3 minutes per clip
        self.storage_limit = 1024 * 1024 * 1024  # 1 GB
        self.video_quality = {
            'resolution': (1920, 1080),
            'fps': 30,
            'bitrate': 1000000  # 1 Mbps
        }
        logger.info("DashCam instance initialized")

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stop_event.clear()
            Thread(target=self._record).start()
            logger.info("Recording started")
            return True
        logger.warning("Attempted to start recording while already recording")
        return False

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stop_event.set()
            logger.info("Recording stopped")
            return True
        logger.warning("Attempted to stop recording while not recording")
        return False

    def _record(self):
        logger.debug("Entering _record method")
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            logger.error("Failed to open camera")
            self.is_recording = False
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        while not self.stop_event.is_set():
            self._manage_storage()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = f"dashcam_{timestamp}.mp4"
            logger.debug(f"Creating new video file: {output_file}")
            
            self.output = cv2.VideoWriter(output_file, fourcc, self.video_quality['fps'], self.video_quality['resolution'])
            if not self.output.isOpened():
                logger.error(f"Failed to create video writer for {output_file}")
                break
            
            start_time = time.time()
            frames_written = 0
            while time.time() - start_time < self.clip_duration and not self.stop_event.is_set():
                ret, frame = self.camera.read()
                if ret:
                    frame = cv2.resize(frame, self.video_quality['resolution'])
                    self.output.write(frame)
                    frames_written += 1
                else:
                    logger.warning("Failed to read frame from camera")
                    break
            
            self.output.release()
            logger.debug(f"Clip {output_file} completed. Frames written: {frames_written}")
        
        if self.camera:
            self.camera.release()
        logger.debug("Exiting _record method")
        self.is_recording = False

    def _manage_storage(self):
        logger.debug("Managing storage")
        total_size = 0
        files = sorted(
            [f for f in os.listdir('.') if f.startswith('dashcam_') and f.endswith('.mp4')],
            key=os.path.getctime
        )
        
        for file in files:
            total_size += os.path.getsize(file)
            
            if total_size > self.storage_limit:
                logger.info(f"Removing old file: {file}")
                os.remove(file)
                total_size -= os.path.getsize(file)
            else:
                break

    def set_video_quality(self, resolution=None, fps=None, bitrate=None):
        logger.info(f"Updating video quality. Resolution: {resolution}, FPS: {fps}, Bitrate: {bitrate}")
        if resolution:
            self.video_quality['resolution'] = tuple(resolution)
        if fps:
            self.video_quality['fps'] = fps
        if bitrate:
            self.video_quality['bitrate'] = bitrate
        return self.video_quality

dashcam = DashCam()

@app.route('/start', methods=['POST'])
def start_recording():
    logger.debug("Received start recording request")
    if dashcam.start_recording():
        return jsonify({"status": "Recording started"}), 200
    else:
        return jsonify({"status": "Already recording"}), 400

@app.route('/stop', methods=['POST'])
def stop_recording():
    logger.debug("Received stop recording request")
    if dashcam.stop_recording():
        return jsonify({"status": "Recording stopped"}), 200
    else:
        return jsonify({"status": "Not recording"}), 400

@app.route('/status', methods=['GET'])
def get_status():
    logger.debug("Received status request")
    status = "Recording" if dashcam.is_recording else "Not Recording"
    return jsonify({
        "status": status,
        "video_quality": dashcam.video_quality,
        "storage_limit": dashcam.storage_limit
    }), 200

@app.route('/set_quality', methods=['POST'])
def set_quality():
    logger.debug("Received set quality request")
    data = request.json
    new_quality = dashcam.set_video_quality(
        resolution=data.get('resolution'),
        fps=data.get('fps'),
        bitrate=data.get('bitrate')
    )
    return jsonify({"status": "Video quality updated", "new_settings": new_quality}), 200

@app.route('/set_storage_limit', methods=['POST'])
def set_storage_limit():
    logger.debug("Received set storage limit request")
    data = request.json
    if 'limit' in data:
        dashcam.storage_limit = int(data['limit'])
        logger.info(f"Storage limit updated to {dashcam.storage_limit}")
        return jsonify({"status": "Storage limit updated", "new_limit": dashcam.storage_limit}), 200
    else:
        logger.warning("Invalid set storage limit request")
        return jsonify({"status": "Invalid request"}), 400

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=5000, debug=True)