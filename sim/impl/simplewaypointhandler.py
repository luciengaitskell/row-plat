import numpy as np

from rowplat.abstract.waypointhandler import WaypointHandler
from rowplat.motion.position import Position
from sim.impl.target import Target


class SimpleWaypointHandler(WaypointHandler):
    def __init__(self, target: Target):
        self._tar = target

        self._dist = np.array([2, 0])  # Distance from target to hold

    def _get_waypoint(self):
        wyp = Position(*(self._tar.pos.loc + self._dist), None)
        return wyp
