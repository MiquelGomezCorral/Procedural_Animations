import pygame as py
from typing import Union
import numpy as np
from dataclasses import  dataclass
from src.classes.knematic_limb import Tentacle, parse_point
from src.settings.settings import Colors, SpiderSettings



class Spider():
    def __init__(
            self, screen, pos: Union[tuple[float, float], np.ndarray], radius: float, n_legs: int,
            margin_angle: float, total_leg_length: float,  leg_thickness: float,
            color_body: tuple[int,int,int] = Colors.BLACK, color_legs: tuple[int,int,int] = Colors.BLACK
    ):
        self.screen = screen
        assert n_legs % 2 == 0, "Please provide an even number of legs"

        self.pos = parse_point(pos)

        self.radius = radius
        self.n_legs = n_legs
        self.margin_angle = margin_angle
        self.margin_angle_rad = np.radians(margin_angle)
        self.color_body = color_body
        self.color_legs = color_legs

        # self.facing_angle = np.float64(np.random.uniform(1,360))
        self.facing_angle = 1
        self.facing_angle_rad = self.facing_angle * np.pi / 180
        self.head_point = self.update_head_point()
        self.eyes = self.update_eye_point()
        self.rotate_smooth_factor: float = SpiderSettings.rotate_smooth_factor

        self.render_support: bool = SpiderSettings.render_support
        self.leg_n_limbs: int = SpiderSettings.leg_n_limbs
        self.leg_total_length: float = total_leg_length
        self.leg_support_margin: float = SpiderSettings.leg_support_margin_rate * self.leg_total_length
        self.leg_min_length: float = SpiderSettings.leg_min_length
        self.leg_point_angle: float = SpiderSettings.leg_point_angle
        self.leg_thickness: float = leg_thickness
        self.leg_smooth_factor: float = SpiderSettings.leg_smooth_factor

        self.legs: list[Tentacle] = []
        self.support_points: list[np.ndarray] = []
        self.generate_legs()
        self.generate_support_points()

    def render(self, delta_time: float):
        py.draw.circle(self.screen, self.color_body, self.pos, self.radius)
        # py.draw.circle(self.screen, Colors.WHITE, self.head_point, self.radius / 7)

        py.draw.circle(self.screen, Colors.WHITE, self.eyes[0], self.radius / 5)
        py.draw.circle(self.screen, Colors.WHITE, self.eyes[1], self.radius / 5)
        py.draw.circle(self.screen, Colors.BLACK, self.eyes[2], self.radius / 10)
        py.draw.circle(self.screen, Colors.BLACK, self.eyes[3], self.radius / 10)
        for (tentacle, point) in zip(self.legs, self.support_points):
            if self.render_support:
                py.draw.circle(self.screen, Colors.LIGHT_BLUE, point, 10)
            tentacle.point_towards(point, delta_time)
            tentacle.render()

    def update_head_point(self):
        point = self.pos + np.array([
            np.cos(self.facing_angle_rad) * self.radius,
            np.sin(self.facing_angle_rad) * self.radius
        ])
        self.head_point = point
        return point

    def update_eye_point(self):
        # Vector from the center of the circle to the head point
        direction_vector = self.head_point - self.pos
        direction_vector /= np.linalg.norm(direction_vector)
        # Get a perpendicular vector (rotate the direction vector by ±90°)
        perpendicular_vector = np.array([-direction_vector[1], direction_vector[0]])
        # perpendicular_vector = perpendicular_vector / np.linalg.norm(perpendicular_vector)  # Normalize

        # Scale the perpendicular vector by some offset distance (e.g., half the radius)
        eye_offset = self.radius * 0.5
        offset_vector = perpendicular_vector * eye_offset

        # Calculate the two eye points
        eye1 = self.pos + offset_vector - direction_vector * 15
        pupil1 = self.pos + offset_vector - direction_vector * 17
        eye2 = self.pos - offset_vector - direction_vector * 15
        pupil2 = self.pos - offset_vector - direction_vector * 17

        self.eyes = [eye1, eye2, pupil1, pupil2]
        return [eye1, eye2, pupil1, pupil2]

    def generate_legs(self):
        # Define ranges
        upper_start = self.margin_angle_rad
        upper_end = np.pi - self.margin_angle_rad
        lower_start = np.pi + self.margin_angle_rad
        lower_end = 2 * np.pi - self.margin_angle_rad

        # Generate angles
        upper_angles = np.linspace(upper_start, upper_end, self.n_legs // 2)
        lower_angles = np.linspace(lower_start, lower_end, self.n_legs // 2)
        all_angles = np.concatenate([upper_angles, lower_angles])

        # Convert to Cartesian coordinates
        points = np.array([
            [self.radius * np.cos(angle), self.radius * np.sin(angle)]
            for angle in all_angles
        ])
        points += self.pos

        self.legs = [
            Tentacle(
                screen=self.screen,
                pos=points[i],
                n_limbs=self.leg_n_limbs,
                total_length=self.leg_total_length,
                thickness=self.leg_thickness,
                smooth_factor=self.leg_smooth_factor,
                color=self.color_legs,
                shorten_first_limb=False
            )
            for i in range(self.n_legs)
        ]

    def generate_support_points(self):
        for tentacle in self.legs:
            self.support_points += [self.generate_support_point(tentacle)]

    def generate_support_point_old(self, tentacle):
        theta = np.random.uniform(-self.leg_point_angle,self.leg_point_angle)
        dist = np.random.uniform(self.leg_min_length,self.leg_total_length)
        base = tentacle.get_start_point()
        vect = base - self.pos
        theta_rad = theta * np.pi / 180  #

        vect_normal = vect / np.linalg.norm(vect)
        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(theta_rad), -np.sin(theta_rad)],
            [np.sin(theta_rad), np.cos(theta_rad)]
        ])

        vect_rotated = rotation_matrix @ vect_normal
        # Scale the rotated vector by distance d
        vect_scaled = dist * vect_rotated

        # Calculate the new point
        return base + vect_scaled
    def generate_support_point(self, tentacle):
        base = tentacle.get_start_point()
        vect = base - self.pos
        vect_normal = vect / np.linalg.norm(vect)
        return base + vect_normal * self.leg_total_length


    def move_spider_to(self, pos: Union[tuple[float, float], np.ndarray]):
        diff = pos - self.pos
        self.pos = pos
        self.update_head_point()
        self.update_eye_point()

        for i, tentacle, point in zip(range(self.n_legs), self.legs, self.support_points):
            tentacle.move_tentacle_by(diff)

            resting_point = self.generate_support_point(tentacle)
            v1 = point - resting_point
            v2 = point - tentacle.get_start_point()
            v3 = point - self.pos
            if (
                    v1[0]**2 + v1[1]**2 > self.leg_support_margin**2
                    # or v2[0]**2 + v2[1]**2 > self.leg_total_length**2
                    or v3[0]**2 + v3[1]**2 <= self.radius**2 + 25
            ):
                self.support_points[i] = resting_point


    def move_spider_by(self, pos: Union[tuple[float, float], np.ndarray]):
        if isinstance(pos, tuple):
            pos = np.array(pos)
        elif not isinstance(pos, np.ndarray):
            raise TypeError("'pos' must be a tuple or a numpy array")

        self.move_spider_to(self.pos + pos)
        # self.point_spider_towards_mouse()

    def move_spider_forward(self, delta_time):
        movement = np.array([np.cos(self.facing_angle_rad), np.sin(self.facing_angle_rad)])
        self.move_spider_by(-movement * delta_time)

    def move_spider_backwards(self, delta_time):
        movement = np.array([np.cos(self.facing_angle_rad), np.sin(self.facing_angle_rad)])
        self.move_spider_by(movement * delta_time)

    def move_spider_left(self, delta_time):
        movement = np.array([np.sin(self.facing_angle_rad), -np.cos(self.facing_angle_rad)])
        self.move_spider_by(-movement * delta_time)

    def move_spider_right(self, delta_time):
        movement = np.array([np.sin(self.facing_angle_rad), -np.cos(self.facing_angle_rad)])
        self.move_spider_by(movement * delta_time)

    def point_spider_towards_mouse(self, delta_time):
        x, y = py.mouse.get_pos()
        objective = np.array([x, y])

        # Calculate vectors
        v1 = objective - self.pos
        v2 = self.head_point - self.pos

        # Normalize vectors
        mag_v1 = np.linalg.norm(v1)
        mag_v2 = np.linalg.norm(v2)
        if mag_v1 == 0 or mag_v2 == 0:
            return  # Avoid division by zero

        v1 /= mag_v1
        v2 /= mag_v2

        # Calculate angle between v1 and v2
        dot = np.dot(v1, v2)
        cos_theta = np.clip(dot, -1.0, 1.0)
        angle_rad = np.arccos(cos_theta)

        # Determine rotation direction using the cross product
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        angle_rad *= np.sign(cross_product)

        # Rotate the spider
        self.rotate_spider(angle_rad*delta_time*self.rotate_smooth_factor)
        self.move_spider_to(self.pos)


    def rotate_spider(self, theta: float):
        # Update facing angle
        self.facing_angle_rad += theta
        self.facing_angle = np.degrees(self.facing_angle_rad)

        self.head_point = self.rotate_point_around_center(self.head_point, theta)
        for tentacle in self.legs:
            tentacle.move_tentacle_to(
                self.rotate_point_around_center(tentacle.get_start_point(), theta)
            )

    def rotate_point_around_center(self, point, angle):
        """
        Rotates a single point around a center by a given angle, maintaining the same radius.

        Parameters:
        point (np.array): The point to be rotated.
        center (np.array): The center point around which to rotate.
        angle (float): The angle to rotate the point by in radians.

        Returns:
        np.array: The rotated point, maintaining the same distance from the center.
        """
        # Calculate the relative position of the point to the center
        relative_point = point - self.pos

        # Create the rotation matrix for the given angle
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])

        # Apply the rotation matrix to the relative point
        rotated_point = rotation_matrix @ relative_point

        # Ensure the point maintains the same distance (radius) from the center
        norm_factor = np.linalg.norm(rotated_point)
        rotated_point = self.pos + rotated_point / norm_factor * np.linalg.norm(point - self.pos)

        return rotated_point