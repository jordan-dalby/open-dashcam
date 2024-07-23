from cam import Camera

if __name__ == "__main__":
    camera = Camera(debug=True, resolution=(1920, 1080), framerate=30)
    print(camera.list_available_cameras())
    
    camera.record()
    camera.end_record()