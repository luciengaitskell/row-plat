from abc import ABCMeta, abstractmethod

from ..motion.position import Position


class Thruster(metaclass=ABCMeta):
    def __init__(self, position: Position):
        self._pos = position

        self._thrust = 0

    # Thruster Properties/Values:
    @property
    def pos(self):
        return self._pos

    # Thruster Interaction:
    @property
    def thrust(self):
        return self._thrust

    @thrust.setter
    def thrust(self, thr):
        self._thrust = thr
        self._set_power(self._conv_thrust(thr))

    @abstractmethod
    def _conv_thrust(self, thrust):
        """ Convert thrust value to power. """
        pass

    @abstractmethod
    def _set_power(self, pwr):
        """ Set actual power value on thruster. """
        pass
