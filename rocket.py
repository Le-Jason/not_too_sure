import pygame
import math as m
import numpy as np

from Algorithms.KeplerProblems import *

class StructFrame():
    def __init__(self, parts, cg, length_per_pixel):
        body_bottom = 0
        body_top = 0
        body_right = 0
        body_left = 0
        init = False
        for part in parts:
            if init == False:
                body_bottom = part.rect.bottom
                body_top = part.rect.top
                body_right = part.rect.right
                body_left = part.rect.left
                body_center = part.rect.center
                init = True
            else:
                if part.rect.bottom > body_bottom:
                    body_bottom = part.rect.bottom
                if part.rect.top < body_top:
                    body_top = part.rect.top
                    body_center = part.rect.center
                if part.rect.right > body_right:
                    body_right = part.rect.right
                if part.rect.left < body_left:
                    body_left = part.rect.left
        for part in parts:
            relative_center_part_x = part.rect.center[0] - body_center[0]
            relative_center_part_y = part.rect.center[1] - body_top
            part.relative_struct_real = (relative_center_part_x, relative_center_part_y)
        cg_x = (cg[0] - body_center[0])
        cg_y = (cg[1] - body_top)

        self.height = (body_bottom - body_top)*length_per_pixel
        self.width = (body_right - body_left)*length_per_pixel
        self.origin = (-cg_x, -cg_y)
        self.parts = parts
        self.rotation = 0

class Rocket():
    def __init__(self, rocket, length_per_pixel):
        self.length_per_pixel = length_per_pixel

        # Create rocket frame
        self.struct_frame = StructFrame(rocket.parts, rocket.cg_location, self.length_per_pixel)
        self.parts = rocket.parts
        self.cg_location = rocket.cg_location
        self.collision = False

        self.state = [0, 6384.563186792453, 0 , 0, 0, 0]
        self.prev_state = [0, 6384.563186792453, 0 , 0, 0, 0]

    def rocket_rotate(self, motion):
        if motion:
            self.struct_frame.rotation += 1
        else:
            self.struct_frame.rotation -= 1

    def rocket_fire(self):
        temp_isp = 300
        temp_g0 =  9.80665
        temp_F = 20
        delta_m = temp_F / (temp_isp * temp_g0)
        temp_m0 = 1000
        delta_v = temp_isp*temp_g0*m.log(temp_m0 / (temp_m0 - (delta_m*1)))


        vector = [0, delta_v]
        vector_x = vector[0]*np.cos(np.deg2rad(-1*self.struct_frame.rotation)) - vector[1]*np.sin(np.deg2rad(-1*self.struct_frame.rotation))
        vector_y = vector[0]*np.sin(np.deg2rad(-1*self.struct_frame.rotation)) + vector[1]*np.cos(np.deg2rad(-1*self.struct_frame.rotation))


        self.state = [self.state[0], self.state[1], 0, self.state[3] + vector_x, self.state[4] + vector_y, 0]

    def update(self):
        pass

    def get_visible_rect(self, image):
        rect = image.get_rect()
        mask = pygame.mask.from_surface(image)
        non_transparent_pixels = mask.outline()

        # Find the minimum bounding box of the non-transparent pixels
        min_x = min(pixel[0] for pixel in non_transparent_pixels)
        max_x = max(pixel[0] for pixel in non_transparent_pixels)
        min_y = min(pixel[1] for pixel in non_transparent_pixels)
        max_y = max(pixel[1] for pixel in non_transparent_pixels)
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Adjust the position of the rectangle to match the sprite's position
        x, y = rect.topleft
        return pygame.Rect(x + min_x, y + min_y, width, height)