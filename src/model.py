from picamera2 import Picamera2
from threading import Event
import time

class DashCamModel:
    def __init__(self):
        self.is_recording = False
        self.stop_event = Event()
        self.picam2 = None
        self.encoder = None
        self.output = None
        self.clip_duration = 3 * 60  # 3 minutes per clip
        self.storage_limit = 1024 * 1024 * 1024  # 1 GB
        self.video_quality = {
            'resolution': (1920, 1080),
            'fps': 30,
            'bitrate': 10000000  # 10 Mbps
        }
        self.camera_controls = {
            'Brightness': 0,
            'Contrast': 1,
            'Saturation': 1,
            'Sharpness': 1,
            'ExposureTime': 0,  # 0 for auto
            'AnalogueGain': 1.0,
            'AeExposureMode': 0,  # 0 for normal, 1 for short
            'AwbMode': 0,  # 0 for auto
            'NoiseReductionMode': 2  # 2 for fast
        }
        self.initialize_camera()

    def initialize_camera(self):
        if self.picam2 is None:
            self.picam2 = Picamera2()
            video_config = self.picam2.create_video_configuration(
                main={"size": self.video_quality['resolution']},
                controls={"FrameRate": self.video_quality['fps']}
            )
            self.picam2.configure(video_config)
            self.picam2.set_controls(self.camera_controls)
            self.picam2.start_preview()

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stop_event.clear()
            if not self.picam2.started:
                self.picam2.start()
                time.sleep(0.1)  # Short delay to ensure camera is ready
            return True
        return False

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stop_event.set()
            return True
        return False

    def set_video_quality(self, resolution=None, fps=None, bitrate=None):
        if resolution:
            self.video_quality['resolution'] = tuple(resolution)
        if fps:
            self.video_quality['fps'] = fps
        if bitrate:
            self.video_quality['bitrate'] = bitrate
        return self.video_quality

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
