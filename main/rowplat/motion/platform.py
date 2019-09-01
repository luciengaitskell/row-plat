import math
import numpy as np

from typing import List

from rowplat.tools import diff_angle
from ..abstract.thruster import Thruster


class Platform:
    def __init__(self, thrusters: List[Thruster]):
        self.running = False
        self.coeff = None
        self.coeff_inv = None

        self.thrusters = thrusters

    @property
    def thrusters(self):
        return self._ths

    @thrusters.setter
    def thrusters(self, ths: List[Thruster]):
        self._ths = ths
        self.last_thrust = np.zeros((len(self._ths, )))
        self._gen_coeff_mat()

    def _gen_coeff_mat(self, lower_bound=10 ** -10):  # Generate coefficient matrix
        """
        Generate coefficient matrix (and inverse) in to use in thrust calculation.
        T = A*M,
        Where T is the input vector (vx,vy,vr), A is this matrix, and M is the motor powers (m1,m2,m3,m4).
        :param lower_bound:
        :return:
        """

        c_x = []
        c_y = []
        c_rot = []
        for t in self._ths:
            a = t.pos.rot
            v = t.pos.loc
            c_x.append(math.sin(a))
            c_y.append(math.cos(a))

            center_dist = np.linalg.norm(v)

            # Calculate perpendicular angle of thruster position (pointing counter clockwise):
            perp_ang = np.arctan2(v[0], v[1])  # find vector angle (from origin to thruster)
            perp_ang += np.pi / 2  # rotate to perpendicular
            perp_ang = diff_angle(perp_ang)  # limit to [-pi, pi)

            c_rot.append(np.cos(a - perp_ang)
                         * center_dist)

        self.coeff = np.mat([c_x, c_y, c_rot])  # Coefficient matrix

        self.coeff_inv = np.linalg.pinv(self.coeff).T  # np.matrix

        for (x, y), val in np.ndenumerate(self.coeff_inv):  # filter out small values
            if abs(val) < lower_bound:
                self.coeff_inv[x, y] = 0

    def set_thrust(self, vx: float, vy: float, vr: float) -> None:
        """
        Set thrust of motors from desired movement. Calculate using inverse coefficient matrix.
        :param vx: x axis input
        :param vy: y axis input
        :param vr: z axis rotation input
        :return: None
        """

        thrusts = np.asarray(np.array([vx, vy, vr]) @ self.coeff_inv).flatten()

        # Scale all if above one:
        if len(thrusts) > 0:
            max_t = abs(max(thrusts.max(), thrusts.min(), key=abs))
            if max_t > 1:
                thrusts /= max_t

        self.last_thrust = thrusts

        for i, t in enumerate(self._ths):
            p = thrusts[i]
            t.thrust = p
        return thrusts

    def disable_thrusters(self):
        self.last_thrust = np.zeros((len(self._ths),))
        for t in self._ths:
            t.thrust = 0
