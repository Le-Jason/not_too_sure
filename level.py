from planet import *
from camera import *
from rocket import *
from level import *
from ui_button import *
from dynamics import *
from graphics import *
from ui import *
import pygame
from sys import exit

class Background_Objects(pygame.sprite.Sprite):
    def __init__(self, image, state, display_mode='EXACT', location_init='center'):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.state = state
        self.location_init = location_init
        self.display_mode = display_mode

class Level:
    def __init__(self, display, gameStateManager, display_surface, system_info, start_time,
                VAB_object):
        # Displays and Game Manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.display_surface = display_surface

        # Create Dynamics Class
        self.dynamics = Dynamics()
        self.graphics = Graphics(display_surface, system_info)

        # Create UI Class
        self.ui = RocketUI(display_surface, system_info)

        # Create Level Sprites
        pygame.display.set_caption('Gound Level')
        self.sky = pygame.image.load('graphics/spites/sky.png').convert_alpha()
        self.sky_rec = self.sky.get_rect(topleft=(0, 0))
        self.vab = Background_Objects('graphics/spites/launch_pad_2.png', [0, 6385.2, 0 , 0, 0, 0])
        self.gnd = Background_Objects('graphics/ground.png', [0, 6378.1363, 0 , 0, 0, 0], 'LOCKED_Y', location_init='top')
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
        self.scroll = 0
        self.tiles = m.ceil(self.WIDTH / self.sky.get_width()) + 1
        # self.tiles_gnd = m.ceil(self.WIDTH / self.gnd_pic.get_width()) + 1

    def run(self):
        if self.init == False:
            self.init = True
            self.rocket = Rocket(self.VAB_object.rocket, self.length_per_pixel)

        if self.init == True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.rocket.rocket_fire()
            if keys[pygame.K_RIGHT]:
                self.rocket.rocket_rotate(True)
            if keys[pygame.K_LEFT]:
                self.rocket.rocket_rotate(False)

            # Update Models
            self.rocket.update()
            self.dynamics.update()
            self.dynamics.update_rocket(self.rocket, self.object_group)

            # Update Background
            for i in range(0, self.tiles):
                self.sky_rec = ((i * self.sky.get_width()) + self.scroll, 0)
                self.display_surface.blit(self.sky, self.sky_rec)
            self.scroll -= 5
            
            if abs(self.scroll) > self.sky.get_width():
                self.scroll = 0
            self.display_surface.blit(self.sky, self.sky_rec)

            # Update Rockets and Objects
            self.graphics.update(self.rocket)
            self.graphics.map_object_to_screen(self.gnd)
            self.graphics.map_object_to_screen(self.vab)
            self.graphics.map_rocket_to_screen(self.rocket)
            self.ui.update(self.rocket)

            
    def get_visible_rect(self, image):
        rect = image.get_rect()
        mask = pygame.mask.from_surface(image)
        non_transparent_pixels = mask.outline()

        # Find the minimum bounding box of the non-transparent pixels
        min_x = min(pixel[0] for pixel in non_transparent_pixels)
        max_x = max(pixel[0] for pixel in non_transparent_pixels)
        min_y = min(pixel[1] for pixel in non_transparent_pixels)
        max_y = max(pixel[1] for pixel in non_transparent_pixels)
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Adjust the position of the rectangle to match the sprite's position
        x, y = rect.topleft
        return pygame.Rect(x + min_x, y + min_y, width, height)

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