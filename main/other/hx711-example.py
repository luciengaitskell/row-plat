#!/usr/bin/python3
import numpy
import time

import RPi.GPIO as GPIO  # import GPIO

from hx711 import HX711  # import the class HX711


try:
    ########## Change the pin values below to the pins you are using ###################
    pin_data = 5
    pin_clock = 6
    num_readings = 25

    print("Reading HX711")
    # Create an object hx which represents your real hx711 chip
    # Required input parameters are only 'dout_pin' (data) and 'pd_sck_pin' (clock)
    # If you do not pass any argument 'gain_channel_A' then the default value is 128
    # If you do not pass any argument 'set_channel' then the default value is 'A'
    # you can set a gain for channel A even though you want to currently select channel B
    hx = HX711(dout_pin=pin_data, pd_sck_pin=pin_clock, gain=128, channel='A')

    print("Reset")
    result = hx.reset()  # Before we start, reset the hx711 ( not necessary)
    if result:  # you can check if the reset was successful
        print('Ready to use')
    else:
        print('not ready')

    while True:
        # Read data several, or only one, time and return mean value
        # it just returns exactly the number which hx711 sends
        # argument times is not required default value is 1
        data = hx.get_raw_data(num_readings)

        if data:  # always check if you get correct value or only False
            data = numpy.array(data, dtype=numpy.float)
            std = numpy.std(data)
            a = numpy.average(data)

            print("avg: {:7.0f}, std: {:4.0f}".format(a, std))
        else:
            print('invalid data')
        time.sleep(0.5)

except (KeyboardInterrupt, SystemExit):
    print('Bye :)')

finally:
    GPIO.cleanup()

