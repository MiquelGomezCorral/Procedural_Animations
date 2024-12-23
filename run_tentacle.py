# Library imports
import pygame as py

# Implementation imports
from src.settings.settings import Settings, Colors
from src.utils.Text import Text, TextManagement
from src.classes import knematic_limb as kl

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
    def reset_tentacles():
        return [
            kl.Tentacle(
                SCREEN,
                (SETTINGS.MARGIN + i * (SETTINGS.WIDTH - SETTINGS.MARGIN*2)/(SETTINGS.N_TENTACLES-1),
                SETTINGS.HEIGHT - SETTINGS.MARGIN),
                SETTINGS.N_LIMBS,
                SETTINGS.TOTAL_LENGTH,
                SETTINGS.THICKNESS,
                SETTINGS.SMOOT_FACTOR,
                Colors.LIGHT_BLUE
            )
            for i in range(SETTINGS.N_TENTACLES)
        ]

    tentacles: list[kl.Tentacle] = reset_tentacles()

    # ================ RUNNING LOOP ================
    RUNNING_GAME: bool = True
    while RUNNING_GAME:
        # ================ BASE ================
        SCREEN.fill(SETTINGS.BACKGROUND_COLOR)
        delta_time = CLOCK.tick(SETTINGS.REFERENCE_FPS)
        if delta_time == 0: continue
        TEXT_MANAGEMENT.FPS.set_value(round(1/delta_time, 2)*SETTINGS.REFERENCE_FPS)
        # ================ OBJECT HANDLER ================
        for tentacle in tentacles:
            tentacle.follow_mouse(delta_time)
            tentacle.render(draw_joint= True)
        # ================ KEY HANDLER ================
        key = py.key.get_pressed()
        if key[py.K_r]:
            tentacles = reset_tentacles()
        elif key[py.K_w]:
            for tentacle in tentacles:
                tentacle.move_tentacle_by((0,-1))
        elif key[py.K_s]:
            for tentacle in tentacles:
                tentacle.move_tentacle_by((0,1))
        elif key[py.K_a]:
            for tentacle in tentacles:
                tentacle.move_tentacle_by((-1,0))
        elif key[py.K_d]:
            for tentacle in tentacles:
                tentacle.move_tentacle_by((1,0))
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