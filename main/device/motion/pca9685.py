# Copyright (c) 2016 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import division
import logging
import time
import math
from ..i2c_device import I2cDevice
from ..interface import PWMInterface

# Registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04


logger = logging.getLogger(__name__)


def software_reset(i2c=None, **kwargs):
    """Sends a software reset (SWRST) command to all servo drivers on the bus."""
    # Setup I2C interface for device 0x00 to talk to all of them.
    d = I2cDevice(0x70, **kwargs)
    d.write_byte_data(0x06)  # SWRST


class PCA9685(I2cDevice):
    """PCA9685 PWM LED/servo controller."""
    def __init__(self, address=PCA9685_ADDRESS, **kwargs):
        """Initialize the PCA9685."""
        super().__init__(address, **kwargs)

        self.freq = None

        # Setup I2C interface for the device.
        self.set_all_pwm(0, 0)
        self.write_byte_data(MODE2, OUTDRV)
        self.write_byte_data(MODE1, ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self.read_byte_data(MODE1, False)
        mode1 = mode1 & ~SLEEP  # wake up (reset sleep)
        self.write_byte_data(MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator

    def get_freq(self):  # To allow channel objects to stay updated
        return self.freq

    def set_pwm_freq(self, freq_hz):
        """Set the PWM frequency to the provided value in hertz."""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        logger.debug('Final pre-scale: {0}'.format(prescale))
        oldmode = self.read_byte_data(MODE1, False)
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        self.write_byte_data(MODE1, newmode)  # go to sleep
        self.write_byte_data(PRESCALE, prescale)
        self.write_byte_data(MODE1, oldmode)
        time.sleep(0.005)
        self.write_byte_data(MODE1, oldmode | 0x80)

        self.freq = freq_hz

    def _calc_pwm_val(self, ms) -> int:
        max_ms = (1/self.freq)*1000
        ms_tick = max_ms/4096

        return int(ms/ms_tick)

    def set_pwm_ms(self, channel, ms):
        self.set_pwm(channel, 0, self._calc_pwm_val(ms))

    def set_all_pwm_ms(self, ms):
        self.set_all_pwm(0, self._calc_pwm_val(ms))

    def set_pwm(self, channel, on, off):
        """Sets a single PWM channel."""
        self.write_byte_data(LED0_ON_L+4*channel, on & 0xFF)
        self.write_byte_data(LED0_ON_H+4*channel, on >> 8)
        self.write_byte_data(LED0_OFF_L+4*channel, off & 0xFF)
        self.write_byte_data(LED0_OFF_H+4*channel, off >> 8)

    def set_all_pwm(self, on, off):
        """Sets all PWM channels."""
        self.write_byte_data(ALL_LED_ON_L, on & 0xFF)
        self.write_byte_data(ALL_LED_ON_H, on >> 8)
        self.write_byte_data(ALL_LED_OFF_L, off & 0xFF)
        self.write_byte_data(ALL_LED_OFF_H, off >> 8)

    def get_channel(self, channel):
        return PCA9685Channel(self, channel)


class PCA9685Channel(PWMInterface):
    def __init__(self, p: PCA9685, channel: int):
        super().__init__(p.get_freq, 0.999999999)
        self.p = p  #PCA9685
        self.c = channel

    def set_pwm_freq(self, freq_hz):
        self.p.set_pwm_freq(freq_hz)

    def _set_pwm(self, ms):
        self.p.set_pwm_ms(self.c, ms)
