import matplotlib.pyplot as plt
import matplotlib.patches as pat

import numpy as np

from rowplat.tools import rotate
from rowplat.motion.position import Position


class Plot:
    def __init__(self):
        self._figure: plt.Figure = plt.figure(0)

        self._boat = pat.FancyArrowPatch((0., 0.), (1., 1.))
        self._figure.gca().add_patch(self._boat)
        self._target = plt.plot([1.], [1.], marker='o', markersize=3, color="blue")[0]
        self._waypoint = plt.plot([1.], [1.], marker='+', markersize=3, color="red")[0]

    def update(self, t=0.001):
        plt.draw()
        plt.pause(t)

    @property
    def boat(self) -> pat.FancyArrowPatch:
        return self._boat

    @boat.setter
    def boat(self, pos: Position):
        head = pos.loc + np.asarray(np.array([0, 1]) * rotate(pos.rot)).flatten()
        self._boat.set_positions(pos.loc, head)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, pos: Position):
        self._target.set_data(pos.loc.reshape(1,2).T)

    @property
    def waypoint(self):
        return self._waypoint

    @waypoint.setter
    def waypoint(self, pos: Position):
        self._waypoint.set_data(pos.loc.reshape(1,2).T)
