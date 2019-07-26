from machine import I2C, Pin
from devices.ssd1306 import SSD1306_I2C
import time
import random

com = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))
s = SSD1306_I2C(128, 32, com)

s.fill(0)
s.text("Row Harder!", 0, 14)


BWIDTH = 20

while True:
    s.fill_rect(128 - BWIDTH, 0, BWIDTH, 32, 0)
    s.rect(128 - BWIDTH, 0, BWIDTH, 32, 1)

    BHEIGHT = random.randint(1, 32)
    s.fill_rect(128-BWIDTH, BHEIGHT, BWIDTH, 32-BHEIGHT, 1)
    s.show()
    time.sleep_ms(100)

