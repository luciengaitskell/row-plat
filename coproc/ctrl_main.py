import time
import ustruct
import _thread

from machine import I2C, Pin

from platform import Platform, SSD1306_I2C

plat = Platform('r', display=False)
plat.display = SSD1306_I2C(128, 64, plat.i2c_bus, 0x3D)
LOOP_PERIOD = 1000

# Buttons -- NOTE: Pull Ups do not seem to work on these pins: 36, 39, 34; used external pull-up
B_UP = Pin(36, Pin.IN, Pin.PULL_UP)
B_DOWN = Pin(4, Pin.IN, Pin.PULL_UP)
B_LEFT = Pin(39, Pin.IN, Pin.PULL_UP)
B_RIGHT = Pin(34, Pin.IN, Pin.PULL_UP)

B_ENB = Pin(14, Pin.IN, Pin.PULL_UP)
B_ALT = Pin(32, Pin.IN, Pin.PULL_UP)


# Shared variables:

last_success = None


def recv_data():
    pass


def update_display():
    global pos
    plat.display.fill(0)
    #display.rect(0, 0, 128, 32, 1)

    # plat.display.text(str(time.ticks_diff(time.ticks_ms(), )), 0, 0)
    '''plat.display.text(
        "{:.2f} {}, {:.2f} {}".format(
            pos[0], pos[1].decode(), pos[2], pos[3].decode()),
        0, 14)'''

    plat.display.text("{}".format(B_UP.value()), 16, 28)

    plat.display.text("{} | {}".format(B_LEFT.value(), B_RIGHT.value()), 0, 42)

    plat.display.text("{}".format(B_DOWN.value()), 16, 56)

    plat.display.text("{} | {}".format(B_ENB.value(), B_ALT.value()), 64, 42)

    plat.display.show()


def main():
    # _thread.start_new_thread(loop_read_gns, ())
    try:
        plat.setup()
        while plat.running:
            loop_start = time.ticks_ms()  # Loop timer

            # Action:
            hb = plat.heartbeat()
            print("HB: ", hb)
            print("RAW: ", hb.to_raw)
            print("LIST: ", list(hb.to_raw))

            #recv_data()
            #update_display()

            # Handle loop sleep, based on elapsed time:
            t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
            sleep = LOOP_PERIOD - t_elapsed
            if sleep > 0:
                time.sleep_ms(sleep)
            else:
                print("CLOCK STRETCHING ", sleep)
            print("--")
    finally:
        plat.close()
