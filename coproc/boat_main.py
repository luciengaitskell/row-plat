import time
from machine import UART

from settings import VERB
from platform import Platform
from comms.packet import Packet
from comms import nmea


plat = Platform('b')  # Platform hardware setup
serial = UART(1, rx=33, tx=15, baudrate=115200)  # Serial communication to host processor (RasPi)


def interp_joy(v):
    """ Interpret joystick value from encoded transmission """
    v -= 127  # Recenter at 0 (from 127)
    v /= 127  # Scale from +/-127 max
    return round(v, 2)


def main():
    try:
        plat.setup()

        while plat.running:
            data = plat.radio.receive(timeout=1.0)  # Attempt wait for incoming packet

            if data is not None:  # If packet received
                # packet = plat.c.accept_bytes(data)  # UNSTABLE -- no msg id sync method in this situation (one way)
                packet = Packet.from_raw(data)  # Interpret data into packet
                if packet is not None:  # Check that packet was not ignored
                    try:  # Ensure it doesn't crash on error
                        raw = packet.body

                        # Attempt to select from serial data
                        c_enable = bool(raw[0])  # Controller thruster enable state
                        c_mode = raw[1]  # Controller thruster mode / layout
                        c_y = interp_joy(raw[2])  # Controller y-axis joystick
                        c_r = interp_joy(raw[3])  # Controller rotation joystick
                        c_g_y = raw[4]  # Controller y-axis gain
                        c_g_r = raw[5]  # Controller rotation gain
                    except KeyError:
                        print("malformed serial data: ", raw)
                    else:
                        msg = nmea.Control(c_enable, c_mode, c_y, c_r, c_g_y, c_g_r)
                        serial.write(msg.render())  # Write to serial, with carriage return and newline
            if VERB>2: print(data)
    finally:
        plat.close()
