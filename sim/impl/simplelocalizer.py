import numpy as np

from rowplat.numpy_tools import rotate
from rowplat.abstract.localizer import Localizer
from rowplat.motion.platform import Platform
from rowplat.motion.position import Position


class SimpleLocalizer(Localizer):
    def _calc_translate(self, new: Position, current: Position, rot) -> Position:
        pos = Position(new.arr - current.arr)
        pos.rot = rot
        return pos

    def _get_recent(self) -> Position:
        return self.loc

    def __init__(self, plat: Platform):
        self.loc = Position(0., 0., 0.)

        self._plat = plat

    def frame(self, tdelta):
        ths = self._plat.last_thrust
        motion = np.asarray(self._plat.coeff * ths.reshape((2,1))).flatten()
        motion *= tdelta

        motion[0:2] = motion[0:2] * rotate(self.loc.rot)

        self.loc._pos = self.loc._pos + motion

        return motion
