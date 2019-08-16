import time

from platform import Platform

LOOP_PERIOD = 200


plat = Platform('b')


def main():
    last_success = None
    try:
        plat.setup()
        while plat.running:
            loop_start = time.ticks_ms()  # Loop timer

            # Action:
            data = plat.radio.receive(timeout=0.1)
            # print(data)
            if isinstance(data, bytearray):
                print("\n")
                pak = plat.c.accept_bytes(data)
                print("RECEIVED (strength: {})".format(plat.radio.rssi))
                print(pak)
                last_success = time.ticks_ms()
            else:
                print("type: ", type(data))

            if last_success is not None and time.ticks_diff(time.ticks_ms(), last_success) > 2000:
                print("No Data")
                last_success = None

            # Handle loop sleep, based on elapsed time:
            t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
            sleep = LOOP_PERIOD - t_elapsed
            if sleep > 0:
                time.sleep_ms(sleep)
            else:
                print("CLOCK STRETCHING ", sleep)
    finally:
        plat.close()
