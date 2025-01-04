import numpy as np
import pygame as py
from typing import Union

from src.utils import utils

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


class Limb:
    def __init__(
            self, screen, pos: point_type, init_d: float, length: float, thickness: float,
            color: tuple[int, int, int] = (68, 190, 242)
    ):
        self.screen = screen
        self.pos = parse_point(pos)

        self.theta = np.float64(init_d)
        self.theta_rad = self.theta * np.pi / 180
        self.length = np.float64(length)
        self.thickness = thickness
        self.color = color

    def get_start_point(self):
        return self.pos
    def get_end_point(self):
        # return self.pos + self.length * np.array([np.cos(self.theta_rad), np.sin(self.theta_rad)])
        return get_point_from_pdl(self.pos, self.theta_rad, self.length)
    def get_angle(self):
        return self.theta
    def get_angel_radians(self):
        return self.theta_rad
    def get_length(self):
        return self.length
    def get_thickness(self):
        return self.thickness
    def update_pos(self, pos: point_type):
        self.pos = parse_point(pos)

    def update_angle(self, angle_deg: float, prev_angle: float = None):
        # if prev_angle is not None:
        #     # Normalize the angular difference to [-180, 180]
        #     diff = angle_deg - prev_angle
        #     if abs(diff) > Settings.MAX_BEND_LIMB:
        #         angle_deg = prev_angle + np.sign(diff)*Settings.MAX_BEND_LIMB

        self.theta = angle_deg
        self.theta_rad = self.theta * np.pi / 180

    def render(self, draw_joint: bool = False, thickness: float = None):
        """
        Renders the limb + a joint
        """
        """       
        point_1 = self.pos
        point_2 = get_point_from_pdl(point_1, 90-self.theta, self.thickness, rad = False)
        point_3 = self.get_end_pos()
        point_4 = get_point_from_pdl(point_3, 90-self.theta, self.thickness, rad = False)

        joint = get_point_from_pdl(point_1, 90-self.theta, self.thickness / 2, rad = False)
        points: list[tuple] = [
            (point_1[0], point_1[1]),
            (point_2[0], point_2[1]),
            (point_4[0], point_4[1]),
            (point_3[0], point_3[1]),
        ]
        py.draw.polygon(screen, self.color, points)
        py.draw.circle(screen, (255,255,255), joint, self.thickness / 4)
        Calculate the direction vector from self.pos to self.get_end_pos()"""
        if thickness is None:
            thickness = self.thickness

        direction = self.get_end_point() - self.pos
        angle = np.arctan2(direction[1], direction[0])  # angle in radians
        # Perpendicular angle (90 degrees clockwise and counterclockwise)
        angle_perp = angle + np.pi / 2
        # Length of the rectangle (distance between self.pos and self.get_end_pos())
        length = np.linalg.norm(direction)
        # Use get_point_from_pdl to get the other two corners of the rectangle
        # These points are at the same distance `length` but perpendicular to the original line
        corner1 = get_point_from_pdl(self.pos, angle_perp, thickness)
        corner2 = get_point_from_pdl(self.get_end_point(), angle_perp, thickness)

        # Calculate the other two corners
        corner3 = get_point_from_pdl(self.pos, angle_perp - np.pi, thickness)
        corner4 = get_point_from_pdl(self.get_end_point(), angle_perp - np.pi, thickness)

        points = [corner1, corner3, corner4, corner2]
        # Draw the rectangle using Pygame's draw.polygon
        py.draw.polygon(self.screen, self.color, points)
        if draw_joint:
            py.draw.circle(self.screen, (255,255,255), self.pos, thickness)

class Tentacle:
    def __init__(
            self, screen, pos: point_type, n_limbs: int,
            total_length: float, thickness: float, smooth_factor: float,
            color: tuple[int, int, int], shorten_first_limb: bool = False,
            objective: utils.point_type = (0,0)
    ):
        self.screen = screen
        self.limb_length = total_length/n_limbs
        self.thickness = thickness
        self.smooth_factor = smooth_factor
        self.color = color
        self.objective: point_type = utils.parse_point(objective)

        # Calculate the sum of the logarithms & Calculate k such that the sum of parts equals L
        log_sum = np.sum(np.log(np.arange(1, n_limbs + 1)))  # Sum of log(i) for i = 1 to N
        self.k_len = total_length / log_sum
        self.k_thick = thickness / log_sum

        if shorten_first_limb:
            self.limbs: list[Limb] = [Limb(
                screen,
                pos,
                0,
                self.k_len * np.log(n_limbs * 0.75),
                self.k_thick * np.log(n_limbs),
                color = color,
            )]
        else:
            self.limbs: list[Limb] = [Limb(
                screen,
                pos,
                0,
                self.k_len * np.log(n_limbs),
                self.k_thick * np.log(n_limbs),
                color=color,
            )]
        for i in range(1, n_limbs):
            self.limbs += [
                Limb(
                    screen,
                    self.limbs[i-1].get_end_point(),
                    -i * 90/n_limbs,
                    self.k_len * np.log(n_limbs-i+1), #self.limb_length/(i+1),
                    self.k_thick * np.log(n_limbs-i+1), #thickness/(i+1)
                    color = color,
                )
            ]

        self.length = sum(limb.get_length() for limb in self.limbs)

    def render(self, draw_joint: bool = False, thickness: float = None):
        for limb in self.limbs:
            limb.render(draw_joint, thickness)

    def get_start_point(self):
        return self.limbs[0].get_start_point()

    def get_objective(self):
        return self.objective

    def get_length(self):
        return self.length

    def get_drawing_points(self):
        points_1 = [self.limbs[0].get_start_point()]
        points_2 = []

        for limb in self.limbs:
            pos = limb.get_start_point()
            direction = np.array([
                np.cos(np.radians(limb.get_angle())),
                np.sin(np.radians(limb.get_angle()))
            ])
            perpend = utils.get_perpendicular(direction)
            points_1 += [
                pos + perpend * limb.get_thickness(),
                pos + perpend * limb.get_thickness() + direction * limb.get_thickness() * 1.3
            ]
            points_2 += [
                pos - perpend * limb.get_thickness(),
                pos - perpend * limb.get_thickness() + direction * limb.get_thickness() * 1.3
            ]

        points_1 += [self.limbs[-1].get_end_point()]

        return points_1 + list(reversed(points_2))

    def follow_mouse(self, delta_time: float):
        x, y = py.mouse.get_pos()
        self.point_towards((x, y), delta_time)

    def move_tentacle_to(self,pos: point_type):
        self.limbs[0].update_pos(pos)
        self.update_limbs()

    def move_tentacle_by(self, pos: point_type):
        if isinstance(pos, tuple):
            pos = np.array(pos)
        elif not isinstance(pos, np.ndarray):
            raise TypeError("'pos' must be a tuple or a numpy array")

        self.move_tentacle_to(self.limbs[0].get_start_point() + pos)

    def point_towards(self, delta_time: float, pos: point_type = None):
        if pos is not None:
            self.objective = parse_point(pos)

        head = self.limbs[-1].get_end_point()
        if np.array_equal(head, self.objective):
            return

        n: int = len(self.limbs)
        for i, limb in enumerate(reversed(self.limbs)):
            v1 = head - limb.get_start_point()
            v2 = self.objective - limb.get_start_point()

            dot = np.dot(v1,v2)
            mag_v1 = np.linalg.norm(v1)
            mag_v2 = np.linalg.norm(v2)

            cos_theta = np.clip(dot /(mag_v1 * mag_v2), -1.0, 1.0)
            angle_rad = np.arccos(cos_theta)
            angle_deg = np.degrees(angle_rad)
            cross_product = v1[0] * v2[1] - v1[1] * v2[0]
            # Update the angle proportionally to the i-th joint
            new_angle = (
                    limb.get_angle() + (np.sign(cross_product) * angle_deg) *
                    delta_time * self.smooth_factor / (n-i+2)
            )
            limb.update_angle(new_angle, self.limbs[i-1].get_angle() if i >= 1 else None)

            self.update_limbs(i)

    def update_limbs(self, i: int = 0):
        n: int = len(self.limbs)
        for j, limb_j in enumerate(self.limbs[n - i:], n - i):
            limb_j.update_pos(self.limbs[j - 1].get_end_point())