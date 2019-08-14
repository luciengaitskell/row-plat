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
            print("pre")
            data = plat.radio.receive(
                timeout=0.1)  # Data seems to be incorrect after send -- need to revise encoding for errors?
            print("post")
            # print(data)
            if isinstance(data, bytearray):
                pak = plat.c.accept_bytes(data)
                print(pak)
                #print(list(pak.to_raw))
                last_success = time.ticks_ms()

            if last_success is not None and time.ticks_diff(time.ticks_ms(), last_success) > 2000:
                print("No Data")
            print("-----")

            # Handle loop sleep, based on elapsed time:
            t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
            sleep = LOOP_PERIOD - t_elapsed
            if sleep > 0:
                time.sleep_ms(sleep)
            else:
                print("CLOCK STRETCHING ", sleep)
    finally:
        plat.close()
