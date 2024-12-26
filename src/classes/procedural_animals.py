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
    def __init__(self, screen, pos: utils.point_type,
                 body_size: list[float], color_base: color_type,
                 color_contrast: color_type, overlapping_body: bool = False,
                 debugging_mode: bool = False
    ):
        self.screen = screen

        self.n = len(body_size)
        self.avg_body_size = sum(body_size) / self.n
        self.angle_dif = 0

        self.body_size = body_size
        self.body_pos = [utils.parse_point(pos)]
        self.body_direction = np.array([0,0], dtype=float)
        self.start_body_pos()
        self.color_base = color_base
        self.color_contrast = color_contrast

        self.overlapping_body = overlapping_body
        self.debugging_mode = debugging_mode
        self.n_points_smooth = int(self.n * 5 + body_size[0])
        self.fin_points = 16

        pos1, pos2 = self.get_eyes_pos()
        self.eyes = WobblyEyes(self.screen, pos1, pos2, body_size[0]*0.5)

    def update_settings(self, settings: Settings):
        self.overlapping_body = settings.OVERLAP_BODY
        self.debugging_mode = settings.DEBUGGING_MODE

    def draw_smooth_points(self, points, n_points_smooth: int = None, color: color_type = None):
        if n_points_smooth is None:
            n_points_smooth = self.n_points_smooth
        if color is None:
            color = self.color_base

        x_smooth, y_smooth = utils.b_spline(points + [points[0]], n_points_smooth)  # add first point again to close loop
        smooth_points = list(zip(x_smooth, y_smooth))
        py.draw.polygon(self.screen, color, smooth_points)  # Fill
        py.draw.polygon(self.screen, Colors.WHITE, smooth_points, 3)  # Shape

    def draw_debug_points(self, points, size: float = 3, color: color_type = Colors.BLACK):
        for point in points:
            py.draw.circle(self.screen, color, point, size)

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

        prev_dir = self.body_direction
        self.angle_dif = 0
        for i in range(1, self.n -1):
            direction = self.body_pos[i-1] - self.body_pos[i]
            direction /= np.linalg.norm(direction)
            perpend = np.array([direction[1], -direction[0]])

            angle_dif = utils.compute_angle(direction, prev_dir, normalized=True) # Both normalized, denominator = 1
            self.angle_dif += utils.cross_product(direction, prev_dir) * angle_dif
            prev_dir = direction

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

        # Add the point with the tail
        if self.n > 1:
            direction = self.body_pos[-2] - self.body_pos[-1]
            direction /= np.linalg.norm(direction)

            angle_dif = utils.compute_angle(direction, prev_dir, normalized=True)  # Both normalized, denominator = 1
            self.angle_dif += utils.cross_product(direction, prev_dir) * angle_dif

            tail = -direction * self.body_size[-1] + self.body_pos[-1]
            shape_1 += [perpend * self.body_size[-1] + self.body_pos[-1],
                        tail]
            shape_2 += [-perpend * self.body_size[-1] + self.body_pos[-1]]

        self.angle_dif = np.degrees(self.angle_dif / (self.n - 1))  # Number of angles between body parts

        shape_points = shape_1 + list(reversed(shape_2)) # Connect the pairs of points
        if self.debugging_mode:
            for body_part, body_size in zip(self.body_pos, self.body_size):
                py.draw.circle(self.screen, Colors.WHITE, body_part, body_size, 1)
                py.draw.circle(self.screen, Colors.WHITE, body_part, 5)
            self.draw_debug_points(shape_points, 5)

        self.draw_fin_lateral_fin(int(self.n * 0.2))
        self.draw_fin_lateral_fin(int(self.n * 0.7))
        self.draw_tail_fin()
        if not self.debugging_mode:
            self.draw_smooth_points(shape_points)
            self.eyes.render()
        self.draw_fin_back_fin(int(self.n * 0.3))

        return self.angle_dif

    def get_eyes_pos(self) -> tuple[utils.point_type, utils.point_type]:
        perpend = np.array([self.body_direction[1], -self.body_direction[0]])
        pos1 = self.body_direction * self.body_size[0] + self.body_pos[0] - perpend * self.body_size[0] * 0.6
        pos2 = self.body_direction * self.body_size[0] + self.body_pos[0] + perpend * self.body_size[0] * 0.6
        return pos1, pos2

    def update_eyes_pos(self):
        self.eyes.set_pos(*self.get_eyes_pos())

    def draw_tail_fin(self):
        assert self.n >= 3, "Need at least 3 parts to draw the tail fin"

        direction = self.body_pos[-2] - self.body_pos[-1]
        direction /= np.linalg.norm(direction)
        perpend = np.array([direction[1], -direction[0]])

        fin_length_prop = 2
        points_fin = [
            self.body_pos[-1] - direction*self.body_size[-1]*0.5, # hidden inside the sape so it curves (more or less)
            self.body_pos[-1] - direction*self.avg_body_size*fin_length_prop * 0.2,
            # self.body_pos[-1] - direction*self.avg_body_size*fin_length_prop * 0.5,
            self.body_pos[-1] - direction*self.avg_body_size*fin_length_prop * 0.8,
            self.body_pos[-1] - direction*self.avg_body_size*fin_length_prop - perpend*self.angle_dif
        ]

        if self.debugging_mode:
            self.draw_debug_points(points_fin, color=Colors.RED)
        else:
            self.draw_smooth_points(points_fin, self.fin_points * 2, self.color_contrast)

    def draw_fin_back_fin(self, index: int):
        assert self.n >= 4, "Need at least 4 parts to draw the back fin"

        points_fin = list(self.body_pos[index - 1 : index + 2])
        for i in range(index-1, index+2): #[i-1, i, i+1]
            direction = self.body_pos[i - 1] - self.body_pos[i]
            # No normalization so we get the "angle" / "Distance" between two segments
            direction_norm = direction / np.linalg.norm(direction)
            points_fin = [self.body_pos[i] - direction_norm*self.body_size[i]] + points_fin

        if self.debugging_mode:
            self.draw_debug_points(points_fin, color=Colors.RED)
        else:
            self.draw_smooth_points(points_fin, self.fin_points * 2, self.color_contrast)

    def draw_fin_lateral_fin(self, index: int):
        assert self.n >= 2, "Need at least 2 parts to draw the side fins"
        if index < 2 :
            index = 2
        direction = self.body_pos[index - 2] - self.body_pos[index]
        direction /= np.linalg.norm(direction)
        perpend = np.array([direction[1], -direction[0]])

        width  = self.avg_body_size * 0.5
        height = self.avg_body_size * 0.75
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
        if self.debugging_mode:
            self.draw_debug_points(points_fin_1 + points_fin_2, color=Colors.RED)

        else:
            self.draw_smooth_points(points_fin_1, self.fin_points, self.color_contrast)
            self.draw_smooth_points(points_fin_2, self.fin_points, self.color_contrast)

    def start_body_pos(self, ):
        positions = [self.body_pos[0]]
        for i, size in enumerate(self.body_size[1:]):  # Starts in 0 so is like "i-1"
            positions +=  [np.array([positions[i][0], positions[i][1] - size*2])]
        self.body_pos = np.array(positions)

    def update_body_pos(self):
        for i in range(1, self.n):
            direction = self.body_pos[i-1] - self.body_pos[i]
            dist = np.linalg.norm(direction)
            direction /= dist
            if self.overlapping_body:
                # NOT OVER-LAPPING BODY
                dist -= (self.body_size[i] + self.body_size[i-1])
            else:
                if self.body_size[i] >= self.body_size[i-1]:
                    dist -= self.body_size[i]
                else:
                    dist -= self.body_size[i - 1]

            self.body_pos[i] += direction * dist # Dist is how much the boyd has to be moved

    def follow_mouse(self, delta_time: float):
        x, y = py.mouse.get_pos()
        # self.point_towards((x, y), delta_time)
        self.move_towards((x, y), delta_time)

    def move_towards(self, point: utils.point_type, delta_time: float):
        noise = np.random.uniform(-1e-2,1e-2)
        direction = self.body_direction + noise + (point - self.body_pos[0]) * delta_time * Settings.SMOOT_FACTOR
        direction /= np.linalg.norm(direction)
        self.body_direction = direction
        self.body_pos[0] += self.body_direction * delta_time * Settings.MOVING_SPEED
        self.update_eyes_pos()

        self.update_body_pos()