from dashcam.streamers.base_streamer import BaseStreamer
from picamera2.encoders import H264Encoder

class FileStreamer(BaseStreamer):
    def __init__(self, settings: dict) -> None:
        super().__init__(settings, H264Encoder())

    def start(self) -> bool:
        return super().start()

    def stop(self) -> bool:
        return super().stop()

    def set_settings(self, settings: dict) -> None:
        super().set_settings(settings)

    def _start(self) -> None:
        super()._start()
        while not self.stop_event.is_set():
            pass
        print("FileStreamer stopped")