import numpy as np
import pygame as py
from typing import Union

from adodbapi.ado_consts import directions

from src.settings.settings import Colors, Settings, color_type

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


class WobblyEyes:
    def __init__(self, screen, pos1: point_type, pos2: point_type, radius: float):
        self.screen = screen
        self.pos1 = parse_point(pos1)
        self.pos2 = parse_point(pos2)
        self.radius = radius

    def render(self):
        mouse = parse_point(py.mouse.get_pos())
        direction_1 = mouse - self.pos1
        direction_1 /= np.linalg.norm(direction_1)
        direction_2 = mouse - self.pos2
        direction_2 /= np.linalg.norm(direction_2)

        py.draw.circle(self.screen, Colors.WHITE, self.pos1, self.radius)
        py.draw.circle(self.screen, Colors.WHITE, self.pos2, self.radius)
        py.draw.circle(self.screen, Colors.BLACK, self.pos1 + direction_1 * self.radius * 0.8, self.radius * 0.4)
        py.draw.circle(self.screen, Colors.BLACK, self.pos2 + direction_2 * self.radius * 0.8, self.radius * 0.4)

    def set_pos(self, pos1, pos2):
        self.pos1, self.pos2 = pos1, pos2

class ProceduralCreature:
    def __init__(self, screen, pos: point_type, body_size: list[float], color: color_type, overlapping_body: bool = False):
        self.screen = screen

        self.n = len(body_size)
        self.body_size = body_size
        self.body_pos = [parse_point(pos)]
        self.body_direction = np.array([0,0], dtype=float)
        self.start_body_pos()
        self.color = color
        self.width = 1
        self.overlapping_body = overlapping_body

        pos1, pos2 = self.get_eyes_pos()
        self.eyes = WobblyEyes(self.screen, pos1, pos2, body_size[0]*0.3)

    def render(self, delta_time: float):
        perpend = np.array([self.body_direction[1], -self.body_direction[0]])
        nose1 = self.body_direction * self.body_size[0]*1.25 + self.body_pos[0]
        nose2 = self.body_direction * self.body_size[0] + self.body_pos[0] - perpend * self.body_size[0] * 0.6
        nose3 = self.body_direction * self.body_size[0] + self.body_pos[0] + perpend * self.body_size[0] * 0.6

        shape_1: list[point_type] = [
            nose2, nose1, nose3,
            perpend * self.body_size[0] + self.body_pos[0]
        ]
        shape_2: list[point_type] = [-perpend * self.body_size[0] + self.body_pos[0]]
        for i in range(1, self.n):
            # py.draw.circle(self.screen, Colors.WHITE, self.body_pos[i], self.body_size[i], self.width)
            # py.draw.circle(self.screen, Colors.WHITE, self.body_pos[i], 5)

            direction = self.body_pos[i-1] - self.body_pos[i]
            direction /= np.linalg.norm(direction)
            perpend = np.array([direction[1], -direction[0]])

            if Settings.SPECIAL_SMOOTHING:
                shape_1 += [perpend*(self.body_size[i] + self.body_size[i-1])/2 + self.body_pos[i] + direction*self.body_size[i]/3]
                shape_1 += [perpend*self.body_size[i] + self.body_pos[i]]
                if i < self.n - 1:
                    shape_1 += [perpend*(self.body_size[i] + self.body_size[i+1])/2 + self.body_pos[i] - direction*self.body_size[i]/3]

                shape_2 += [-perpend * (self.body_size[i] + self.body_size[i - 1]) / 2 + self.body_pos[i] + direction*self.body_size[i]/3]
                shape_2 += [-perpend * self.body_size[i] + self.body_pos[i]]
                if i < self.n - 1:
                    shape_2 += [-perpend*(self.body_size[i] + self.body_size[i+1])/2 + self.body_pos[i] - direction*self.body_size[i]/3]
            else:
                shape_1 += [perpend*self.body_size[i] + self.body_pos[i]]
                shape_2 += [-perpend * self.body_size[i] + self.body_pos[i]]

        if self.n > 1:
            direction = self.body_pos[-2] - self.body_pos[-1]
            direction /= np.linalg.norm(direction)
            tail = -direction * self.body_size[-1] + self.body_pos[-1]
            shape_1 += [tail]

        points = shape_1 + list(reversed(shape_2))


        if Settings.DEBUGGING_MODE:
            for body_part, body_size in zip(self.body_pos, self.body_size):
                py.draw.circle(self.screen, Colors.WHITE, body_part, body_size, self.width)
                py.draw.circle(self.screen, Colors.WHITE, body_part, 5)
            for point in points:
                py.draw.circle(self.screen, Colors.BLACK, point, 5)

        else:
            py.draw.polygon(self.screen, self.color, points)
            py.draw.polygon(self.screen, Colors.WHITE, points, 3)
            self.eyes.render()

    def get_eyes_pos(self) -> tuple[point_type, point_type]:
        perpend = np.array([self.body_direction[1], -self.body_direction[0]])
        pos1 = self.body_direction * self.body_size[0] + self.body_pos[0] - perpend * self.body_size[0] * 0.6
        pos2 = self.body_direction * self.body_size[0] + self.body_pos[0] + perpend * self.body_size[0] * 0.6
        return pos1, pos2

    def update_eyes_pos(self):
        self.eyes.set_pos(*self.get_eyes_pos())

    def start_body_pos(self, ):
        positions = [self.body_pos[0]]
        for i, size in enumerate(self.body_size[1:]):  # Starts in 0 so is like "i-1"
            positions +=  [np.array([positions[i][0], positions[i][1] + size])]
        self.body_pos = np.array(positions)

    def update_body_pos(self, overlapping_body: bool = False):
        for i in range(1, self.n):
            direction = self.body_pos[i-1] - self.body_pos[i]
            dist = np.linalg.norm(direction)
            direction /= dist
            move = dist
            if overlapping_body:
                # NOT OVER-LAPPING BODY
                move -= self.body_size[i] - self.body_size[i-1]
            else:
                if self.body_size[i] >= self.body_size[i-1]:
                    move -= self.body_size[i]
                else:
                    move -= self.body_size[i - 1]
            self.body_pos[i] += direction * move


    def follow_mouse(self, delta_time: float):
        x, y = py.mouse.get_pos()
        # self.point_towards((x, y), delta_time)
        self.move_towards((x, y), delta_time)

    def move_towards(self, point: point_type, delta_time: float):
        direction = self.body_direction + (point - self.body_pos[0]) * delta_time * 2.5e-5
        direction /= np.linalg.norm(direction)
        self.body_direction = direction
        self.body_pos[0] += self.body_direction * delta_time * Settings.MOVING_SPEED
        self.update_eyes_pos()

        self.update_body_pos(self.overlapping_body)