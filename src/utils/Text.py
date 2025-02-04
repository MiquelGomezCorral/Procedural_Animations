import pygame as py

class Text:
    def __init__(self, text: str, value: any, x: float, y: float, text_col: tuple = (255,255,255)):
        self.text = text
        self.pos = (x,y)
        self.text_col = text_col
        self.value = value

    def get_data(self):
        return self.text, self.pos, self.text_col, self.value

    def set_value(self, v: any):
        self.value = v

    def get_value(self):
        return self.value

    def __str__(self):
        if self.value is not None:
            return f'{self.text}: {self.value}'
        else:
            return self.text


class TextManagement:
    def __init__(self, texts: dict, text_size: int = 15, show_text: bool = True):
        self.text_font = py.font.SysFont("Arial", text_size)
        self.show_text = show_text
        for text_name, (value, x, y) in texts.items():
            setattr(self, text_name, Text(text_name, value, x, y))

    def render(self, screen, show_text: bool = True):
        self.show_text = show_text
        if not show_text: return
        for attr_name, text_to_render in self.__dict__.items():
            if isinstance(text_to_render, Text):
                img = self.text_font.render(
                    str(text_to_render), True, text_to_render.text_col
                )
                screen.blit(img, text_to_render.pos)

"""
text: dict = {
    "FPS": (10, 0, 0), # Value, Posx, Posy
    "NAME": ('Matias', 100, 100) # Value, Posx, Posy
}
text_management: TextManagement = TextManagement(text)

text_namagement.render()
"""