from dataclasses import dataclass


@dataclass
class Colors:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    DARK_BLUE = (23, 56, 102)
    LIGHT_BLUE = (68, 190, 242)
    LIGHT_GREY = (87, 121, 156)

@dataclass
class Settings:
    BACKGROUND_COLOR: tuple[int] = Colors.LIGHT_GREY
    REFERENCE_FPS: int = 1200

    WIDTH: float = 1024
    HEIGHT: float = 1024
    MARGIN: float = 100

    MOVING_SPEED: float = 0.5

    SMOOT_FACTOR: float = 0.01
    N_TENTACLES: int = 5
    N_SPIDERS: int = 25
    N_LIMBS: int = 5
    TOTAL_LENGTH: float = 500
    THICKNESS: float = 15
    MAX_BEND_LIMB: float = 10

@dataclass
class SpiderSettings:
    render_support: bool = False
    render_mommy: bool = False

    rotate_smooth_factor: float = 0.001
    margin_angle: float = 60
    leg_n_leg: int = 8
    leg_n_limbs: int = 2
    leg_total_length: float = 100
    leg_support_margin_rate: float = 1.25
    leg_min_length: float = 150
    leg_point_angle: float = 10
    leg_thickness: float = 2.5
    leg_smooth_factor: float = 0.1
