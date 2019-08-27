import numpy as np


def rotate(a):
    """ Generate 2d rotation matrix, where pos = CW and neg = CCW. """
    # Calculate rotation matrix:
    s = np.sin(a)
    c = np.cos(a)
    return np.mat([[c, -s], [s, c]])


def diff_angle(t, o=0):
    """ Difference (in radians) from origin (o) to target (t). """
    return ((t-o) + np.pi) % (2 * np.pi) - np.pi  # limits to [-pi, pi)


if __name__ == "__main__":
    mat = rotate(0.1)
    print(mat)
    print(np.array([1, 0]) * mat)
