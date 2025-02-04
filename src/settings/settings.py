from dataclasses import dataclass
import matplotlib.colors as mcolors

color_type = tuple[int,int,int]
@dataclass
class Colors:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    DARK_BLUE = (23, 56, 102)
    LIGHT_BLUE = (68, 190, 242)
    LIGHT_GREY = (87, 121, 156)
    GREEN = (104, 171, 108)
    RED = (255, 0, 0)

def get_rgb_iterator(n_colors, light: float = 0.7):
    # Generate evenly spaced colors in HSV space
    hsv_colors = [(i / n_colors, 1.0, 1.0) for i in range(n_colors)]
    # Convert HSV to RGB
    rgb_colors = [tuple(mcolors.hsv_to_rgb(hsv)) for hsv in hsv_colors]
    # Scale RGB values to 0-255 if needed (optional)
    rgb_colors_scaled = [(int(r * 255 * light), int(g * 255 * light), int(b * 255 * light)) for r, g, b in rgb_colors]
    return rgb_colors_scaled

@dataclass
class Settings:
    RUNNING: bool = True
    SHOW_TEXT: bool = True

    DEBUGGING_MODE: bool = False
    SPECIAL_SMOOTHING: bool = False
    OVERLAP_BODY: bool = False

    DRAW_EYES: bool = True
    DRAW_FINS: bool = True
    DRAW_LEGS: bool = False

    BACKGROUND_COLOR: color_type = Colors.LIGHT_GREY
    REFERENCE_FPS: int = 1200

    WIDTH: float = 1024
    HEIGHT: float = 1024
    SCREEN_CENTER: tuple[float,float] = (WIDTH // 2, HEIGHT // 2)
    MARGIN: float = 100

    MOVING_SPEED: float = 0.5
    SMOOT_FACTOR: float = 1e-5

    N_ANIMALS: int = 1
    N_PARTS: int = 10
    FISH_SIZE: float = 1
    FISH_REFERENCE_SIZE: float = 15
