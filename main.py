from planet import *
from camera import *
from rocket import *
import pygame
from sys import exit

class SoftwareRender:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Orbit Game')
        self.RES = self.WIDTH, self.HEIGHT = 640,640
        self.screen = pygame.display.set_mode(self.RES)
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.scale = self.HEIGHT / 160000

    def draw(self, planet):
        self.screen.fill(pygame.Color('darkslategrey'))
        planet.update()


    def run(self):

        camera_group = CameraGroup()
        planet = Planet((self.WIDTH // 2, self.HEIGHT // 2),camera_group)
        rocket = Rocket((160000, 0), camera_group, self.scale)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            force_x, force_y = planet.gravity_two_body(rocket)
            rocket.update_position(force_x, force_y)

            camera_group.update()
            camera_group.custom_draw()
            
            self.screen.blit(rocket.image, (rocket.x/1E30, rocket.y/1E30))

            y_pos = 0
            for line in rocket.orbit_parameters_text:
                text = rocket.font.render(line, False, 'Blue')
                self.screen.blit(text, (500, y_pos))
                y_pos += text.get_height()

            pygame.display.update()
            self.clock.tick(self.FPS)

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()