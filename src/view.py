from flask import Flask, request, jsonify

class DashCamView:
    def __init__(self, presenter):
        self.app = Flask(__name__)
        self.presenter = presenter
        self.setup_routes()

    def setup_routes(self):
        self.app.route('/start', methods=['POST'])(self.presenter.start_recording)
        self.app.route('/stop', methods=['POST'])(self.presenter.stop_recording)
        self.app.route('/status', methods=['GET'])(self.presenter.get_status)
        self.app.route('/set_quality', methods=['POST'])(self.presenter.set_quality)
        self.app.route('/set_storage_limit', methods=['POST'])(self.presenter.set_storage_limit)

    def run(self, host, port, debug):
        self.app.run(host=host, port=port, debug=debug)