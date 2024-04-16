from planet import *
from camera import *
from rocket import *
from level import *
from ui_button import *
import pygame
from sys import exit

class Level:
    def __init__(self, display, gameStateManager, screen, WIDTH, HEIGHT, max_width, max_height, MET_TIME, TIME_STEP, start_time):
        self.display = display
        self.gameStateManager = gameStateManager

        self.screen = screen
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.max_width = max_width
        self.max_height = max_height
        self.MET_TIME = MET_TIME
        self.TIME_STEP = TIME_STEP
        self.start_time = start_time

        self.camera_group = CameraGroup()
        self.planet = Planet((self.WIDTH, self.HEIGHT, self.max_width, self.max_height),
                        self.camera_group)
        self.rocket = Rocket((160000.0, 0.0),
                        (0.0, 1.4),
                        (self.WIDTH, self.HEIGHT, self.max_width, self.max_height),
                        self.camera_group)

        self.boosting = False
        self.lefting = False
        self.righting = False
        self.timer = 0

    def run(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.rocket.rocket_fire()
        if keys[pygame.K_RIGHT]:
            self.rocket.rocket_rotate(1)
        if keys[pygame.K_LEFT]:
            self.rocket.rocket_rotate(0)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.boosting = True
                if event.key == pygame.K_RIGHT:
                    self.righting = True
                if event.key == pygame.K_LEFT:
                    self.lefting = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE: 
                    self.boosting = False
                if event.key == pygame.K_RIGHT:
                    self.righting = False
                if event.key == pygame.K_LEFT:
                    self.lefting = False
        if self.boosting:
            self.rocket.rocket_fire()
        if self.righting:
            self.rocket.rocket_rotate(1)
        if self.lefting:
            self.rocket.rocket_rotate(0)
        rocket_state = self.planet.rk4(0, [self.rocket.x, self.rocket.y, 0.0, self.rocket.vx, self.rocket.vy, 0.0], self.TIME_STEP, self.planet.two_body_ode)
        self.rocket.update_image(rocket_state)
        self.planet.update_image(self.MET_TIME)
        self.rocket.update_kep_state(self.planet.mu)
        # Update timer with elapsed time
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000
        if (elapsed_seconds % 1) <= 0.016:
            self.rocket.orbit_traj = self.planet.propagate_body(
                0,
                [self.rocket.x, self.rocket.y, 0.0, self.rocket.vx, self.rocket.vy, 0.0],
                100*24,
                self.planet.two_body_ode,
                self.rocket.period)

        self.camera_group.update()
        self.camera_group.custom_draw()
        
        self.screen.blit(self.planet.display_image, self.planet.rect)
        self.screen.blit(self.rocket.display_image, self.rocket.rect)
        for pos in self.rocket.orbit_traj:
            const_win_x = self.WIDTH // 2
            const_win_y = self.HEIGHT // 2
            win_scale_x = self.WIDTH/(2*self.max_width)
            win_scale_y = -1*self.HEIGHT/(2*self.max_height)
            x_centered = (pos[0] * win_scale_x) + const_win_x
            y_centered = (pos[1] * win_scale_y) + const_win_y
            pygame.draw.circle(self.screen, (255, 255, 255), (x_centered, y_centered), 1)


        y_pos = 0
        for line in self.rocket.orbit_parameters_text:
            text = self.rocket.font.render(line, False, 'Blue')
            self.screen.blit(text, (400, y_pos))
            y_pos += text.get_height()

        self.MET_TIME += self.TIME_STEP

class VAB:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.display_surface = pygame.display.get_surface()

        pygame.display.set_caption('VAB')
        self.sky = pygame.image.load('graphics/spites/sky.png').convert_alpha()
        self.sky_rec = self.sky.get_rect(topleft=(0, 0))

        self.vab_pic = pygame.image.load('graphics/spites/launch_pad.png').convert_alpha()
        self.vab_pic_rec = self.vab_pic.get_rect(topleft=(0, 0))

        self.ui = pygame.image.load('graphics/spites/vab_ui.png').convert_alpha()
        self.ui_rec = self.ui.get_rect(topleft=(0, 0))

        self.current_menu = 'NA'

        self.buttons = [
            vab_ui_button('Command Pod', (0, 55), (55, 42)),
            vab_ui_button('Fuel Tank',(0, 55 + 48), (55, 42)),
            vab_ui_button('Rocket Engine',(0, 55 + (2*48) + 1), (55, 42)),
            vab_ui_button('Controls',(0, 55 + (3*48) + 2), (55, 42)),
            vab_ui_button('Structures',(0, 55 + (4*48) + 3), (55, 42)),
            vab_ui_button('Aero-Structures',(0, 55 + (5*48) + 4), (55, 42)),
            vab_ui_button('Miscellaneous',(0, 55 + (6*48) + 5), (55, 42)),
            vab_ui_button('Payload',(0, 55 + (7*48) + 6), (55, 42)),

            vab_ui_button('ui1',(294, 0), (43, 63)),
            vab_ui_button('ui2',(294 + (49), 0), (43, 63)),
            vab_ui_button('Astronaut',(294 + (2*49), 0), (43, 63)),
            vab_ui_button('Flag',(843, 0), (43, 63)),
            vab_ui_button('New',(1002, 0), (43, 63)),
            vab_ui_button('Folder',(1002 + (49), 0), (43, 63)),
            vab_ui_button('Save',(1002 + (2*49), 0), (43, 63)),
            vab_ui_button('Launch',(1169, 0), (43, 63)),
            vab_ui_button('Leave',(1169 + 61, 0), (43, 63)),
        ]

    def run(self):
        self.display_surface.blit(self.sky, self.sky_rec)
        self.display_surface.blit(self.vab_pic, self.vab_pic_rec)

        for button in self.buttons:
            self.display_surface.blit(button.rec, button.rec_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            self.current_menu = button.click(mouse_pos, self.display_surface, self.current_menu)

        self.display_surface.blit(self.ui, self.ui_rec)


class Start:
    def __init__(self, display,gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        pygame.display.set_caption('Main Menu')
        self.display_surface = pygame.display.get_surface()
        self.background = pygame.image.load('graphics/start_menu.png').convert_alpha()
        self.background_rec = self.background.get_rect(topleft = (0,0))

        self.title = pygame.image.load('graphics/title.png').convert_alpha()
        self.title_rec = self.title.get_rect(topleft = (-100,-100))

        self.font = pygame.font.Font('font/Pixeltype.ttf', 100)
        start_text = "Start Game"
        setting_text = "Settings"
        quit_text = "Quit"
        self.font_surface = self.font.render(start_text, False, 'Blue')
        self.text_rect = self.font_surface.get_rect(topleft = (500, 350))
        self.font_surface_2 = self.font.render(setting_text, False, 'Blue')
        self.text_rect_2 = self.font_surface_2.get_rect(topleft = (545, 450))
        self.font_surface_3 = self.font.render(quit_text, False, 'Blue')
        self.text_rect_3 = self.font_surface_3.get_rect(topleft = (600, 550))
        

    def run(self):
        self.display_surface.blit(self.background, self.background_rec)
        self.display_surface.blit(self.title, self.title_rec)
        self.display_surface.blit(self.font_surface, self.text_rect)
        self.display_surface.blit(self.font_surface_2, self.text_rect_2)
        self.display_surface.blit(self.font_surface_3, self.text_rect_3)

        mouse_pos = pygame.mouse.get_pos()
        if self.text_rect.collidepoint(mouse_pos):
            if (pygame.mouse.get_pressed()[0]):
                self.gameStateManager.set_state('VAB')
        if self.text_rect_2.collidepoint(mouse_pos):
            print(pygame.mouse.get_pressed()[0])

        if self.text_rect_3.collidepoint(mouse_pos):
            if (pygame.mouse.get_pressed()[0]):
                pygame.quit()
                exit()

class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState
    
    def set_state(self, state):
        self.currentState = state