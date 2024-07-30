from dashcam.streamers.base_streamer import BaseStreamer
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time
import os

class FileStreamer(BaseStreamer):
    def __init__(self, dashcam, settings: dict) -> None:
        super().__init__(dashcam, settings, H264Encoder(settings['bitrate']))
        self.directory = settings['directory']
        self.extension = settings['extension']
        self.clip_duration = settings['clip_duration']

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()

    def set_settings(self, settings: dict) -> None:
        super().set_settings(settings)

    def _get_next_file_name(self) -> str:
        return f"dashcam_{time.strftime('%Y%m%d-%H%M%S')}.{self.extension}"

    def _start(self) -> None:
        super()._start()
        while not self.stop_event.is_set():
            try:
                file_name = self._get_next_file_name()
                print(f"Clip started: {file_name}")

                output = FfmpegOutput(os.path.join(self.directory, file_name))
                self.dashcam.picam2.start_recording(self.encoder, output)

                start_time = time.time()
                # Wait for clip_duration to be met
                while time.time() - start_time < self.clip_duration and not self.stop_event.is_set():
                    time.sleep(1) # CPU friendly sleep

                # Stop the current clip
                self.dashcam.picam2.stop_recording()
                print(f"Clip finished: {file_name}")

                # TODO: Improve the logic here, this will cause clips to have a brief gap between them
                # Not ideal for a dashcam
            finally:
                self.dashcam.picam2.stop_recording()
        print("FileStreamer stopped")
        self.is_streaming = False