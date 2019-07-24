# The MIT License (MIT)
#
# Copyright (c) 2017 Radomir Dopieralski for Adafruit Industries.
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


"""
``adafruit_bno055`` - Adafruit 9-DOF Absolute Orientation IMU Fusion Breakout - BNO055
=======================================================================================

This is a MicroPython driver for the Bosch BNO055 nine degree of freedom
inertial measurement unit module with sensor fusion.

 * Author(s): Radomir Dopieralski (CircuitPython)
 * Modified by Lucien Gaitskell for conversion to MicroPython, July 2019

Converted using additional components from:
 * https://bitbucket.org/thesheep/micropython-bno055/
"""
from micropython import const
import time
import ustruct
from functools import partial

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BNO055.git"

_CHIP_ID = const(0xa0)

CONFIG_MODE = const(0x00)
ACCONLY_MODE = const(0x01)
MAGONLY_MODE = const(0x02)
GYRONLY_MODE = const(0x03)
ACCMAG_MODE = const(0x04)
ACCGYRO_MODE = const(0x05)
MAGGYRO_MODE = const(0x06)
AMG_MODE = const(0x07)
IMUPLUS_MODE = const(0x08)
COMPASS_MODE = const(0x09)
M4G_MODE = const(0x0a)
NDOF_FMC_OFF_MODE = const(0x0b)
NDOF_MODE = const(0x0c)

_POWER_NORMAL = const(0x00)
_POWER_LOW = const(0x01)
_POWER_SUSPEND = const(0x02)

_MODE_REGISTER = const(0x3d)
_PAGE_REGISTER = const(0x07)
_CALIBRATION_REGISTER = const(0x35)
_TRIGGER_REGISTER = const(0x3f)
_POWER_REGISTER = const(0x3e)
_ID_REGISTER = const(0x00)


class BNO055:
    """
    Driver for the BNO055 9DOF IMU sensor.
    """
    def _registers(self, register, struct, value=None, scale=1):
        if value is None:
            size = ustruct.calcsize(struct)
            data = self.i2c.readfrom_mem(self.address, register, size)
            value = ustruct.unpack(struct, data)
            if scale != 1:
                value = tuple(v * scale for v in value)
            return value
        if scale != 1:
            value = tuple(v / scale for v in value)
        data = ustruct.pack(struct, *value)
        self.i2c.writeto_mem(self.address, register, data)

    def _register(self, value=None, register=0x00, struct='B'):
        if value is None:
            return self._registers(register, struct=struct)[0]
        self._registers(register, struct=struct, value=(value,))

    _chip_id = partial(_register, register=0x00, value=None)
    _power_mode = partial(_register, register=0x3e)
    _system_trigger = partial(_register, register=0x3f)
    _page_id = partial(_register, register=0x07)
    temperature = partial(_register, register=0x34, value=None)
    """Measures the temperature of the chip in degrees Celsius."""
    acceleration = partial(_registers, register=0x08, struct='<hhh', value=None, scale=1/100)
    """Gives the raw accelerometer readings, in m/s."""
    magnetic = partial(_registers, register=0x0e, struct='<hhh', value=None, scale=1/16)
    """Gives the raw magnetometer readings in microteslas."""
    gyroscope = partial(_registers, register=0x14, struct='<hhh', value=None, scale=1/900)
    """Gives the raw gyroscope reading in degrees per second."""
    euler = partial(_registers, register=0x1a, struct='<hhh', value=None, scale=1/16)
    """Gives the calculated orientation angles, in degrees."""
    quaternion = partial(_registers, register=0x20, struct='<hhhh', value=None, scale=1/(1<<14))
    """Gives the calculated orientation as a quaternion."""
    linear_acceleration = partial(_registers, register=0x28, struct='<hhh', value=None, scale=1/100)
    """Returns the linear acceleration, without gravity, in m/s."""
    gravity = partial(_registers, register=0x2e, struct='<hhh', value=None, scale=1/100)
    """Returns the gravity vector, without acceleration in m/s."""

    def __init__(self, i2c, address=0x28):
        self.i2c = i2c
        self.address = address
        self.buffer = bytearray(1)
        chip_id = self._read_register(_ID_REGISTER)
        if chip_id != _CHIP_ID:
            raise RuntimeError("bad chip id (%x != %x)" % (chip_id, _CHIP_ID))
        self._reset()
        self._power_mode(_POWER_NORMAL)
        self._page_id(0)
        self._system_trigger(0x00)
        time.sleep(0.01)
        self.mode = NDOF_MODE
        time.sleep(0.01)

    def _write_register(self, register, value):
        self.buffer[0] = value
        self.i2c.writeto_mem(self.address, register, self.buffer)

    def _read_register(self, register):
        return self.i2c.readfrom_mem(self.address, register, 1)[0]

    def _reset(self):
        """Resets the sensor to default settings."""
        self.mode = CONFIG_MODE
        try:
            self._write_register(_TRIGGER_REGISTER, 0x20)
        except OSError: # error due to the chip resetting
            pass
        # wait for the chip to reset (650 ms typ.)
        time.sleep(0.7)

    @property
    def mode(self):
        """
        Switch the mode of operation and return the previous mode.

        Mode of operation defines which sensors are enabled and whether the
        measurements are absolute or relative:

        +------------------+-------+---------+------+----------+
        | Mode             | Accel | Compass | Gyro | Absolute |
        +==================+=======+=========+======+==========+
        | CONFIG_MODE      |   -   |   -     |  -   |     -    |
        +------------------+-------+---------+------+----------+
        | ACCONLY_MODE     |   X   |   -     |  -   |     -    |
        +------------------+-------+---------+------+----------+
        | MAGONLY_MODE     |   -   |   X     |  -   |     -    |
        +------------------+-------+---------+------+----------+
        | GYRONLY_MODE     |   -   |   -     |  X   |     -    |
        +------------------+-------+---------+------+----------+
        | ACCMAG_MODE      |   X   |   X     |  -   |     -    |
        +------------------+-------+---------+------+----------+
        | ACCGYRO_MODE     |   X   |   -     |  X   |     -    |
        +------------------+-------+---------+------+----------+
        | MAGGYRO_MODE     |   -   |   X     |  X   |     -    |
        +------------------+-------+---------+------+----------+
        | AMG_MODE         |   X   |   X     |  X   |     -    |
        +------------------+-------+---------+------+----------+
        | IMUPLUS_MODE     |   X   |   -     |  X   |     -    |
        +------------------+-------+---------+------+----------+
        | COMPASS_MODE     |   X   |   X     |  -   |     X    |
        +------------------+-------+---------+------+----------+
        | M4G_MODE         |   X   |   X     |  -   |     -    |
        +------------------+-------+---------+------+----------+
        | NDOF_FMC_OFF_MODE|   X   |   X     |  X   |     X    |
        +------------------+-------+---------+------+----------+
        | NDOF_MODE        |   X   |   X     |  X   |     X    |
        +------------------+-------+---------+------+----------+

        The default mode is ``NDOF_MODE``.
        """
        return self._read_register(_MODE_REGISTER)

    @mode.setter
    def mode(self, new_mode):
        self._write_register(_MODE_REGISTER, CONFIG_MODE)  # Empirically necessary
        time.sleep(0.02)  # Datasheet table 3.6
        if new_mode != CONFIG_MODE:
            self._write_register(_MODE_REGISTER, new_mode)
            time.sleep(0.01)  # Table 3.6

    @property
    def calibration_status(self):
        """Tuple containing sys, gyro, accel, and mag calibration data."""
        calibration_data = self._read_register(_CALIBRATION_REGISTER)
        sys = (calibration_data >> 6) & 0x03
        gyro = (calibration_data >> 4) & 0x03
        accel = (calibration_data >> 2) & 0x03
        mag = calibration_data & 0x03
        return sys, gyro, accel, mag

    @property
    def calibrated(self):
        """Boolean indicating calibration status."""
        sys, gyro, accel, mag = self.calibration_status
        return sys == gyro == accel == mag == 0x03

    @property
    def external_crystal(self):
        """Switches the use of external crystal on or off."""
        last_mode = self.mode
        self.mode = CONFIG_MODE
        self._write_register(_PAGE_REGISTER, 0x00)
        value = self._read_register(_TRIGGER_REGISTER)
        self.mode = last_mode
        return value == 0x80

    @external_crystal.setter
    def use_external_crystal(self, value):
        last_mode = self.mode
        self.mode = CONFIG_MODE
        self._write_register(_PAGE_REGISTER, 0x00)
        self._write_register(_TRIGGER_REGISTER, 0x80 if value else 0x00)
        self.mode = last_mode
        time.sleep(0.01)
