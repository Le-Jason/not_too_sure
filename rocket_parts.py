import pygame
from data.part_data import *
import json

class RocketManager():
    def __init__(self):
        self.parts = pygame.sprite.Group()

    def add_part(self, rocket_part):
        self.parts.add(rocket_part)

class RocketPart(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        # Setting up data
        with open('data/part_label.json', 'r') as file:
            data = json.load(file)
        self.data = data[name]
        # Setting up image
        self.image = pygame.image.load(self.data['image']).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))

    def initialization(self):
        pass

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, mouse_position, display_surface):
        local_x = mouse_position[0]
        local_y = mouse_position[1]
        self.set_position(local_x, local_y)
        display_surface.blit(self.image, self.rect)
