import os
import cv2
import time
import numpy
from threading import Thread
from flask import jsonify, request, Response
from picamera2 import MappedArray
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import FfmpegOutput

class DashCamPresenter:
    def __init__(self, model, logger):
        self.model = model
        self.logger = logger
        self.recordings_folder = "recordings"
        self.recording_thread = None
        self.streaming_thread = None
        self.recording_encoder = H264Encoder(bitrate=self.model.video_quality['bitrate'])
        self.streaming_encoder = MJPEGEncoder(bitrate=self.model.stream_video_quality['bitrate'])

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

    def start_streaming(self):
        self.logger.debug("Received start streaming request")
        if self.model.start_streaming():
            self.streaming_thread = Thread(target=self._stream)
            self.streaming_thread.start()
            return jsonify({"status": "Streaming started"}), 200
        else:
            return jsonify({"status": "Already streaming"}), 400

    def stop_streaming(self):
        self.logger.debug("Received stop streaming request")
        if self.model.stop_streaming():
            if self.streaming_thread:
                self.streaming_thread.join()
            return jsonify({"status": "Streaming stopped"}), 200
        else:
            return jsonify({"status": "Not streaming"}), 400

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
            def apply_timestamp(request):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with MappedArray(request, "main") as m:
                    cv2.putText(m.array, timestamp, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            self.model.picam2.pre_callback = apply_timestamp

            while not self.model.stop_recording_event.is_set():
                self._manage_storage()
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_file = os.path.join(self.recordings_folder, f"dashcam_{timestamp}.mp4")
                self.logger.debug(f"Creating new video file: {output_file}")
                
                output = FfmpegOutput(output_file)

                self.model.picam2.start_recording(self.recording_encoder, output)
                
                start_time = time.time()
                while time.time() - start_time < self.model.clip_duration and not self.model.stop_recording_event.is_set():
                    time.sleep(1)  # Sleep for 1 second to reduce CPU usage
                
                self.model.picam2.stop_recording()
                self.logger.debug(f"Clip {output_file} completed.")
        
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

    def _stream(self):
        self.logger.debug("Entering _stream method")
        try:
            while not self.model.stop_streaming_event.is_set():
                time.sleep(0.1)  # Small delay to prevent busy-waiting
        except Exception as e:
            self.logger.error(f"Error in streaming: {str(e)}")
        finally:
            self.logger.debug("Exiting _stream method")
            self.model.is_streaming = False

def video_feed(self):
    self.logger.debug("Received video feed request")
    if not self.model.is_streaming:
        return jsonify({"error": "Streaming is not active"}), 400

    def generate():
        try:
            while self.model.is_streaming:
                buffer = self.model.picam2.capture_buffer("lores")
                h, w = self.model.stream_video_quality['resolution']
                buffer = numpy.frombuffer(buffer, dtype=numpy.uint8)[:w * h].reshape(h, w)

                # Encode the buffer as a JPEG image
                ret, jpeg = cv2.imencode('.jpg', buffer)
                if not ret:
                    self.logger.error("Failed to encode frame as JPEG")
                    continue

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                time.sleep(1 / self.model.stream_video_quality['fps'])
        except Exception as e:
            self.logger.error(f"Error in video feed: {str(e)}")

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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

    def lock_recording(self):
        self.logger.debug("Received lock recording request")
        data = request.json
        if 'filename' in data:
            filename = data['filename']
            file_path = os.path.join(self.recordings_folder, filename)
            if os.path.exists(file_path):
                os.chmod(file_path, "0o444")
                self.logger.info(f"Made {filename} read-only"), 200
                return jsonify({"status": "Success"})
            else:
                return jsonify({"status": "File not found"}), 404
        else:
            return jsonify({"status": "Invalid request"}), 400

    def unlock_recording(self):
        self.logger.debug("Received unlock recording request")
        data = request.json
        if 'filename' in data:
            filename = data['filename']
            file_path = os.path.join(self.recordings_folder, filename)
            if os.path.exists(file_path):
                os.chmod(file_path, "0o777") # maybe not 777
                self.logger.info(f"Made {filename} read and writeable"), 200
                return jsonify({"status": "Success"})
            else:
                return jsonify({"status": "File not found"}), 404
        else:
            return jsonify({"status": "Invalid request"}), 400
