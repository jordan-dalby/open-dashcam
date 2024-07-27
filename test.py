from picamera2 import Picamera2
import time
import numpy as np

def test_picamera2():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    
    picam2.start()
    time.sleep(2)  # Give the camera time to adjust
    
    metadata = picam2.capture_metadata()
    print("Camera metadata:", metadata)
    
    image = picam2.capture_array()
    print("Captured image shape:", image.shape)
    print("Captured image dtype:", image.dtype)
    
    picam2.capture_file("picamera2_test.jpg")
    print("Image saved as 'picamera2_test.jpg'")
    
    picam2.stop()
    print("Camera test complete")

if __name__ == "__main__":
    test_picamera2()
