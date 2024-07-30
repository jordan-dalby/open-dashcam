from picamera2.encoders import Encoder
from threading import Event
from flask import jsonify

class BaseStreamer():
    def __init__(self, settings: dict, encoder: Encoder) -> None:
        self.settings = settings
        self.encoder = encoder
        self.stop_event = Event()
        self.is_streaming = False

    def start(self):
        if self.is_streaming:
            self.stop_event.clear()
            self._start()
            return jsonify({"message": "Already streaming"}), 400
        self.is_streaming = True
        return jsonify({"message": "Started streaming"}), 200

    def stop(self):
        if not self.is_streaming:
            return jsonify({"message": "Not streaming"}), 400
        self.stop_event.set()
        self.is_streaming = False
        return jsonify({"message": "Stopped streaming"}), 200

    def set_settings(self, settings: dict) -> None:
        self.settings = settings
    
    def _start(self) -> None:
        print("Started ", type(self).__name__)