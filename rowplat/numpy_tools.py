import numpy as np


def rotate(a):
    """ Generate 2d rotation matrix, where pos = CW and neg = CCW. """
    # Calculate rotation matrix:
    s = np.sin(a)
    c = np.cos(a)
    return np.mat([[c, -s], [s, c]])


if __name__ == "__main__":
    mat = rotate(0.1)
    print(mat)
    print(np.array([1, 0]) * mat)
