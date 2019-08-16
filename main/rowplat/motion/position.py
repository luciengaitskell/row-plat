import numpy as np
from enum import Enum


class UNITS(Enum):
    METERS = 0
    GPS = 1


class Position:
    def __init__(self, x, y=None, rot=None, time=None, units=None):
        if y is None:
            self._pos = np.ndarray((3,))
            if rot is not None:
                self._pos = np.ndarray((3,))
                self._pos[0:2] = x
                self._pos[2] = rot
            else:
                self._pos[0:3] = x

        else:
            self._pos = np.array((x, y, rot))

        self._t = time
        self.units = None

    @property
    def arr(self):
        return self._pos

    @property
    def loc(self):
        return self._pos[0:2]

    @loc.setter
    def loc(self, loc):
        self._pos[0:2] = loc

    @property
    def rot(self):
        return self._pos[2]

    @rot.setter
    def rot(self, rot):
        self._pos[2] = rot

    @property
    def time(self):
        return self._t
