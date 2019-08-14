import time

from platform import Platform

LOOP_PERIOD = 1000


plat = Platform('b')


def main():
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
