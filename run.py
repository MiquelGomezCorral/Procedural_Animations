# Library imports
import pygame as py
import numpy as np
# Implementation imports
from src.settings.settings import Settings, Colors, get_rgb_iterator
from src.utils.Text import Text, TextManagement
from src.classes import procedural_animals as pa
def main():
    # ================ INITIAL VARIABLES ================
    py.init()
    screen_info = py.display.Info()
    # set_resolution(info_object.current_w, info_object.current_h)
    SCREEN = py.display.set_mode((screen_info.current_w, screen_info.current_h)) #, py.FULLSCREEN
    py.display.set_caption('Py Procedural Animations')
    CLOCK = py.time.Clock()
    SETTINGS = Settings(WIDTH=screen_info.current_w, HEIGHT=screen_info.current_h)
    SETTINGS.SCREEN_CENTER = (SETTINGS.WIDTH / 2, SETTINGS.HEIGHT / 2)
    texts: dict ={
        'FPS': (SETTINGS.REFERENCE_FPS, 0, 0),
        'Debugging_Mode_1': (SETTINGS.OVERLAP_BODY, 0, 20),
        'Overlap_Body_2': (SETTINGS.OVERLAP_BODY, 0, 40),
        # 'ANGLE_DIF': (0, 0, 100)
    }
    TEXT_MANAGEMENT: TextManagement = TextManagement(texts)

    # ================ OBJECTS ================
    def reset_objects() -> list[pa.ProceduralCreature]:
        center = np.array(SETTINGS.SCREEN_CENTER)
        return [
            pa.ProceduralCreature(
                SCREEN,
                center + np.random.uniform(-1000, 1000, 2),
                [np.log((SETTINGS.N_PARTS-i+1))*SETTINGS.FISH_SIZE for i in range(SETTINGS.N_PARTS)],
                # [50, 40, 30, 40, 30, 40, 30, 25, 20, 20, 15, 10, 5, 5],
                color_base, color_contrast,
                overlapping_body=SETTINGS.OVERLAP_BODY
            )
            for color_base, color_contrast in
                zip(get_rgb_iterator(SETTINGS.N_FISH, 0.75), get_rgb_iterator(SETTINGS.N_FISH, 1))
        ]
    objects = reset_objects()

    # ================ RUNNING LOOP ================
    RUNNING_GAME: bool = True
    while RUNNING_GAME:
        # ================ BASE ================
        SCREEN.fill(SETTINGS.BACKGROUND_COLOR)
        delta_time = CLOCK.tick(SETTINGS.REFERENCE_FPS)
        if delta_time == 0: continue
        TEXT_MANAGEMENT.FPS.set_value(round(1/delta_time, 2)*SETTINGS.REFERENCE_FPS)
        # ================ OBJECT HANDLER ================
        for obj in objects:
            obj.follow_mouse(delta_time)
            angle = obj.render(delta_time)
            obj.update_settings(SETTINGS)
            # TEXT_MANAGEMENT.ANGLE_DIF.set_value((round(angle, 4)))
        # ================ KEY HANDLER ================
        key = py.key.get_pressed()
        if key[py.K_r]:
            objects = reset_objects()
        # elif key[py.K_w]:
        #     # spider.move_spider_by((0,-SETTINGS.MOVING_SPEED))
        #     ojects.move_spider_forward(delta_time*SETTINGS.MOVING_SPEED)
        # elif key[py.K_s]:
        #     # spider.move_spider_by((0,SETTINGS.MOVING_SPEED))
        #     ojects.move_spider_backwards(delta_time*SETTINGS.MOVING_SPEED)
        # elif key[py.K_a]:
        #     # spider.move_spider_by((-SETTINGS.MOVING_SPEED,0))
        #     ojects.move_spider_left(delta_time*SETTINGS.MOVING_SPEED)
        # elif key[py.K_d]:
        #     # spider.move_spider_by((SETTINGS.MOVING_SPEED,0))
        #     ojects.move_spider_right(delta_time*SETTINGS.MOVING_SPEED)
        # ================ EVENT HANDLER LOOP ================
        events = py.event.get()
        for event in events:
            if event.type == py.QUIT:
                RUNNING_GAME = False; break
            elif event.type == py.KEYUP:
                if event.key == py.K_ESCAPE:
                    RUNNING_GAME = False; break
                if event.key == py.K_1:
                    SETTINGS.DEBUGGING_MODE = not SETTINGS.DEBUGGING_MODE
                    TEXT_MANAGEMENT.Debugging_Mode_1.set_value(SETTINGS.DEBUGGING_MODE)
                if event.key == py.K_2:
                    SETTINGS.OVERLAP_BODY = not SETTINGS.OVERLAP_BODY
                    TEXT_MANAGEMENT.Overlap_Body_2.set_value(SETTINGS.OVERLAP_BODY)
        # ================ RE-RENDER ================
        TEXT_MANAGEMENT.render(SCREEN)
        py.display.update()

if __name__ == '__main__':
    main()