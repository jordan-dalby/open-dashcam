from flask import Flask
from waitress import serve

class DashcamWebServer():
    def __init__(self, dashcam) -> None:
        self.app = Flask(__name__)
        self.dashcam = dashcam
        self.setup_routes()

    def setup_endpoints(self):
        self.app.route('/start_recording', methods=['POST'])(self.dashcam.start_recording)
        self.app.route('/stop_recording', methods=['POST'])(self.dashcam.stop_recording)
        self.app.route('/start_streaming', methods=['POST'])(self.dashcam.start_streaming)
        self.app.route('/stop_streaming', methods=['POST'])(self.dashcam.stop_streaming)

    def start_server(self):
        serve(self.app, host="0.0.0.0", port=5000)