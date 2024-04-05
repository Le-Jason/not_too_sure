import pygame

class vab_ui_button:
    def __init__(self, pos, size):
        self.rec = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.rec.fill((255, 0, 0, 128))  # Fill the surface with a transparent red color
        self.rec_rect = self.rec.get_rect(topleft=(pos[0], pos[1]))

    def click():
        pass