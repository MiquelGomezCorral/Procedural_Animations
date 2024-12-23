import numpy as np
import pygame as py
from typing import Union

from src.settings.settings import Colors, Settings, color_type

point_type = Union[tuple[float, float], np.ndarray]
def parse_point(point: point_type):
    if isinstance(point, tuple):
        return np.array(point)
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


class Procedural_Creature():
    def __init__(self, screen, pos: point_type, body_size: list[float], color: color_type):
        self.screen = screen

        self.n = len(body_size)
        self.body_size = body_size
        self.body_pos = [parse_point(pos)]
        self.start_body_pos()
        self.color = color
        self.width = 1

    def render(self, delta_time: float):
        for body_part, body_size in zip(self.body_pos, self.body_size):
            py.draw.circle(self.screen, self.color, body_part, body_size, self.width)
            py.draw.circle(self.screen, self.color, body_part, 5)

    def start_body_pos(self, ):
        positions = [self.body_pos[0]]
        for i, size in enumerate(self.body_size[1:]):  # Starts in 0 so is like "i-1"
            positions +=  [np.array([positions[i][0], positions[i][1] + size])]
        self.body_pos = np.array(positions)

    def update_body_pos(self):
        for i in range(1, self.n):
            direction = self.body_pos[i-1] - self.body_pos[i]
            dist = np.linalg.norm(direction)
            direction /= dist
            move = dist - self.body_size[i] - self.body_size[i-1]
            self.body_pos[i] += direction * move

    def follow_mouse(self, delta_time: float):
        x, y = py.mouse.get_pos()
        # self.point_towards((x, y), delta_time)
        self.move_towards((x, y), delta_time)

    def move_towards(self, point: point_type, delta_time: float):
        direction = point - self.body_pos[0]
        direction /= np.linalg.norm(direction)
        self.body_pos[0] += direction * delta_time * Settings.MOVING_SPEED

        self.update_body_pos()