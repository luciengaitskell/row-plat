from abc import ABCMeta, abstractmethod
import numpy as np

from rowplat.numpy_tools import rotate
from .platform import Platform
from .position import Position
from ..abstract.waypointhandler import WaypointHandler
from ..abstract.localizer import Localizer


class PathAlgorithm(metaclass=ABCMeta):
    """ Handles scaling and direction for desired position->target motion. """
    @abstractmethod
    def calc(self, pos: Localizer, wyp: Position) -> np.ndarray(shape=(3,)):
        """ Calculate x,y,rot thrust from current and desired position """
        pass


class Navigation:  # TODO: ADD THREADING
    """ Threaded handler of platform to track target from current position. """
    def __init__(self, plat: Platform, pos: Localizer, wyp: WaypointHandler, alg: PathAlgorithm):
        self._plat = plat
        self._pos = pos
        self._wyp = wyp

        self.algorithm = alg

    def frame(self):
        thr = self.algorithm.calc(self._pos, self._wyp.waypoint)
        rot = rotate(self._pos.current.rot)
        thr[0:2] = thr[0:2] * rot
        self._plat.set_thrust(*thr)
