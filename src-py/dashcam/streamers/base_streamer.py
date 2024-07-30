from picamera2.encoders import Encoder
from threading import Event, Thread

class BaseStreamer():
    def __init__(self, dashcam, settings: dict, encoder: Encoder) -> None:
        self.dashcam = dashcam
        self.settings = settings
        self.encoder = encoder
        self.dashcam.picam2.start_encoder(self.encoder)

        self.stop_event = Event()
        self.is_streaming = False

    def start(self):
        if self.is_streaming:
            return {"message": "Already streaming"}, 400
        self.stop_event.clear()
        Thread(target=self._start).start()
        return {"message": "Started streaming"}, 200

    def stop(self):
        if not self.is_streaming:
            return {"message": "Not streaming"}, 400
        self.stop_event.set()
        self.is_streaming = False
        return {"message": "Stopped streaming"}, 200

    def set_settings(self, settings: dict) -> None:
        self.settings = settings
    
    def _start(self) -> None:
        print("Started", type(self).__name__)
        self.is_streaming = True