import socket
import cv2
import pickle
import struct


PAYLOAD_SIZE = struct.calcsize(">L")


class RenderVideo:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.addr = addr

        self.conn = None

        self._data = b""

    def connect(self):
        self.socket.connect((self.addr, 8485))
        self.conn = self.socket.makefile('wb')

    def frame(self):
        while len(self._data) < PAYLOAD_SIZE:
            self._data += self.socket.recv(4096)

        packed_msg_size = self._data[:PAYLOAD_SIZE]
        self._data = self._data[PAYLOAD_SIZE:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(self._data) < msg_size:
            self._data += self.socket.recv(4096)
        frame_data = self._data[:msg_size]
        self._data = self._data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('ImageWindow', frame)
        cv2.waitKey(1)
