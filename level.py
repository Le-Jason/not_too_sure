from planet import *
from camera import *
from rocket import *
from level import *
from ui_button import *
from dynamics import *
from graphics import *
from object import *
from ui import *
import pygame
from sys import exit

class Level:
    def __init__(self, display, gameStateManager, display_surface, system_info, start_time,
                VAB_object):
        # Displays and Game Manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.display_surface = display_surface
        self.level = 'rocket' # Level start view

        # Create Manager Classes
        self.dynamics = Dynamics()
        self.graphics = Graphics(display_surface, system_info, self.dynamics.env.sky_color, self.dynamics.env.radius)
        self.ui = RocketUI(display_surface, system_info)

        # Create Level Sprites
        pygame.display.set_caption('Gound Level')
        self.earth = Background_Objects('graphics/ui/earth.png', [0, 0, 0 , 0, 0, 0], system_info['length_per_pixel'], size=6378136.3*2)
        self.vab = Background_Objects('graphics/spites/launch_pad_2.png', [0, 6378143.3, 0 , 0, 0, 0], system_info['length_per_pixel'])
        self.gnd = Background_Objects('graphics/ground.png', [0, 6378136.3, 0 , 0, 0, 0], system_info['length_per_pixel'], location_init='top')
        self.object_group = pygame.sprite.Group()
        self.object_group.add(self.gnd)
        self.object_group.add(self.vab)

        # System Level
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.TIME_STEP = system_info['TIME_STEP']
        self.length_per_pixel = system_info['length_per_pixel']
        self.start_time = start_time

        self.VAB_object = VAB_object
        self.init = False

        # Used for key press debounce
        self.debounce_threshold = 500 # Wait for 500 ticks 
        self.last_update_time = 0     # Counter for last updated time

        # Used for scaling
        self.scale = 1.0
        self.scale_increment = 0.01

    def run(self):
        # Wait til the VAB level get a working rocket
        if self.init == False:
            self.init = True
            self.rocket = Rocket(self.VAB_object.rocket, self.length_per_pixel)

        # Start level
        if self.init == True:
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()
            # Fire the current rocket engines
            if keys[pygame.K_SPACE]:
                self.rocket.rocket_fire()
            # Rotate the rocket clockwise
            if keys[pygame.K_RIGHT]:
                self.rocket.rocket_rotate(True)
            # Rotate the rocket counter-clockwise
            if keys[pygame.K_LEFT]:
                self.rocket.rocket_rotate(False)
            # Scale the level up
            if keys[pygame.K_UP]:
                self.scale += self.scale_increment
            # Scale the level down
            if keys[pygame.K_DOWN]:
                self.scale -= self.scale_increment
            # Switch the level views
            if keys[pygame.K_m]:
                if current_time - self.last_update_time > self.debounce_threshold:
                    if self.level == 'rocket':
                        self.level = 'map'
                    else:
                        self.level = 'rocket'
                    self.last_update_time = current_time

            # Update Models
            self.dynamics.update(self.rocket)

            # Update Graphics
            self.gnd.update_state(self.rocket)
            self.graphics.update(self.rocket, self.dynamics.env)
            self.graphics.map_object_to_screen(self.gnd, 'rocket_view')
            self.graphics.map_object_to_screen(self.vab, 'rocket_view')
            self.graphics.map_rocket_to_screen(self.rocket, 'rocket_view')
            if self.level == 'rocket':
                self.ui.update(self.rocket, self.dynamics.env)
            if self.level == 'map':
                self.graphics.update_map(self.rocket, self.dynamics.env.mu)
                # self.earth.scaled_image(self.scale)
                self.graphics.scaled_map(self.scale, 'map_view')
                self.graphics.map_object_to_screen(self.earth, 'map_view')
                self.ui.update(self.rocket, self.dynamics.env)

            # # Update Models
            self.dynamics.update_rocket(self.rocket, self.object_group)
            self.rocket.update(self.dynamics.env.mu)

class VAB:
    def __init__(self, display, gameStateManager, length_per_pixel):
        # Set variables for each level
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.length_per_pixel = length_per_pixel
        pygame.display.set_caption('VAB')

        # Set Background
        self.sky = pygame.image.load('graphics/spites/sky.png').convert_alpha()
        self.sky_rec = self.sky.get_rect(topleft=(0, 0))
        self.vab_pic = pygame.image.load('graphics/spites/launch_pad.png').convert_alpha()
        self.vab_pic_rec = self.vab_pic.get_rect(topleft=(0, 0))
        self.ui = pygame.image.load('graphics/spites/vab_ui.png').convert_alpha()
        self.ui_rec = self.ui.get_rect(topleft=(0, 0))

        # Set overview buttons
        self.buttons = vab_ui_button()
        self.buttons.add('Command Pod', (0, 55), (55, 42))
        self.buttons.add('Fuel Tank',(0, 55 + 48), (55, 42))
        self.buttons.add('Rocket Engine',(0, 55 + (2*48) + 1), (55, 42))
        self.buttons.add('Controls',(0, 55 + (3*48) + 2), (55, 42))
        self.buttons.add('Structures',(0, 55 + (4*48) + 3), (55, 42))
        self.buttons.add('Aero-Structures',(0, 55 + (5*48) + 4), (55, 42))
        self.buttons.add('Miscellaneous',(0, 55 + (6*48) + 5), (55, 42))
        self.buttons.add('Payload',(0, 55 + (7*48) + 6), (55, 42))
        self.buttons.add('ui1',(294, 0), (43, 63))
        self.buttons.add('ui2',(294 + (49), 0), (43, 63))
        self.buttons.add('Astronaut',(294 + (2*49), 0), (43, 63))
        self.buttons.add('Flag',(843, 0), (43, 63))
        self.buttons.add('New',(1002, 0), (43, 63))
        self.buttons.add('Folder',(1002 + (49), 0), (43, 63))
        self.buttons.add('Save',(1002 + (2*49), 0), (43, 63))
        self.buttons.add('Launch',(1169, 0), (43, 63))
        self.buttons.add('Leave',(1169 + 61, 0), (43, 63))

        self.rocket = None
        self.current_menu = 'NA'

    def run(self):
        self.display_surface.blit(self.sky, self.sky_rec)
        self.display_surface.blit(self.vab_pic, self.vab_pic_rec)

        self.buttons.draw(self.display_surface)

        mouse_pos = pygame.mouse.get_pos()
        self.current_menu, rocket_launch = self.buttons.click(mouse_pos, self.display_surface, self.current_menu)

        if self.current_menu == 'Launch':
            self.rocket = rocket_launch
            self.gameStateManager.set_state('level')

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