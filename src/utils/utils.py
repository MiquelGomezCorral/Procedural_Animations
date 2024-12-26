from typing import Union
import numpy as np
from scipy import interpolate

point_type = Union[tuple[float, float], np.ndarray]
def parse_point(point: point_type):
    if isinstance(point, tuple):
        return np.array(point, dtype = float)
    elif isinstance(point, np.ndarray):
        return point
    else:
        raise TypeError("'point' must be a tuple or a numpy array")

def get_point_from_pdl(point: np.array, d: float, l: float, rad: bool = True) -> np.array:
    """
    Gets a point at a specified distance and angle from the given point.
    :param point: np.array, the starting point (x, y) from which the new point
                  will be calculated.
    :param d: np.float64, the angle in radians from the positive x-axis.
    :param l: np.float64, the distance from the starting point to the new point.
    :param rad:bool, weather the degree are in radians or not

    :return: np.array, the new point (x', y') calculated based on the given
             distance `l` and angle `d`.
    """
    if not rad:
        d *= np.pi / 180
    return point + l * np.array([np.cos(d), np.sin(d)])

def b_spline(waypoints, num_points: int = 100):
    """
    Creates a smooth path form waypoints
    original code: https://www.youtube.com/watch?v=ueUgHvUT2Z0
    :param waypoints: Points to be smoothen into a smooth shape
    :param num_points: how many points should be in that smooth shape
    :return:
    """
    if isinstance(waypoints, np.ndarray):
        x, y = waypoints[:, 0], waypoints[:, 1]
    else:
        x=[]
        y=[]
        for point in waypoints:
            x.append(point[0])
            y.append(point[1])

    tck, *rest = interpolate.splprep([x,y])
    u = np.linspace(0, 1, num=num_points)
    smooth_shape = interpolate.splev(u, tck)
    return smooth_shape

def compute_angle(a,b,normalized: bool = False):
    if normalized:
        return np.arccos(np.dot(a, b))  # Both normalized, denominator = 1
    else:
        return np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) )

def cross_product(a, b):
    return a[0] * b[1] - a[1] * b[0]