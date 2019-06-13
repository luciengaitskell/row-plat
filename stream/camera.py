import cv2
import io
import socket
import struct
import time
import pickle
import zlib
import numpy as np

DEBUG = False

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind(('',8485))
print('Socket bind complete')
client_socket.listen(10)
print('Socket now listening')


conn,addr=client_socket.accept()

cam = cv2.VideoCapture(0)

cam.set(3, 320);
cam.set(4, 240);

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

while True:
    ret, frame = cam.read()

    lower = np.array([17, 15, 100], dtype="uint8")
    upper = np.array([200, 200, 200], dtype="uint8")
    mask = cv2.inRange(frame, lower, upper)
    output = cv2.bitwise_and(frame, frame, mask=mask)

    frame = output

    result, frame = cv2.imencode('.jpg', frame, encode_param)
    # data = zlib.compress(pickle.dumps(frame, 0))
    data = pickle.dumps(frame, 0)
    size = len(data)

    if DEBUG: print("{}: {}".format(img_counter, size))
    conn.sendall(struct.pack(">L", size) + data)
    img_counter += 1

cam.release()
