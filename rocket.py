import pygame

class Rocket(pygame.sprite.Sprite):
    def __init__(self, pos, group, scale):
        super().__init__(group)
        pos = (pos[0] * scale, pos[1] * scale)
        self.image = pygame.image.load('graphics/rocket.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.x = pos[0]
        self.y = pos[1]
        self.vx = 0
        self.vy = 0
        self.mass = 100
        self.TIMESTEP = 100*24
        self.font = pygame.font.Font('font/Pixeltype.ttf', 25)
        self.orbit_parameters_text = [f"Semimajor Axis: {3}",
                                    f"Eccentricity: {3}",
                                    f"Inclination: {3}",
                                    f"RAAN: {3}",
                                    f"Arguemnt of P: {3}",
                                    f"True Anomaly: {3}"]
        for line in self.orbit_parameters_text:
            self.font_surface = self.font.render(line, False, 'Blue')
    
    def update_position(self, fx, fy):
        self.vx += fx / self.mass * self.TIMESTEP
        self.vy += fy / self.mass * self.TIMESTEP
        self.x += self.vx * self.TIMESTEP
        self.y += self.vy * self.TIMESTEP