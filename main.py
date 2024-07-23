from cam import Camera

if __name__ == "__main__":
    camera = Camera(debug=True, resolution=(1920, 1080), framerate=30)
    camera.record()
    camera.end_record()