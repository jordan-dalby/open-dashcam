from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import CircularOutput
from picamera2 import Picamera2, Preview
from threading import Event
import logging
import time
import io

class DashCamModel:
    def __init__(self):
        self.is_recording = False
        self.is_streaming = False
        self.stop_recording_event = Event()
        self.stop_streaming_event = Event()
        self.picam2 = None
        self.clip_duration = 3 * 60  # 3 minutes per clip
        self.storage_limit = 1024 * 1024 * 1024  # 1 GB
        self.video_quality = {
            'resolution': (1920, 1080),
            'fps': 30,
            'bitrate': 10000000  # 10 Mbps
        }
        self.stream_video_quality = {
            'resolution': (640, 480),
            'fps': 30,
            'bitrate': 5000000  # 5 Mbps
        }
        self.camera_controls = {
            'Brightness': 0,
            'Contrast': 1,
            'Saturation': 1,
            'Sharpness': 1,
            'ExposureTime': 0,  # 0 for auto
            'AnalogueGain': 1.0,
            'AeEnable': True,  # Enable auto-exposure
            'AwbEnable': True,  # Enable auto white balance
        }

        self.logger = logging.getLogger(__name__)
        self.initialize_camera()

    def initialize_camera(self):
        if self.picam2 is None:
            self.picam2 = Picamera2()
            
            supported_controls = self.picam2.camera_controls
            config_controls = {"FrameRate": self.video_quality['fps']}
            for control, value in self.camera_controls.items():
                if control in supported_controls:
                    config_controls[control] = value
                else:
                    self.logger.warning(f"Control '{control}' is not supported by this camera.")

            video_config = self.picam2.create_video_configuration(
                main={"size": self.video_quality['resolution']},
                lores={"size": self.stream_video_quality['resolution']},
                controls=config_controls
            )

            try:
                self.picam2.configure(video_config)
                self.picam2.start_preview(Preview.NULL)
                self.picam2.start()
                time.sleep(2)  # Allow auto focus and exposure to settle
                self.logger.info("Camera initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing camera: {str(e)}")
                raise

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stop_recording_event.clear()
            return True
        return False

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stop_recording_event.set()
            return True
        return False

    def start_streaming(self):
        if not self.is_streaming:
            self.is_streaming = True
            self.stop_streaming_event.clear()
            return True
        return False

    def stop_streaming(self):
        if self.is_streaming:
            self.is_streaming = False
            self.stop_streaming_event.set()
            return True
        return False

    def get_stream_output(self):
        if self.stream_output is None:
            self.stream_output = CircularOutput(buffersize=4*1024*1024)  # 4MB buffer
        return self.stream_output

    def get_stream_frame(self):
        with self.stream_lock:
            self.streaming_output = io.BytesIO()
            self.picam2.capture_file(self.streaming_output, format='jpeg')
            frame = self.streaming_output.getvalue()
        return frame

    def set_video_quality(self, resolution=None, fps=None, bitrate=None):
        if resolution:
            self.video_quality['resolution'] = tuple(resolution)
        if fps:
            self.video_quality['fps'] = fps
        if bitrate:
            self.video_quality['bitrate'] = bitrate
        
        # Reconfigure camera if it's already initialized
        if self.picam2:
            video_config = self.picam2.create_video_configuration(
                main={"size": self.video_quality['resolution']},
                controls={"FrameRate": self.video_quality['fps']}
            )
            self.picam2.configure(video_config)
        
        return self.video_quality

    def set_camera_controls(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.camera_controls:
                self.camera_controls[key] = value
        
        # Apply new controls if camera is already initialized
        if self.picam2:
            self.picam2.set_controls(self.camera_controls)
        
        return self.camera_controls

    def set_storage_limit(self, limit):
        self.storage_limit = limit

    def get_status(self):
        return {
            "status": "Recording" if self.is_recording else "Not Recording",
            "video_quality": self.video_quality,
            "camera_controls": self.camera_controls,
            "storage_limit": self.storage_limit
        }
    
    def get_camera_info(self):
        if self.picam2:
            return {
                "supported_controls": self.picam2.camera_controls,
                "current_config": self.picam2.camera_config
            }
        return None