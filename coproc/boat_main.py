import time
from machine import UART

from settings import VERB
from platform import Platform
from comms.packet import Packet


plat = Platform('b')  # Platform hardware setup
serial = UART(1, rx=33, tx=15, baudrate=115200)  # Serial communication to host processor (RasPi)


def main():
    try:
        plat.setup()

        while plat.running:
            data = plat.radio.receive(timeout=1.0)  # Attempt wait for incoming packet

            if data is not None:  # If packet received
                # packet = plat.c.accept_bytes(data)  # UNSTABLE -- no msg id sync method in this situation (one way)
                packet = Packet.from_raw(data)  # Interpret data into packet
                if packet is not None:  # Check that packet was not ignored
                    msg = packet.body
                    serial.write(msg + '\n')  # Write to serial, with newline
            if VERB>2: print(data)
    finally:
        plat.close()
