from planet import *
from camera import *
from rocket import *
from level import *
import pygame
from sys import exit

class SoftwareRender:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Orbit Game')
        self.RES = self.WIDTH, self.HEIGHT = 1280,720
        self.screen = pygame.display.set_mode(self.RES)
        self.length_per_pixel = 1.25 / 53
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.h_width = self.WIDTH // 2
        self.h_height = self.HEIGHT // 2
        
        self.scale = self.HEIGHT / 160000
        self.max_width = 160000
        self.max_height = 160000
        self.TIME_STEP = 10*24
        self.MET_TIME = 0

        self.start_time = pygame.time.get_ticks()

        self.gameStateManager = GameStateManager('VAB')
        self.start = Start(self.screen, self.gameStateManager)
        self.VAB = VAB(self.screen, self.gameStateManager, self.length_per_pixel)
        self.level = Level(self.screen, self.gameStateManager, self.screen, self.WIDTH, self.HEIGHT, self.max_width, self.max_height,
                        self.MET_TIME, self.TIME_STEP, self.start_time)
        self.groundLevel = goundLevel(self.screen, self.gameStateManager, self.screen, self.WIDTH, self.HEIGHT, self.max_width, self.max_height,
                        self.MET_TIME, self.TIME_STEP, self.start_time, self.VAB)
        
        self.states = {
            'start': self.start,
            'level': self.level,
            'VAB': self.VAB,
            'groundLevel': self.groundLevel
        }

    def draw(self, planet):
        self.screen.fill(pygame.Color('darkslategrey'))
        planet.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.states[self.gameStateManager.get_state()].run()
            pygame.display.update()
            self.clock.tick(self.FPS)

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()