from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from threading import Event

class DashCamModel:
    def __init__(self):
        self.is_recording = False
        self.stop_event = Event()
        self.picam2 = Picamera2()
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

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.stop_event.clear()
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

    def set_camera_controls(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.camera_controls:
                self.camera_controls[key] = value
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
