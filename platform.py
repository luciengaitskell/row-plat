import time
from machine import I2C, Pin

from comms.comms import CommsNode
from devices.rfm69 import RFM69
from devices.ssd1306 import SSD1306_I2C


class Platform:
    def __init__(self, id: str, display: bool=True):
        self.running = False
        self.i2c_bus = I2C(0, scl=Pin(22, mode=Pin.PULL_UP), sda=Pin(23, mode=Pin.PULL_UP))

        self.c = CommsNode(id, None)
        self.radio = RFM69(12, 27, baudrate=5000000)
        if display is True:
            self.display = SSD1306_I2C(128, 32, self.i2c_bus)
        else:
            self.display = None

        """
        gns = XA1110(i2c=i2c_bus)
        gns.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
        gns.read_all_data()  # Clear buffer so that we know that data that followings is current
        gns_data = MicropyGPS(location_formatting='dd')

        imu = bno055.BNO055(i2c_bus)"""

    def setup(self):
        self.radio.init(915.0)
        self.running = True

        #_thread.start_new_thread(self._heartbeat_thread, ())

    def heartbeat(self):
        test_packet = self.c.gen_message(
            recp_id=bytes([ord('m')]),  # Intended recipient ID
            codec_id=b'h',  # Codec ID
            sub_id=bytes([0]),  # Message packet sub ID
            max_id=bytes([0]),  # Maximum number of packets in message
            csum=bytes([0]),  # Checksum
            body=bytes([])
        )
        self.radio.send(test_packet)
        return test_packet

    def _heartbeat_thread(self):
        while self.running:
            self.heartbeat()
            time.sleep_ms(500)

    def close(self):
        self.running = False
        self.radio.close()
