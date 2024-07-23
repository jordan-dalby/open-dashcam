import cv2
from datetime import datetime

class Camera():
    def __init__(self, debug=False, resolution=(640, 480), framerate=30):
        self.debug = debug

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, resolution[0])
        self.cap.set(4, resolution[1])

        self.resolution = resolution
        self.framerate = framerate

        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        pass

    def record(self, write_time=True, write_date=True):
        start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(start_time)
        out = cv2.VideoWriter('output.mp4', self.fourcc, self.framerate, self.resolution)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            current_time = datetime.now().strftime(' '.join(['%Y-%m-%d' if write_date else '', '%H:%M:%S' if write_time else '']))

            cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
            out.write(frame)

            if self.debug:
                cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        out.release()

    def end_record(self):
        self.cap.release()
        cv2.destroyAllWindows()