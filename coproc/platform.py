import time
from machine import I2C, Pin
import random

from comms.comms import CommsNode
from devices.rfm69 import RFM69
from devices.ssd1306 import SSD1306_I2C


class Platform:
    def __init__(self, id: str, display: bool=True):
        """ Create platform object. """

        self.running = False  # Status of platform. Used for concurrent threads

        """
        Interfaces/Buses:
         - I2C
        """
        self.i2c_bus = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))

        """
        Hardware:
         - RFM69 Radio
         - SSD1306 Display
        """
        self.radio = RFM69(12, 27, baudrate=int(2e6))  # NOTE: Bytes in communication became corrupted with baudrates
        #   above 4 MHz (noticed unreliability at 4.4 MHz and full breakdown at 5 MHz)
        if display is True:
            self.display = SSD1306_I2C(128, 32, self.i2c_bus)
        else:
            self.display = None

        """ Wrappers/Supporting Classes """
        self.c = CommsNode(id, None)  # Handles messaging over radio

        '''
        gns = XA1110(i2c=i2c_bus)
        gns.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
        gns.read_all_data()  # Clear buffer so that we know that data that followings is current
        gns_data = MicropyGPS(location_formatting='dd')

        imu = bno055.BNO055(i2c_bus)'''

    def setup(self):
        self.radio.init(915.0)
        self.running = True

        #_thread.start_new_thread(self._heartbeat_thread, ())

    def heartbeat(self):
        hb_pak = self.c.gen_message(
            recp_id=0,  # Intended recipient ID
            codec_id=12,  # Codec ID
            sub_id=bytes([0]),  # Message packet sub ID
            max_id=bytes([0]),  # Maximum number of packets in message
            body=bytes([random.randint(125, 129)])
        )
        self.radio.send(hb_pak.to_raw)
        return hb_pak

    def _heartbeat_thread(self):
        while self.running:
            self.heartbeat()
            time.sleep_ms(500)

    def close(self):
        self.running = False
        self.radio.close()
