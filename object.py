import pygame
import numpy as np
from core import *

class Main_Menu_Sprite_2(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_image, frame_width, frame_height, animations):
        super().__init__()
        self.sprite_sheet = pygame.image.load(sprite_sheet_image).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.animations = animations  # Dictionary of animations

        self.current_animation = 'idle'  # Default animation
        self.current_frame_index = 0
        self.frame_rate = 10
        self.last_update = pygame.time.get_ticks()

        # Initialize the sprite image and rect
        self.image, self.rect = self.get_frame(self.current_animation, self.current_frame_index)

        self.rotation = 0
        self.angle = 0
        self.position = Vector3()
        self.velocity = Vector3()
        self.acceleration = Vector3()

    def extract_frames(self, start_index, num_frames):
        frames = []
        for i in range(num_frames):
            x = (start_index + i) * self.frame_width
            frame_rect = pygame.Rect(x, 0, self.frame_width, self.frame_height)
            frames.append(self.sprite_sheet.subsurface(frame_rect))
        return frames

    def get_frame(self, animation_name, index):
        start_index, num_frames = self.animations.get(animation_name, (0, 0))
        frames = self.extract_frames(start_index, num_frames)
        if frames:
            return frames[index % len(frames)], pygame.Rect(self.frame_width // 2, self.frame_height // 2, self.frame_width, self.frame_height)
        return pygame.Surface((self.frame_width, self.frame_height)), pygame.Rect(self.frame_width // 2, self.frame_height // 2, self.frame_width, self.frame_height)

    def add_animation(self, name, start_index, num_frames):
        self.animations[name] = (start_index, num_frames)

    def set_animation(self, name):
        if name in self.animations and name != self.current_animation:
            self.current_animation = name
            self.current_frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.og_image, self.rect = self.get_frame(self.current_animation, self.current_frame_index)

    def set_position(self, x, y, z):
        self.position = Vector3(x, y, z)
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_velocity(self, x, y, z):
        self.velocity = Vector3(x, y, z)

    def set_acceleration(self, x, y, z):
        self.acceleration = Vector3(x, y, z)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def set_angle(self, angle):
        self.angle = angle

    def integrate(self, dt):
        self.velocity.addScaledVector(self.acceleration, dt)
        self.position.addScaledVector(self.velocity, dt)
        self.angle += self.rotation * dt

    def update(self):
        self.integrate(1 / 60)
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 // self.frame_rate:
            self.last_update = now
            self.current_frame_index = (self.current_frame_index + 1) % self.animations[self.current_animation][1]
            self.og_image, self.rect = self.get_frame(self.current_animation, self.current_frame_index)
        self.set_position(self.position.x, self.position.y, 0)
        self.set_angle(self.angle)
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Main_Menu_Sprite(pygame.sprite.Sprite):
    def __init__(self, animations):
        super().__init__()

        self.animations = animations
        first_key = next(iter(animations))
        self.current_animation = first_key
        self.current_frame_index = 0
        self.frame_width = self.animations[self.current_animation][2][0]
        self.frame_height = self.animations[self.current_animation][2][1]
        self.last_update = pygame.time.get_ticks()

        self.image, self.rect = self.get_frame(self.current_animation, self.current_frame_index)

        self.rotation = 0
        self.angle = 0
        self.position = Vector3()
        self.velocity = Vector3()
        self.acceleration = Vector3()

    def add_animation(self, name, image_path):
        sheet = pygame.image.load(image_path).convert_alpha()
        frames = self.extract_frames(sheet)
        self.animations[name] = (sheet, frames)

    def extract_frames(self, sheet):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frame_rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
                frames.append(sheet.subsurface(frame_rect))
        return frames

    def get_frame(self, animation_name, index):
        sheet, frames = self.animations.get(animation_name)
        if sheet:
            return frames[index], pygame.Rect(self.frame_width // 2, self.frame_height // 2, self.frame_width, self.frame_height)
        return pygame.Surface((self.frame_width, self.frame_height)), pygame.Rect(self.frame_width // 2, self.frame_height // 2, self.frame_width, self.frame_height)


    def set_position(self, x, y, z):
        self.position = Vector3(x, y ,z)
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_velocity(self, x, y, z):
        self.velocity = Vector3(x, y ,z)

    def set_acceleration(self, x, y, z):
        self.acceleration = Vector3(x, y ,z)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def set_angle(self, angle):
        self.angle = angle

    def integrate(self, dt):
        # Assume gravity in the acceleration vector
        self.velocity.addScaledVector(self.acceleration, dt)
        self.position.addScaledVector(self.velocity, dt)
        self.angle += self.rotation * dt

        self.set_position(self.position.x, self.position.y, 0)
        self.set_angle(self.angle)

    def update(self):
        self.integrate(1/60)
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Main_Menu_Objects(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        # Load the image and set up initial properties
        self.og_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)

        # Dimension Variables
        self.og_width = self.rect.width
        self.og_height = self.rect.height

        # Scaling Variables
        self.scaled_width = self.og_width
        self.scaled_height = self.og_height

        self.rotation = 0
        self.angle = 0

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def set_scale(self, scale):
        self.scaled_width = int(self.og_width * scale)
        self.scaled_height = int(self.og_height * scale)

    def update_angle(self):
        self.angle += self.rotation

    def update(self):
        self.update_angle()
        self.image = pygame.transform.scale(self.og_image, (self.scaled_width, self.scaled_height))
        self.image = pygame.transform.rotate(self.image, self.angle)
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