# Library imports
import pygame as py
import numpy as np
# Implementation imports
from src.settings.settings import Settings, SpiderSettings
from src.utils.Text import Text, TextManagement
from src.classes import spider as sp

def main():
    # ================ INITIAL VARIABLES ================
    py.init()
    screen_info = py.display.Info()
    # set_resolution(info_object.current_w, info_object.current_h)
    SCREEN = py.display.set_mode((screen_info.current_w, screen_info.current_h)) #, py.FULLSCREEN
    py.display.set_caption('Py Inverse Kinematics: Tentacles')
    CLOCK = py.time.Clock()
    SETTINGS = Settings(WIDTH=screen_info.current_w, HEIGHT=screen_info.current_h)
    texts: dict ={
        'FPS': (SETTINGS.REFERENCE_FPS, 0, 0)
    }
    TEXT_MANAGEMENT: TextManagement = TextManagement(texts)

    # ================ OBJECTS ================
    def reset_spider() -> (sp.Spider, list[sp.Spider]):
        return (sp.Spider(
            SCREEN,
            (SETTINGS.WIDTH / 2, SETTINGS.HEIGHT / 2),
            75,
            SpiderSettings.leg_n_leg,
            SpiderSettings.margin_angle,
            SpiderSettings.leg_total_length,
            SpiderSettings.leg_thickness
            ),
            [sp.Spider(
            SCREEN,
            (
                np.cos(360/(i+1))*2000 + SETTINGS.WIDTH / 2,
                np.sin(360/(i+1))*2000 + SETTINGS.HEIGHT / 2
            ),
            25,
            SpiderSettings.leg_n_leg,
            SpiderSettings.margin_angle,
            SpiderSettings.leg_total_length/3,
            SpiderSettings.leg_thickness/3
            ) for i in range(SETTINGS.N_SPIDERS)]
        )
    spider_mom: sp.Spider
    spider_kids: list[sp.Spider]
    spider_mom, spider_kids = reset_spider()
    # ================ RUNNING LOOP ================
    RUNNING_GAME: bool = True
    while RUNNING_GAME:
        # ================ BASE ================
        SCREEN.fill(SETTINGS.BACKGROUND_COLOR)
        delta_time = CLOCK.tick(SETTINGS.REFERENCE_FPS)
        if delta_time == 0: continue
        TEXT_MANAGEMENT.FPS.set_value(round(1/delta_time, 2)*SETTINGS.REFERENCE_FPS)
        # ================ OBJECT HANDLER ================
        for kid in spider_kids:
            kid.move_spider_forward(delta_time*SETTINGS.MOVING_SPEED)
            kid.point_spider_towards_mouse(delta_time)
            kid.render(delta_time)
        if SpiderSettings.render_mommy:
            spider_mom.render(delta_time)
            spider_mom.point_spider_towards_mouse(delta_time)
        # ================ KEY HANDLER ================
        key = py.key.get_pressed()
        if key[py.K_r]:
            spider_mom, spider_kids = reset_spider()
        elif key[py.K_w]:
            # spider.move_spider_by((0,-SETTINGS.MOVING_SPEED))
            spider_mom.move_spider_forward(delta_time*SETTINGS.MOVING_SPEED)
        elif key[py.K_s]:
            # spider.move_spider_by((0,SETTINGS.MOVING_SPEED))
            spider_mom.move_spider_backwards(delta_time*SETTINGS.MOVING_SPEED)
        elif key[py.K_a]:
            # spider.move_spider_by((-SETTINGS.MOVING_SPEED,0))
            spider_mom.move_spider_left(delta_time*SETTINGS.MOVING_SPEED)
        elif key[py.K_d]:
            # spider.move_spider_by((SETTINGS.MOVING_SPEED,0))
            spider_mom.move_spider_right(delta_time*SETTINGS.MOVING_SPEED)
        # ================ EVENT HANDLER LOOP ================
        events = py.event.get()
        for event in events:
            if event.type == py.QUIT:
                RUNNING_GAME = False; break
            elif event.type == py.KEYUP:
                if event.key == py.K_ESCAPE:
                    RUNNING_GAME = False; break
        # ================ RE-RENDER ================
        TEXT_MANAGEMENT.render(SCREEN)
        py.display.update()

if __name__ == '__main__':
    main()