import time
import ustruct
import _thread

from machine import I2C, Pin

from devices.ssd1306 import SSD1306_I2C
#from lib.xa1110 import XA1110
#from lib.micropygps import MicropyGPS
#from lib import bno055
from devices.rfm69 import RFM69


LOOP_PERIOD = 50

# Chip communication setup:
i2c_bus = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))

# Device setup:
display = SSD1306_I2C(128, 64, i2c_bus, 0x3D)

radio = RFM69(12, 27, baudrate=5000000)

'''
gns = XA1110(i2c=i2c_bus)
gns.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
gns.read_all_data()  # Clear buffer so that we know that data that followings is current
gns_data = MicropyGPS(location_formatting='dd')

imu = bno055.BNO055(i2c_bus)'''

# Buttons -- NOTE: Pull Ups do not seem to work on these pins: 36, 39, 34; used external pull-up
B_UP = Pin(36, Pin.IN, Pin.PULL_UP)
B_DOWN = Pin(4, Pin.IN, Pin.PULL_UP)
B_LEFT = Pin(39, Pin.IN, Pin.PULL_UP)
B_RIGHT = Pin(34, Pin.IN, Pin.PULL_UP)

B_ENB = Pin(14, Pin.IN, Pin.PULL_UP)
B_ALT = Pin(32, Pin.IN, Pin.PULL_UP)


# Shared variables:
running = True
ang = None
pos = (0, b'-', 0, b'-')


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
    data = radio.receive(timeout=0.1)  # Data seems to be incorrect after send -- need to revise encoding for errors?
    if isinstance(data, bytes):
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

    display.text("{}".format(B_UP.value()), 16, 28)

    display.text("{} | {}".format(B_LEFT.value(), B_RIGHT.value()), 0, 42)

    display.text("{}".format(B_DOWN.value()), 16, 56)

    display.text("{} | {}".format(B_ENB.value(), B_ALT.value()), 64, 42)

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
        t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
        sleep = LOOP_PERIOD - t_elapsed
        if sleep > 0:
            time.sleep_ms(sleep)
        else:
            print("CLOCK STRETCHING")
finally:
    running = False
    print("stopping")
    radio.close()
