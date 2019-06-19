import cv2
from imutils.video import VideoStream
import socket
import struct
import pickle
import time
import imutils
import numpy as np


class CameraServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ENC_PARAM = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        self.conn = None
        self.addr = None

    def _start_serv(self):
        self.socket.bind(('', 8485))
        print('Socket bind complete')
        self.socket.listen(10)
        print('Socket now listening')

    def _start_cam(self, pi_cam):
        self.cam = VideoStream(usePiCamera=True, resolution=(1640, 922), framerate=15).start()
        time.sleep(2.0)

    def wait_for_accept(self):
        self.conn, self.addr = self.socket.accept()

    def start(self, pi_cam=True, wait=False):
        self._start_cam(pi_cam)
        self._start_serv()

        if wait: self.wait_for_accept()

    def frame(self):
        frame = self.cam.read()

        #lower = np.array([17, 15, 100], dtype="uint8")
        #upper = np.array([200, 200, 200], dtype="uint8")
        #mask = cv2.inRange(frame, lower, upper)
        #output = cv2.bitwise_and(frame, frame, mask=mask)
        #frame = output

        frame = imutils.resize(frame, height=240)

        result, frame = cv2.imencode('.jpg', frame, self.ENC_PARAM)
        data = pickle.dumps(frame, 0)
        size = len(data)

        self.conn.sendall(struct.pack(">L", size) + data)

    def close(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.cam.stop()
