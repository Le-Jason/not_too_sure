import pygame

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.ground_surf = pygame.image.load('graphics/space.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))
    def custom_draw(self):

        self.display_surface.blit(self.ground_surf, self.ground_rect)

        # for sprite in self.sprites():
        #     self.display_surface.blit(sprite.image, sprite.rect)