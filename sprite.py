import pygame
from core import *

class AnimationSprite(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_image, frame_width, frame_height, animations):
        super().__init__()
        self.sprite_sheet = pygame.image.load(sprite_sheet_image).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.animations = animations

        self.current_animation = next(iter(animations)) # Default animation
        self.current_frame_index = 0
        self.current_cycle = self.animations[self.current_animation][1]
        self.last_update = pygame.time.get_ticks()

        # Initialize the sprite image and rect
        self.og_image = self.get_frame(self.current_animation, self.current_frame_index)

    def get_frame(self, animation_name, index):
        data = self.animations.get(animation_name, [(0, 0), (0)])
        start_index = data[0][0]
        num_frame = data[0][1]
        self.current_cycle = data[1]
        frames = self.extract_frames(start_index, num_frame)
        if frames:
            return frames[index % len(frames)]
        return pygame.Surface((self.frame_width, self.frame_height))

    def extract_frames(self, start_index, num_frames):
        frames = []
        for i in range(num_frames):
            x = (start_index + i) * self.frame_width
            frame_rect = pygame.Rect(x, 0, self.frame_width, self.frame_height)
            frames.append(self.sprite_sheet.subsurface(frame_rect))
        return frames

    def add_animation(self, name, start_index, num_frames, cycles):
        self.animations[name] = [(start_index, num_frames), cycles]

    def set_animation(self, name):
        if name in self.animations and name != self.current_animation:
            self.current_animation = name
            self.current_frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.og_image = self.get_frame(self.current_animation, self.current_frame_index)

    def update(self):
        # Cycle the animation if the frame is not zero seconds
        if self.current_cycle[self.current_frame_index] > 0:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.current_cycle[self.current_frame_index]:
                self.last_update = now
                self.current_frame_index = (self.current_frame_index + 1) % self.animations[self.current_animation][0][1]
                self.og_image = self.get_frame(self.current_animation, self.current_frame_index)

class MainMenuSprite(AnimationSprite):
    def __init__(self, sprite_sheet_image, frame_width, frame_height, animations):
        super().__init__(sprite_sheet_image, frame_width, frame_height, animations)
        self.image = pygame.image.load(sprite_sheet_image).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))

        self.rotation = 0
        self.angle = 0
        self.position = Vector3()
        self.velocity = Vector3()
        self.acceleration = Vector3()

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
        super().update()
        self.integrate(1 / 60)
        self.set_position(self.position.x, self.position.y, 0)
        self.set_angle(self.angle)
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)