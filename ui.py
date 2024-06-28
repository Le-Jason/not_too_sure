import pygame
import math as m

class Num_Setup():
    def __init__(self, num, loc, dis):
        # num = number of sprites
        # loc = starting location
        # dis = distance between numbers
        self.num = num
        self.numbers = pygame.sprite.Group()
        for N in range(num):
            self.numbers.add(UI_Objects('graphics/ui/0.png', loc_param="midtop", loc_dis=(loc[0] + (N*dis), loc[1])))
        self.units= UI_Objects('graphics/ui/m.png', loc_param="midtop", loc_dis=(loc[0] + (num*dis), loc[1]))

    def update_numbers(self, altitude):
        # Convert altitude to a string to iterate over its digits
        limit = int('9' * self.num)
        if altitude > limit:
            self.units.update_image('graphics/ui/K.png')
            altitude = m.floor(altitude / 1000)
        else:
            self.units.update_image('graphics/ui/m.png')
        altitude_str = str(altitude)
        self.display_num = [0] * self.num
        digits = [int(char) for char in altitude_str]
        start_index = self.num - len(digits)
        for i in range(start_index, self.num):
            self.display_num[i] = digits[i - start_index]
        
        # Dictionary mapping digits to image paths
        image_paths = {
            0: 'graphics/ui/0.png',
            1: 'graphics/ui/1.png',
            2: 'graphics/ui/2.png',
            3: 'graphics/ui/3.png',
            4: 'graphics/ui/4.png',
            5: 'graphics/ui/5.png',
            6: 'graphics/ui/6.png',
            7: 'graphics/ui/7.png',
            8: 'graphics/ui/8.png',
            9: 'graphics/ui/9.png'
        }
        
        # Update images based on display_num
        for idx, num in enumerate(self.numbers):
            if idx < len(self.display_num):
                num.update_image(image_paths[self.display_num[idx]])
            else:
                # Handle case where idx is out of bounds of display_num (though ideally should not happen)
                num.update_image('graphics/ui/0.png')  # Default image or handle appropriately

    def update(self, display_screen):
        self.numbers.draw(display_screen)
        display_screen.blit(self.units.image, self.units.rect)

class UI_Objects(pygame.sprite.Sprite):
    def __init__(self, image, loc_param="center", loc_dis=(0,0)):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        if loc_param == "midtop":
            self.rect = self.image.get_rect(midtop=loc_dis)
        elif loc_param == "center":
            self.rect = self.image.get_rect(center=loc_dis)

    def update_image(self, new_image):
        self.image = pygame.image.load(new_image).convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)

class RocketUI():
    def __init__(self, display_screen, system_info):
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel = system_info['length_per_pixel']

        self.sprite = pygame.sprite.Group()
        self.altitude_bg = UI_Objects('graphics/ui/altitude_bg.png', loc_param="midtop", loc_dis=(self.WIDTH/2, 0))
        self.altitude_num = Num_Setup(6, (528, 8), 32)

    def update(self, rocket):
        self.display_screen.blit(self.altitude_bg.image, self.altitude_bg.rect)
        self.altitude_num.update(self.display_screen)
        self.altitude_num.update_numbers(m.floor(rocket.state[1]-6378.1363))