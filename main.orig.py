from machine import I2C, Pin
import time

from lib import bno055

com = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP), freq=100000)

b = bno055.BNO055(com)
#b.init(bno055.COMPASS_MODE)

while True:
    #print("Temp: {}, mag: {}".format(b.temperature(), b.linear_acceleration()))
    print(b.calibration_status)
    time.sleep_ms(500)
