import cv2
import os
import time
from flask import jsonify, request
from threading import Thread

class DashCamPresenter:
    def __init__(self, model, logger):
        self.model = model
        self.logger = logger
        self.recordings_folder = "recordings"

        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)
            self.logger.info(f"Created recordings folder: {self.recordings_folder}")

    def start_recording(self):
        self.logger.debug("Received start recording request")
        if self.model.start_recording():
            Thread(target=self._record).start()
            return jsonify({"status": "Recording started"}), 200
        else:
            return jsonify({"status": "Already recording"}), 400

    def stop_recording(self):
        self.logger.debug("Received stop recording request")
        if self.model.stop_recording():
            return jsonify({"status": "Recording stopped"}), 200
        else:
            return jsonify({"status": "Not recording"}), 400

    def get_status(self):
        self.logger.debug("Received status request")
        return jsonify(self.model.get_status()), 200

    def set_quality(self):
        self.logger.debug("Received set quality request")
        data = request.json
        new_quality = self.model.set_video_quality(
            resolution=data.get('resolution'),
            fps=data.get('fps'),
            bitrate=data.get('bitrate')
        )
        return jsonify({"status": "Video quality updated", "new_settings": new_quality}), 200

    def set_storage_limit(self):
        self.logger.debug("Received set storage limit request")
        data = request.json
        if 'limit' in data:
            self.model.set_storage_limit(int(data['limit']))
            self.logger.info(f"Storage limit updated to {self.model.storage_limit}")
            return jsonify({"status": "Storage limit updated", "new_limit": self.model.storage_limit}), 200
        else:
            self.logger.warning("Invalid set storage limit request")
            return jsonify({"status": "Invalid request"}), 400

    def _record(self):
        self.logger.debug("Entering _record method")
        self.model.camera = cv2.VideoCapture(0)
        if not self.model.camera.isOpened():
            self.logger.error("Failed to open camera")
            self.model.is_recording = False
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        while not self.model.stop_event.is_set():
            self._manage_storage()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(self.recordings_folder, f"dashcam_{timestamp}.mp4")
            self.logger.debug(f"Creating new video file: {output_file}")
            
            self.model.output = cv2.VideoWriter(output_file, fourcc, self.model.video_quality['fps'], self.model.video_quality['resolution'])
            if not self.model.output.isOpened():
                self.logger.error(f"Failed to create video writer for {output_file}")
                break
            
            start_time = time.time()
            frames_written = 0
            while time.time() - start_time < self.model.clip_duration and not self.model.stop_event.is_set():
                ret, frame = self.model.camera.read()
                if ret:
                    frame = cv2.resize(frame, self.model.video_quality['resolution'])
                    self.model.output.write(frame)
                    frames_written += 1
                else:
                    self.logger.warning("Failed to read frame from camera")
                    break
            
            self.model.output.release()
            self.logger.debug(f"Clip {output_file} completed. Frames written: {frames_written}")
        
        if self.model.camera:
            self.model.camera.release()
        self.logger.debug("Exiting _record method")
        self.model.is_recording = False

    def _manage_storage(self):
        self.logger.debug("Managing storage")
        total_size = 0
        files = sorted(
            [f for f in os.listdir(self.recordings_folder) if f.startswith('dashcam_') and f.endswith('.mp4')],
            key=lambda x: os.path.getctime(os.path.join(self.recordings_folder, x))
        )
        
        for file in files:
            file_path = os.path.join(self.recordings_folder, file)
            total_size += os.path.getsize(file_path)
            
            if total_size > self.model.storage_limit:
                self.logger.info(f"Removing old file: {file}")
                os.remove(file_path)
                total_size -= os.path.getsize(file_path)
            else:
                break