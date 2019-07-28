import time
import ustruct
import _thread

from machine import I2C, Pin

from devices.ssd1306 import SSD1306_I2C
from devices.xa1110 import XA1110
from devices.micropygps import MicropyGPS
from devices import bno055
from devices.rfm69 import RFM69


LOOP_PERIOD = 200

# Chip communication setup:
i2c_bus = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))

# Device setup:
display = SSD1306_I2C(128, 32, i2c_bus)

gns = XA1110(i2c=i2c_bus)
gns.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
gns.read_all_data()  # Clear buffer so that we know that data that followings is current
gns_data = MicropyGPS(location_formatting='dd')

imu = bno055.BNO055(i2c_bus)

radio = RFM69(12, 27, baudrate=5000000)

# Shared variables:
running = True
ang = None


def loop_read_gns():
    global running
    try:
        while running:
            line = gns.read_line()

            for c in line:
                stat = gns_data.update(chr(c))
            time.sleep_ms(50)
    finally:
        running = False


def read_bno055():
    global ang
    ang = round(imu.euler()[0], 2)


def update_display():
    display.fill(0)
    #display.rect(0, 0, 128, 32, 1)

    display.text(str(ang), 0, 0)
    pos = gns_data.latitude, gns_data.longitude
    display.text("{:.2f} {}, {:.2f} {}".format(pos[0][0], pos[0][1], pos[1][0], pos[1][1]), 0, 14)
    display.show()


def send_data():
    pos = gns_data.latitude, gns_data.longitude
    data = ustruct.pack("dfsfs", ang, pos[0][0], pos[0][1], pos[1][0], pos[1][1])
    radio.send(data)


_thread.start_new_thread(loop_read_gns, ())

try:
    radio.init(915.0)
    while running:
        loop_start = time.ticks_ms()  # Loop timer

        # Action:
        read_bno055()
        update_display()
        send_data()

        # Handle loop sleep, based on elapsed time:
        sleep = time.ticks_diff(time.ticks_ms(), loop_start)
        if sleep > 0:
            time.sleep_ms(LOOP_PERIOD - sleep)
        else:
            print("CLOCK STRETCHING")
finally:
    running = False
    print("stopped")
    radio.close()
