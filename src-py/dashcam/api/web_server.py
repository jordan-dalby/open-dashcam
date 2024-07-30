from flask import Flask, jsonify
from waitress import serve

class DashcamWebServer():
    def __init__(self, dashcam) -> None:
        self.app = Flask(__name__)
        self.dashcam = dashcam
        self.setup_routes()

    def setup_endpoints(self):
        @self.app.route('/start_recording', methods=['POST'])
        def start_recording():
            result, status_code = self.dashcam.start_recording()
            return jsonify(result), status_code

        @self.app.route('/stop_recording', methods=['POST'])
        def stop_recording():
            result, status_code = self.dashcam.stop_recording()
            return jsonify(result), status_code
        
        @self.app.route('/start_streaming', methods=['POST'])
        def start_streaming():
            result, status_code = self.dashcam.start_streaming()
            return jsonify(result), status_code
        
        @self.app.route('/stop_streaming', methods=['POST'])
        def stop_streaming():
            result, status_code = self.dashcam.stop_streaming()
            return jsonify(result), status_code

    def start_server(self):
        serve(self.app, host="0.0.0.0", port=5000)