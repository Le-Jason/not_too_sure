from planet import *
from camera import *
from rocket import *
from level import *
import pygame
from sys import exit

class SoftwareRender:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Orbit Game')
        self.RES = self.WIDTH, self.HEIGHT = 1280,720
        self.screen = pygame.display.set_mode(self.RES)
        self.length_per_pixel = 1.25 / 53 # m to pixel
        self.length_per_pixel_map = 6378136.3 / 193.5 # Based on Earth pixel map
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.h_width = self.WIDTH // 2
        self.h_height = self.HEIGHT // 2
        self.TIME_STEP = 10*24
        self.system_info = {
            'length_per_pixel': self.length_per_pixel,
            'length_per_pixel_map': self.length_per_pixel_map,
            'WIDTH': self.WIDTH,
            'HEIGHT': self.HEIGHT,
            'TIME_STEP': self.TIME_STEP,
        }

        self.start_time = pygame.time.get_ticks()

        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager, self.system_info)
        self.VAB = VAB(self.screen, self.gameStateManager, self.system_info)
        self.level = Level(self.screen, self.gameStateManager, self.screen, self.system_info, self.start_time, self.VAB)
        
        self.states = {
            'start': self.start,
            'level': self.level,
            'VAB': self.VAB,
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
            if self.gameStateManager.currentState != self.gameStateManager.prev_state:
                self.gameStateManager.prev_state = self.gameStateManager.currentState
                self.states[self.gameStateManager.get_state()].initialization()
            self.states[self.gameStateManager.get_state()].run()
            pygame.display.update()
            self.clock.tick(self.FPS)
            # fps = self.clock.get_fps()
            # print(f'FPS: {fps:.2f}')

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()