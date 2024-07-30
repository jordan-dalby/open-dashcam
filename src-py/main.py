'''
Dashcam - Class to manage the dashcam operations, start, stop, etc...
FileStreamer - Class to manage streaming video to files
MJPEGStreamer - Class to manage streaming video to MJPEG
DashcamWebServer - Class to manage the web server for the dashcam, has all of the endpoints
StorageManager - Class to manage the storage of the dashcam, deleting old files, etc...
'''
from dashcam.dashcam import Dashcam
from dashcam.api.web_server import DashcamWebServer

if __name__ == "__main__":
    dashcam = Dashcam()
    dashcam.start_recording()
    dashcam.start_streaming()

    server = DashcamWebServer(dashcam=dashcam)
    server.start_server()