import time
import ustruct
import _thread

from machine import I2C, Pin

from devices.ssd1306 import SSD1306_I2C
#from lib.xa1110 import XA1110
#from lib.micropygps import MicropyGPS
#from lib import bno055
from devices.rfm69 import RFM69


LOOP_PERIOD = 200

# Chip communication setup:
i2c_bus = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))

# Device setup:
display = SSD1306_I2C(128, 32, i2c_bus)

radio = RFM69(12, 27, baudrate=5000000)

'''
gns = XA1110(i2c=i2c_bus)
gns.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
gns.read_all_data()  # Clear buffer so that we know that data that followings is current
gns_data = MicropyGPS(location_formatting='dd')

imu = bno055.BNO055(i2c_bus)'''

# Shared variables:
running = True
ang = None
pos = None


'''
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
    ang = imu.euler()[0]'''


def recv_data():
    global pos, ang
    data = radio.receive()  # Data seems to be incorrect after send -- need to revise encoding for errors?
    ret = ustruct.unpack("dfsfs", data)
    ang = float(ret[0])
    pos = ret[1:]
    print(data)


def update_display():
    global pos
    display.fill(0)
    #display.rect(0, 0, 128, 32, 1)

    display.text(str(ang), 0, 0)
    display.text(
        "{:.2f} {}, {:.2f} {}".format(
            pos[0], pos[1].decode(), pos[2], pos[3].decode()),
        0, 14)
    display.show()


#_thread.start_new_thread(loop_read_gns, ())

try:
    radio.init(915.0)
    while running:
        loop_start = time.ticks_ms()  # Loop timer

        # Action:
        recv_data()
        update_display()

        # Handle loop sleep, based on elapsed time:
        sleep = time.ticks_diff(time.ticks_ms(), loop_start)
        if sleep > 0:
            time.sleep_ms(LOOP_PERIOD - sleep)
        else:
            print("CLOCK STRETCHING")
finally:
    running = False
    print("stopping")
    radio.close()
