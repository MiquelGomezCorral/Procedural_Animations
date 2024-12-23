from dataclasses import dataclass


color_type = tuple[int,int,int]
@dataclass
class Colors:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    DARK_BLUE = (23, 56, 102)
    LIGHT_BLUE = (68, 190, 242)
    LIGHT_GREY = (87, 121, 156)

@dataclass
class Settings:
    BACKGROUND_COLOR: color_type = Colors.LIGHT_GREY
    REFERENCE_FPS: int = 1200

    WIDTH: float = 1024
    HEIGHT: float = 1024
    SCREEN_CENTER: tuple[float,float] = (WIDTH // 2, HEIGHT // 2)
    MARGIN: float = 100

    MOVING_SPEED: float = 0.5

    SMOOT_FACTOR: float = 0.01
    N_PARTS: int = 10
