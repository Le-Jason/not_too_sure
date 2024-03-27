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
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.scale = self.HEIGHT / 160000

        self.h_width = self.WIDTH // 2
        self.h_height = self.HEIGHT // 2
        self.max_width = 160000
        self.max_height = 160000
        self.TIME_STEP = 10*24
        self.MET_TIME = 0

        self.start_time = pygame.time.get_ticks()

        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.level = Level(self.screen, self.gameStateManager, self.screen, self.WIDTH, self.HEIGHT, self.max_width, self.max_height,
                        self.MET_TIME, self.TIME_STEP, self.start_time)

        self.states = {'start': self.start, 'level': self.level}

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
            #     if event.type == pygame.KEYDOWN: 
            #         if event.key == pygame.K_SPACE:
            #             boosting = True
            #         if event.key == pygame.K_RIGHT:
            #             righting = True
            #         if event.key == pygame.K_LEFT:
            #             lefting = True
            #     elif event.type == pygame.KEYUP:
            #         if event.key == pygame.K_SPACE: 
            #             boosting = False
            #         if event.key == pygame.K_RIGHT:
            #             righting = False
            #         if event.key == pygame.K_LEFT:
            #             lefting = False
            # if boosting:
            #     rocket.rocket_fire()
            # if righting:
            #     rocket.rocket_rotate(1)
            # if lefting:
            #     rocket.rocket_rotate(0)

            # rocket_state = planet.rk4(0, [rocket.x, rocket.y, 0.0, rocket.vx, rocket.vy, 0.0], self.TIME_STEP, planet.two_body_ode)
            # rocket.update_image(rocket_state)
            # planet.update_image(self.MET_TIME)
            # rocket.update_kep_state(planet.mu)

            # # Update timer with elapsed time
            # elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
            # if (elapsed_seconds % 1) <= 0.016:
            #     rocket.orbit_traj = planet.propagate_body(
            #         0,
            #         [rocket.x, rocket.y, 0.0, rocket.vx, rocket.vy, 0.0],
            #         100*24,
            #         planet.two_body_ode,
            #         rocket.period)

            # camera_group.update()
            # camera_group.custom_draw()
            
            # self.screen.blit(planet.display_image, planet.rect)
            # self.screen.blit(rocket.display_image, rocket.rect)
            # for pos in rocket.orbit_traj:
            #     const_win_x = self.WIDTH // 2
            #     const_win_y = self.HEIGHT // 2
            #     win_scale_x = self.WIDTH/(2*self.max_width)
            #     win_scale_y = -1*self.HEIGHT/(2*self.max_height)
            #     x_centered = (pos[0] * win_scale_x) + const_win_x
            #     y_centered = (pos[1] * win_scale_y) + const_win_y
            #     pygame.draw.circle(self.screen, (255, 255, 255), (x_centered, y_centered), 1)


            # y_pos = 0
            # for line in rocket.orbit_parameters_text:
            #     text = rocket.font.render(line, False, 'Blue')
            #     self.screen.blit(text, (400, y_pos))
            #     y_pos += text.get_height()

            # pygame.display.update()
            # self.clock.tick(self.FPS)
            # self.MET_TIME += self.TIME_STEP

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()