from machine import I2C, Pin
import time
from lib import adafruit_bno055


i2c = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP), freq=100000)

sensor = adafruit_bno055.BNO055(i2c)

while True:
    print('Temperature: {} degrees C'.format(sensor.temperature()))
    print('Accelerometer (m/s^2): {}'.format(sensor.acceleration()))
    print('Magnetometer (microteslas): {}'.format(sensor.magnetic()))
    print('Gyroscope (deg/sec): {}'.format(sensor.gyroscope()))
    print('Euler angle: {}'.format(sensor.euler()))
    print('Quaternion: {}'.format(sensor.quaternion()))
    print('Linear acceleration (m/s^2): {}'.format(sensor.linear_acceleration()))
    print('Gravity (m/s^2): {}'.format(sensor.gravity()))
    print()

    time.sleep(1)
