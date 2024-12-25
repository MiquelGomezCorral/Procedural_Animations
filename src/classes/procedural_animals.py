import numpy as np
import pygame as py

from src.settings.settings import Colors, Settings, color_type
from src.utils import utils


class WobblyEyes:
    def __init__(self, screen, pos1: utils.point_type, pos2: utils.point_type, radius: float):
        self.screen = screen
        self.pos1 = utils.parse_point(pos1)
        self.pos2 = utils.parse_point(pos2)
        self.radius = radius

    def render(self):
        mouse = utils.parse_point(py.mouse.get_pos())
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
    def __init__(self, screen, pos: utils.point_type, body_size: list[float], color_base: color_type, color_contrast: color_type, overlapping_body: bool = False):
        self.screen = screen

        self.n = len(body_size)
        self.n_points_smooth = self.n * 5
        self.body_size = body_size
        self.body_pos = [utils.parse_point(pos)]
        self.body_direction = np.array([0,0], dtype=float)
        self.start_body_pos()
        self.color_base = color_base
        self.color_contrast = color_contrast
        self.width = 1
        self.overlapping_body = overlapping_body

        pos1, pos2 = self.get_eyes_pos()
        self.eyes = WobblyEyes(self.screen, pos1, pos2, body_size[0]*0.5)

    def render(self, delta_time: float):
        perpend = np.array([self.body_direction[1], -self.body_direction[0]])
        nose1 = self.body_direction * self.body_size[0]*1.25 + self.body_pos[0]
        nose2 = self.body_direction * self.body_size[0] + self.body_pos[0] - perpend * self.body_size[0] * 0.6
        nose3 = self.body_direction * self.body_size[0] + self.body_pos[0] + perpend * self.body_size[0] * 0.6

        shape_1: list[utils.point_type] = [
            nose2, nose1, nose3,
            perpend * self.body_size[0] + self.body_pos[0]
        ]
        shape_2: list[utils.point_type] = [
            -perpend * self.body_size[0] + self.body_pos[0]
        ]
        for i in range(1, self.n):
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

        points = shape_1 + list(reversed(shape_2)) # Connect the pairs of points
        if Settings.DEBUGGING_MODE:
            for body_part, body_size in zip(self.body_pos, self.body_size):
                py.draw.circle(self.screen, Colors.WHITE, body_part, body_size, self.width)
                py.draw.circle(self.screen, Colors.WHITE, body_part, 5)
            for point in points:
                py.draw.circle(self.screen, Colors.BLACK, point, 5)
        else:
            x_smooth, y_smooth = utils.b_spline(points + [points[0]], self.n_points_smooth) # add first point again to close loop
            smooth_points = list(zip(x_smooth, y_smooth))

            self.draw_fin_lateral_fin(int(self.n * 0.2))
            self.draw_fin_lateral_fin(int(self.n * 0.7))

            self.draw_fin_back_fin(int(self.n * 0.5))

            py.draw.polygon(self.screen, self.color_base, smooth_points)  # Fill
            py.draw.polygon(self.screen, Colors.WHITE, smooth_points, 3)  # Shape
            self.eyes.render()

    def get_eyes_pos(self) -> tuple[utils.point_type, utils.point_type]:
        perpend = np.array([self.body_direction[1], -self.body_direction[0]])
        pos1 = self.body_direction * self.body_size[0] + self.body_pos[0] - perpend * self.body_size[0] * 0.6
        pos2 = self.body_direction * self.body_size[0] + self.body_pos[0] + perpend * self.body_size[0] * 0.6
        return pos1, pos2

    def update_eyes_pos(self):
        self.eyes.set_pos(*self.get_eyes_pos())

    def draw_fin_back_fin(self, index: int):
        if index < 2 :
            index = 2
        direction = self.body_pos[index - 2] - self.body_pos[index]
        direction /= np.linalg.norm(direction)
        perpend = np.array([direction[1], -direction[0]])

        width  = self.body_size[index] * 0.5
        height = self.body_size[index] * 0.75
        # fin 1
        fin_point_1 = perpend * self.body_size[index] + self.body_pos[index]
        direction_1 = self.body_pos[index - 1] - fin_point_1
        direction_1 /= np.linalg.norm(direction_1)
        perpend_1 = np.array([direction_1[1], -direction_1[0]])

        points_fin_1 = [
            fin_point_1 + direction_1 * height,
            fin_point_1 + perpend_1 * width,
            fin_point_1 - direction_1 * height,
            fin_point_1 - perpend_1 * width,
        ]

        fin_point_2 = - perpend * self.body_size[index] + self.body_pos[index]
        direction_2 = self.body_pos[index - 1] - fin_point_2
        direction_2 /= np.linalg.norm(direction_2)
        perpend_2 = np.array([direction_2[1], -direction_2[0]])

    def draw_fin_lateral_fin(self, index: int):
        if index < 2 :
            index = 2
        direction = self.body_pos[index - 2] - self.body_pos[index]
        direction /= np.linalg.norm(direction)
        perpend = np.array([direction[1], -direction[0]])

        width  = self.body_size[index] * 0.5
        height = self.body_size[index] * 0.75
        # fin 1
        fin_point_1 = perpend * self.body_size[index] + self.body_pos[index]
        direction_1 = self.body_pos[index - 1] - fin_point_1
        direction_1 /= np.linalg.norm(direction_1)
        perpend_1 = np.array([direction_1[1], -direction_1[0]])

        points_fin_1 = [
            fin_point_1 + direction_1 * height,
            fin_point_1 + perpend_1 * width,
            fin_point_1 - direction_1 * height,
            fin_point_1 - perpend_1 * width,
        ]

        fin_point_2 = - perpend * self.body_size[index] + self.body_pos[index]
        direction_2 = self.body_pos[index - 1] - fin_point_2
        direction_2 /= np.linalg.norm(direction_2)
        perpend_2 = np.array([direction_2[1], -direction_2[0]])

        points_fin_2 = [
            fin_point_2 + direction_2 * height,
            fin_point_2 + perpend_2 * width,
            fin_point_2 - direction_2 * height,
            fin_point_2 - perpend_2 * width,
        ]
        x_smooth, y_smooth = utils.b_spline(points_fin_1 + [points_fin_1[0]], 16)  # add first point again to close loop
        smooth_points = list(zip(x_smooth, y_smooth))
        py.draw.polygon(self.screen, self.color_contrast, smooth_points)  # Fill
        py.draw.polygon(self.screen, Colors.WHITE, smooth_points, 3)

        x_smooth, y_smooth = utils.b_spline(points_fin_2 + [points_fin_2[0]], 16)  # add first point again to close loop
        smooth_points = list(zip(x_smooth, y_smooth))
        py.draw.polygon(self.screen, self.color_contrast, smooth_points)  # Fill
        py.draw.polygon(self.screen, Colors.WHITE, smooth_points, 3)

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

    def move_towards(self, point: utils.point_type, delta_time: float):
        noise = np.random.uniform(-1e-2,1e-2)
        direction = self.body_direction + noise + (point - self.body_pos[0]) * delta_time * 1e-5
        direction /= np.linalg.norm(direction)
        self.body_direction = direction
        self.body_pos[0] += self.body_direction * delta_time * Settings.MOVING_SPEED
        self.update_eyes_pos()

        self.update_body_pos(self.overlapping_body)