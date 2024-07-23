import cv2
from threading import Event

class DashCamModel:
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

    def set_storage_limit(self, limit):
        self.storage_limit = limit

    def get_status(self):
        return {
            "status": "Recording" if self.is_recording else "Not Recording",
            "video_quality": self.video_quality,
            "storage_limit": self.storage_limit
        }