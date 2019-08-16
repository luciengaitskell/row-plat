from abc import ABCMeta, abstractmethod
import math
import numpy as np

from rowplat.tools import diff_angle
from ..motion.position import Position


class Localizer(metaclass=ABCMeta):
    """ Localizer for tracking current position of the platform. """

    @property
    def current(self) -> Position:
        return self._get_recent()

    @abstractmethod
    def _get_recent(self) -> Position:
        """ Get most recent positioning value """
        pass

    def translate(self, new: Position, current: Position = None) -> Position:
        # TODO: SUPPORT None values
        if current is None:
            current = self.current

        if new.rot is not None:
            rot = diff_angle(new.rot, current.rot)
        else:
            rot = 0
        return self._calc_translate(new, current, rot)

    @abstractmethod
    def _calc_translate(self, new: Position, current: Position, rot_diff: np.float) -> Position:
        pass
