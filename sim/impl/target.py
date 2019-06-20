import numpy as np

from rowplat.tools import rotate
from rowplat.motion.position import Position


class Target:
    def __init__(self, initial: Position):
        self.pos = initial
        self.vel = np.array((0., 0.))

    def frame(self, tdelta):
        dpos_prime = self.vel * tdelta  # Movement in target frame

        dpos = dpos_prime*rotate(self.pos.rot)  # Rotate movement for absolute frame
        self.pos.loc = self.pos.loc + dpos  # Add to position track

        return dpos
