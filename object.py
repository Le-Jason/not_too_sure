import pygame
import numpy as np
from core import *

class Main_Menu_Sprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.og_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))

        self.inverse_mass = 0
        self.position = Vector3()
        self.velocity = Vector3()
        self.rotation = 0
        self.acceleration = Vector3()


    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def set_acceleration(self, acceleration):
        pass

    def set_rotation(self, rotation):
        self.rotation = rotation
    
    def update_angle(self):
        self.angle += self.rotation

    def integrate(self, duration):

        pass

    def update(self):
        self.update_angle()
        update_positon = (self.rect.center[0], self.rect.center[1] + self.velocity)
        self.set_position(update_positon[0], update_positon[1])
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Main_Menu_Objects(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.og_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation = 0
        self.angle = 0
    
    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_rotation(self, rotation):
        self.rotation = rotation
    
    def update_angle(self):
        self.angle += self.rotation

    def update(self):
        self.update_angle()
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Background_Objects(pygame.sprite.Sprite):
    def __init__(self, image, state, length_per_pixel, display_mode='EXACT', location_init='center', size=0):
        super().__init__()
        self.og_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        [self.mask_rect_width, self.mask_rect_height] = self.get_mask_bounding_box(self.mask)

        self.state = state
        self.location_init = location_init
        self.display_mode = display_mode

        self.size = size
        self.og_width = self.rect.width
        self.og_height = self.rect.height

        
        if location_init == 'top':
            temp = self.og_height / length_per_pixel  #TODO units
            self.state[1] -= 8

        self.test = state[1]

        self.rotation = 0.0

    def update_state(self, rocket):
        pos = rocket.state[:3]
        unit_vec = np.array(pos) / np.linalg.norm(pos)  
        self.state = [self.test*unit_vec[0], self.test*unit_vec[1], self.test*unit_vec[2], 0, 0, 0]
        self.rotation = -1*np.rad2deg(np.arctan2(unit_vec[0], unit_vec[1]))
    
    def scaled_image(self, scale):
        scaled_width = int(self.og_width * scale)
        scaled_height = int(self.og_height * scale)
        self.image = pygame.transform.scale(self.og_image, (scaled_width, scaled_height))
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_mask_bounding_box(self, mask):
        # Get the size of the mask
        width, height = mask.get_size()
        
        # Initialize the bounding box coordinates
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        
        # Iterate over the mask to find the bounding box of non-transparent pixels
        for x in range(width):
            for y in range(height):
                if mask.get_at((x, y)):
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y

        # Return the bounding box dimensions
        return (max_x - min_x + 1, max_y - min_y + 1)