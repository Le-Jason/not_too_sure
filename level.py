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
        self.dynamics = Dynamics(system_info)
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

            # pygame.draw.circle(self.display_surface, (255, 0, 0), self.dynamics.overlap, 1)
            # pygame.draw.circle(self.display_surface, (255, 0, 0), self.dynamics.part_overlap, 1)

            # # Update Models
            self.dynamics.update_rocket(self.rocket, self.object_group, self.graphics.screen_frame_dim)
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
    def __init__(self, display,gameStateManager, system_info):
        self.display = display
        self.gameStateManager = gameStateManager
        self.system_info = system_info

        pygame.display.set_caption('Main Menu')
        self.display_surface = pygame.display.get_surface()

        self.title_text = NoSurroundingButton('Space Simulator', 'font/Pixeltype.ttf', 200)
        self.title_text.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.25)
        self.title_text.set_color('#b5cfff')

        self.earth_bg = Main_Menu_Objects('graphics/title_earth.png')
        self.earth_bg.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 1.3)
        self.earth_bg.set_rotation(0.05)

        self.space_bg = Main_Menu_Objects('graphics/space_background.png')
        self.space_bg.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT']/2)

        self.start_button = NoSurroundingButton('Start Game', 'font/Pixeltype.ttf', 100)
        self.start_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.45)
        
        self.settings_button = NoSurroundingButton('Settings', 'font/Pixeltype.ttf', 100)
        self.settings_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.60)

        self.quit_button = NoSurroundingButton('Quit', 'font/Pixeltype.ttf', 100)
        self.quit_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.75)

        self.penguin = Main_Menu_Sprite('graphics/penguin_suit.png')
        self.penguin.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT']/2)
        self.penguin.set_rotation(0.03)

    def run(self):
        self.earth_bg.update()
        self.penguin.update()

        self.display_surface.blit(self.space_bg.image, self.space_bg.rect)
        self.display_surface.blit(self.earth_bg.image, self.earth_bg.rect)
        self.display_surface.blit(self.penguin.image, self.penguin.rect)

        self.start_button.update(pygame.mouse.get_pos(), actions=[self.switch_levels])
        self.settings_button.update(pygame.mouse.get_pos())
        self.quit_button.update(pygame.mouse.get_pos(), actions=[self.quit_game])

        self.display_surface.blit(self.title_text.font_surface, self.title_text.font_rect)
        self.display_surface.blit(self.start_button.font_surface, self.start_button.font_rect)
        self.display_surface.blit(self.settings_button.font_surface, self.settings_button.font_rect)
        self.display_surface.blit(self.quit_button.font_surface, self.quit_button.font_rect)

    
    def quit_game(self):
        pygame.quit()
        exit()

    def switch_levels(self):
        self.gameStateManager.set_state('VAB')

class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState
    
    def set_state(self, state):
        self.currentState = state