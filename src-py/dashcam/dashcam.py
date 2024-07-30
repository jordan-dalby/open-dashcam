from dashcam.streamers.mjpeg_streamer import MJPEGStreamer
from dashcam.streamers.file_streamer import FileStreamer
from libcamera import Transform
from picamera2 import Picamera2
import time

class Dashcam():
    def __init__(self) -> None:
        self.settings = {
            'recording': {
                'resolution': (1920, 1080),
                'fps': 30,
                'bitrate': 10000000, # 10Mbps
                'extension': 'mp4',
                'directory': 'recordings',
                'clip_duration': 3 * 60, # 3 minutes per clip
            },
            'streaming': {
                'resolution': (1280, 720),
                'fps': 15,
                'bitrate': 5000000, # 5Mbps
            }
        }
        self.picam2 = None
        self.filestreamer = FileStreamer(self, self.settings['recording'])
        self.mjpegstreamer = MJPEGStreamer(self, self.settings['streaming'])

        print(self.filestreamer.is_streaming)

        self.initialise_camera()

    def initialise_camera(self) -> None:
        if self.picam2 is None:
            self.picam2 = Picamera2()
            video_config = self.picam2.create_video_configuration(
                main={"size": self.settings['recording']['resolution'], "format": "RGB888"},
                lores={"size": self.settings['streaming']['resolution'], "format": "YUV420"},
                transform=Transform(vflip=True, hflip=True),
            )

            try:
                self.picam2.configure(video_config)
                self.picam2.start_preview()
                self.picam2.start()

                # start_recording will start the filestreamer encoder, we don't need to do it manually
                self.picam2.start_encoder(self.mjpegstreamer.encoder)

                time.sleep(2)  # Allow auto focus and exposure to settle
            except Exception as e:
                raise Exception(f"Error initializing camera: {str(e)}")

    def start_recording(self):
        return self.filestreamer.start()

    def stop_recording(self):
        return self.filestreamer.stop()

    def start_streaming(self):
        return self.mjpegstreamer.start()

    def stop_streaming(self):
        return self.mjpegstreamer.stop()
    
    def set_recording_settings(self, settings: dict):
        return self.filestreamer.set_settings(settings)

    def set_streaming_settings(self, settings: dict):
        return self.mjpegstreamer.set_settings(settings)