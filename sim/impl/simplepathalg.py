import numpy as np
import math

from rowplat.abstract.localizer import Localizer
from rowplat.motion.navigation import PathAlgorithm
from rowplat.motion.position import Position


class SimplePathAlg(PathAlgorithm):  # TODO: Gotta angle towards the point.... we can't strafe
    def __init__(self, mind, maxd, db, dba, mint, mintr):
        self._mind = mind
        self._maxd = maxd
        self._db = db  # Translational deadband
        self._dba = dba  # Angle deadband
        self._mint = mint  # Minimum thrust linear
        self._mintr = mintr  # Minimum thrust for rotation

    def calc(self, pos: Localizer, wyp: Position) -> np.ndarray(shape=(3,)):
        diff = pos.translate(wyp)  # Support 'None' for rot
        d = np.linalg.norm(diff.loc)

        thrust = np.zeros((3,))

        # On target:
        if d <= self._db:
            return thrust

        scale = (d - self._mind) / (self._maxd - self._mind)

        thrust[0:2] = diff.loc * (scale * (1-self._mint) + self._mint)

        if abs(diff.rot) > self._dba:
            thrust[2] = diff.rot/math.pi * (1 - self._mintr) + self._mintr

        return thrust
