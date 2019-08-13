import time
import ustruct
import _thread

from machine import I2C, Pin

from devices.ssd1306 import SSD1306_I2C
from devices.xa1110 import XA1110
from devices.micropygps import MicropyGPS
from devices import bno055
from devices.rfm69 import RFM69
from platform import Platform

LOOP_PERIOD = 1000


plat = Platform('b')


try:
    plat.setup()
    while plat.running:
        loop_start = time.ticks_ms()  # Loop timer

        # Action:
        print(plat.heartbeat())

        # Handle loop sleep, based on elapsed time:
        t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
        sleep = LOOP_PERIOD - t_elapsed
        if sleep > 0:
            time.sleep_ms(sleep)
        else:
            print("CLOCK STRETCHING ", sleep)
finally:
    plat.close()
