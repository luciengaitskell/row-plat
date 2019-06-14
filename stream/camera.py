import cv2
import socket
import struct
import pickle
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

    def _start_cam(self):
        self.cam = cv2.VideoCapture(0)

        self.cam.set(3, 320)
        self.cam.set(4, 240)

    def wait_for_accept(self):
        self.conn, self.addr = self.socket.accept()

    def start(self, wait=False):
        self._start_cam()
        self._start_serv()

        if wait: self.wait_for_accept()

    def frame(self):
        ret, frame = self.cam.read()

        lower = np.array([17, 15, 100], dtype="uint8")
        upper = np.array([200, 200, 200], dtype="uint8")
        mask = cv2.inRange(frame, lower, upper)
        output = cv2.bitwise_and(frame, frame, mask=mask)

        frame = output

        result, frame = cv2.imencode('.jpg', frame, self.ENC_PARAM)
        data = pickle.dumps(frame, 0)
        size = len(data)

        self.conn.sendall(struct.pack(">L", size) + data)

    def close(self):
        self.cam.release()
