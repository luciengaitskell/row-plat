from abc import ABCMeta, abstractmethod

from .localizer import Localizer


class WaypointHandler(metaclass=ABCMeta):
    """ Handles navigation waypoints. """
    @property
    def waypoint(self):
        return self._get_waypoint()

    @abstractmethod
    def _get_waypoint(self):
        pass


