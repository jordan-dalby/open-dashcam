from dashcam.streamers.base_streamer import BaseStreamer
from picamera2.encoders import H264Encoder
from dashcam.dashcam import Dashcam
import time

class FileStreamer(BaseStreamer):
    def __init__(self, dashcam: Dashcam, settings: dict) -> None:
        super().__init__(dashcam, settings, H264Encoder(settings['bitrate']))

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()

    def set_settings(self, settings: dict) -> None:
        super().set_settings(settings)

    def _start(self) -> None:
        super()._start()
        while not self.stop_event.is_set():
            try:
                self.dashcam.picam2.start_encoder(self.encoder)
                self.dashcam.picam2.start_recording()
                while not self.stop_event.is_set():
                    time.sleep(0.1)
            finally:
                self.dashcam.picam2.stop_recording()
        print("FileStreamer stopped")