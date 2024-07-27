import os
import time
from flask import jsonify, request
from threading import Thread
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

class DashCamPresenter:
    def __init__(self, model, logger):
        self.model = model
        self.logger = logger
        self.recordings_folder = "recordings"
        self.recording_thread = None

        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)
            self.logger.info(f"Created recordings folder: {self.recordings_folder}")

    def start_recording(self):
        self.logger.debug("Received start recording request")
        if self.model.start_recording():
            self.recording_thread = Thread(target=self._record)
            self.recording_thread.start()
            return jsonify({"status": "Recording started"}), 200
        else:
            return jsonify({"status": "Already recording"}), 400

    def stop_recording(self):
        self.logger.debug("Received stop recording request")
        if self.model.stop_recording():
            if self.recording_thread:
                self.recording_thread.join()
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
        self.logger.info(f"Video quality updated: {new_quality}")
        return jsonify({"status": "Video quality updated", "new_settings": new_quality}), 200

    def set_camera_controls(self):
        self.logger.debug("Received set camera controls request")
        data = request.json
        new_controls = self.model.set_camera_controls(**data)
        self.logger.info(f"Camera controls updated: {new_controls}")
        return jsonify({"status": "Camera controls updated", "new_settings": new_controls}), 200

    def set_storage_limit(self):
        self.logger.debug("Received set storage limit request")
        data = request.json
        if 'limit' in data:
            new_limit = int(data['limit'])
            self.model.set_storage_limit(new_limit)
            self.logger.info(f"Storage limit updated to {new_limit}")
            return jsonify({"status": "Storage limit updated", "new_limit": new_limit}), 200
        else:
            self.logger.warning("Invalid set storage limit request")
            return jsonify({"status": "Invalid request"}), 400

    def _record(self):
        self.logger.debug("Entering _record method")
        try:
            # Configure camera
            video_config = self.model.picam2.create_video_configuration(
                main={"size": self.model.video_quality['resolution']},
                controls={"FrameRate": self.model.video_quality['fps']}
            )
            self.model.picam2.configure(video_config)
            
            # Apply camera controls
            #self.model.picam2.set_controls(self.model.camera_controls)
            
            while not self.model.stop_event.is_set():
                self._manage_storage()
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_file = os.path.join(self.recordings_folder, f"dashcam_{timestamp}.mp4")
                self.logger.debug(f"Creating new video file: {output_file}")
                
                encoder = H264Encoder(bitrate=self.model.video_quality['bitrate'])
                output = FfmpegOutput(output_file)

                self.model.picam2.start_recording(encoder, output)
                
                start_time = time.time()
                while time.time() - start_time < self.model.clip_duration and not self.model.stop_event.is_set():
                    time.sleep(1)  # Sleep for 1 second to reduce CPU usage
                
                self.model.picam2.stop_recording()
                self.logger.debug(f"Clip {output_file} completed.")
                
                # Check if we need to update camera settings
                self._update_camera_settings()
        
        except Exception as e:
            self.logger.error(f"Error in recording: {str(e)}")
        finally:
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
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            if total_size > self.model.storage_limit:
                self.logger.info(f"Removing old file: {file}")
                os.remove(file_path)
                total_size -= file_size
            else:
                break

    def _update_camera_settings(self):
        # This method can be called to update camera settings if they've been changed
        # during recording. For now, it's a placeholder for potential future use.
        pass

    def get_recordings(self):
        self.logger.debug("Received get recordings request")
        recordings = [f for f in os.listdir(self.recordings_folder) if f.endswith('.mp4')]
        recordings.sort(key=lambda x: os.path.getctime(os.path.join(self.recordings_folder, x)), reverse=True)
        return jsonify({"recordings": recordings}), 200

    def delete_recording(self):
        self.logger.debug("Received delete recording request")
        data = request.json
        if 'filename' in data:
            filename = data['filename']
            file_path = os.path.join(self.recordings_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted recording: {filename}")
                return jsonify({"status": "Recording deleted"}), 200
            else:
                return jsonify({"status": "File not found"}), 404
        else:
            return jsonify({"status": "Invalid request"}), 400
