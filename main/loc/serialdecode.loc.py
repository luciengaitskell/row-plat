import serial

s = serial.Serial('/dev/tty.usbserial-A4006DBQ', 115200)

while True:
    l = s.readline()
    l = l[:-1]  # Remove last char (newline)
    print(list(l))

