import pygame
import math as m
import numpy as np

class OrbitManager():
    """
    Class to manage the orbit related items

    Augments:
        display_screen (object): screen display object
        system_info (dict): key info about the game screen
        text_font_obj (text object): object for text font

    Notes:

    """
    def __init__(self, display_screen, system_info, text_font_obj):
        # Assign class members
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel = system_info['length_per_pixel']
        self.text_font_obj = text_font_obj

        # Create objects used for this display
        self.orbit_display_background = UI_Objects('graphics/ui/veh_info.png', placement="bottomleft", screen_coord_location=(0, self.HEIGHT))

    def draw_text(self, text, font, col, x, y):
        """ Draw the text

        Augments:
            text (string): Message that you want to display
            font (text object): Font that you want the message to be in
            col (array of three): RGB values
            x (int): X Screen Coordinate that the message will be at
            y (int): Y Screen Coordinate that the message will be at
        """
        img = font.render(text, True, col)
        text_rect = img.get_rect()
        text_rect.topright = (x, y)
        self.display_screen.blit(img, text_rect)

    def update(self, rocket, environment_manager):
        """ Update the manager

        Returns:
            rocket (object): Display rocket stats
            environment_manager (manager): Get the radius of the current planet
        """
        # Draw the orbit display background and info
        self.display_screen.blit(self.orbit_display_background.image, self.orbit_display_background.rect)

        # Draw the rocket's apoapsis and periapsis 
        self.draw_text(f"{((rocket.periapsis-environment_manager.radius)/1000):.4f}km", self.text_font_obj, (106, 190, 48), 194, self.HEIGHT - 64)
        self.draw_text(f"{((rocket.apoapsis-environment_manager.radius)/1000):.4f}km", self.text_font_obj, (106, 190, 48), 94, self.HEIGHT - 64)

        # Draw the rocket's time of flight to apoapsis and periapsis
        [time_to_periapsis_hour, time_to_periapsis_minutes, time_to_periapsis_seconds] = self.convert_seconds_to_hhmmss(rocket.periapsis_tof)
        [time_to_apoapsis_hour, time_to_apoapsis_minutes, time_to_apoapsis_seconds] = self.convert_seconds_to_hhmmss(rocket.apoapsis_tof)
        if np.isnan(rocket.periapsis_tof):
            self.draw_text(f"T-{0}h,{0}m,{0}s", self.text_font_obj, (106, 190, 48), 194, self.HEIGHT - 42)
        else:
            self.draw_text(f"T-{int(time_to_periapsis_hour)}h,{int(time_to_periapsis_minutes)}m,{int(time_to_periapsis_seconds)}s", self.text_font_obj, (106, 190, 48), 194, self.HEIGHT - 42)
        if np.isnan(rocket.apoapsis_tof):
            self.draw_text(f"T-{0}h,{0}m,{0}s", self.text_font_obj, (106, 190, 48), 94, self.HEIGHT - 42)
        else:
            self.draw_text(f"T-{int(time_to_apoapsis_hour)}h,{int(time_to_apoapsis_minutes)}m,{int(time_to_apoapsis_seconds)}s", self.text_font_obj, (106, 190, 48), 94, self.HEIGHT - 42)

    def convert_seconds_to_hhmmss(self, seconds):
        """ Convert seconds to HH:MM:SS

        Returns:
            seconds (double): seconds that you want to convert
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return hours, minutes, remaining_seconds


class AltimeterManager():
    """
    Class to manage the altimeter related items

    Augments:
        display_screen (object): screen display object
        system_info (dict): key info about the game screen

    Notes:

    """
    def __init__(self, display_screen, system_info):
        # Assign class members
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel = system_info['length_per_pixel']

        # Create objects used for the altimeter
        self.background = UI_Objects('graphics/ui/altitude_bg.png', placement="midtop", screen_coord_location=(self.WIDTH/2, 0))
        self.altitude_num = AltimeterNumManager(6, (528, 8), 32)
        self.atmosphere_arrow = UI_Objects('graphics/ui/arrow.png', placement="midtop", screen_coord_location=(531, 65), screen_extrema=(531.0, 726.0))

    def update(self, rocket, environment_manager):
        """ Update the manager

        Augments:
            rocket (Object): Determine the altitude of the rocket
            environment_manager (Manager): Determine the density of the current altitude
        
        """
        # Draw Background
        self.display_screen.blit(self.background.image, self.background.rect)

        # Determine the altitude and draw the numbers
        rocket_position = rocket.state[:3]
        rocket_position_unit_vector = np.array(rocket_position) / np.linalg.norm(rocket_position)
        # TODO: This is fine for sea level but needs to be updated for surface altitude
        center_planet_to_rocket_pos_mag = m.sqrt((rocket.state[0] - (environment_manager.radius*rocket_position_unit_vector[0]))**2 + 
                                                (rocket.state[1] - (environment_manager.radius*rocket_position_unit_vector[1]))**2 + 
                                                (rocket.state[2] - (environment_manager.radius*rocket_position_unit_vector[2]))**2)
        self.altitude_num.update_numbers(m.floor(center_planet_to_rocket_pos_mag))
        self.altitude_num.update(self.display_screen)

        # Update and Draw the atmospheric density meter
        self.atmosphere_arrow.update_pos_within_extrema(environment_manager.rho, environment_manager.rho_limits)
        self.display_screen.blit(self.atmosphere_arrow.image, self.atmosphere_arrow.rect)

class AltimeterNumManager():
    """
    Class to manage the numbering system for the ui altimeter

    Augments:
        num_of_digits (int): Number of digit the altimeter can handle
        screen_coord_location (array of 2): Location of the top-mid point of a image (screen coordinates)
        distance_between_num (int): Distance between different sprites [pixels]

    Returns:
        The current height between the planet surface and the current rocket on the altimeter

    Notes:
        Assumes numbers will be horizontal from each other

    TODO:
        Manage between sea level height and surface height

    """
    def __init__(self, num_of_digits, screen_coord_location, distance_between_num):
        # Assign class memebers
        self.num_of_digits = num_of_digits
        self.display_num = [0] * self.num_of_digits
        # Dictionary mapping digits to image paths
        self.image_paths = {
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

        # Create Number Sprite Group for altimeter
        self.num_group = pygame.sprite.Group()
        for N in range(num_of_digits):
            self.num_group.add(UI_Objects('graphics/ui/0.png', 
                                        placement="midtop", 
                                        screen_coord_location=(screen_coord_location[0] + (N*distance_between_num), 
                                        screen_coord_location[1])))
        
        # Create Units Sprite for altimeter
        self.units= UI_Objects('graphics/ui/m.png', 
                                placement="midtop", 
                                screen_coord_location=(screen_coord_location[0] + (num_of_digits*distance_between_num), 
                                screen_coord_location[1]))

    def update_numbers(self, altitude):
        """ Update the value of the altimeter

        Args:
            altitude (double): height value
        """
        # Reset the display_num array
        self.display_num = [0] * self.num_of_digits

        # Manage Units for the display[m, km]
        limit = int('9' * self.num_of_digits)
        if altitude > limit:
            self.units.update_image('graphics/ui/K.png')
            altitude = m.floor(altitude / 1000)
        else:
            self.units.update_image('graphics/ui/m.png')

        # Convert altitude to a array of int values
        altitude_str = str(altitude)
        digits = [int(char) for char in altitude_str if char.isdigit()]
        start_index = self.num_of_digits - len(digits)
        for i in range(start_index, self.num_of_digits):
            self.display_num[i] = digits[i - start_index]
        
        # Update num_group based on altitude
        for idx, num in enumerate(self.num_group):
            if idx < len(self.display_num):
                num.update_image(self.image_paths[self.display_num[idx]])
            else:
                # Handle case where idx is out of bounds of display_num (though ideally should not happen)
                num.update_image('graphics/ui/0.png')  # Default image or handle appropriately

    def update(self, display_screen):
        """ Update and draw

        Args:
            display_screen : display object
        """
        self.num_group.draw(display_screen)
        display_screen.blit(self.units.image, self.units.rect)

class UI_Objects(pygame.sprite.Sprite):
    """
    Class to create a sprite object for UI elements

    Augments:
        image (string): location of image
        placement (string): Where of the image to put screen_coord_location to
        screen_coord_location (array of two): Location of the top-mid point of a image (screen coordinates)
        screen_extrema (array of two): the max and min where the object can move to using self.update_pos_within_extrema()

    Returns:
        Create the UI sprite object

    Notes:

    """
    def __init__(self, image, placement="center", screen_coord_location=(0,0), screen_extrema=(0, 100)):
        # Assign basic sprite members
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        if placement == "midtop":
            self.rect = self.image.get_rect(midtop=screen_coord_location)
        elif placement == "center":
            self.rect = self.image.get_rect(center=screen_coord_location)
        elif placement == "bottomleft":
            self.rect = self.image.get_rect(bottomleft=screen_coord_location)

        # Assign UI_Objects members
        self.screen_coord_location = screen_coord_location
        self.screen_extrema = screen_extrema

    def update_image(self, new_image):
        """ Update the class image

        Args:
            new_image (string): Location of new image
        """
        self.image = pygame.image.load(new_image).convert_alpha()
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_pos_within_extrema(self, value, value_extrema):
        """ Update image location with a extrema

        Args:
            value (double): value within the extrema
            value_extrema (array of two): first index is the min and second index is the max of the extrema
        """
        # Safe guard value from being outside the extrema range
        if value > max(value_extrema):
            value_extrema[value_extrema.index(max(value_extrema))] = value
        if value < min(value_extrema):
            value_extrema[value_extrema.index(min(value_extrema))] = value
        
        # Find the pixel amount that each unit "value" has
        pixel_per_param = (self.screen_extrema[1] - self.screen_extrema[0]) / (value_extrema[1] - value_extrema[0])

        # Center the image based on the "value"
        if value_extrema[0] < value_extrema[1]:
            center = (self.screen_coord_location[0] + value * pixel_per_param, self.screen_coord_location[1])
        elif value_extrema[0] >= value_extrema[1]:
            center = (self.screen_coord_location[0] + (value - abs(value_extrema[0] - value_extrema[1])) * pixel_per_param, self.screen_coord_location[1])
        
        # Update rect
        self.rect = self.image.get_rect(center=center)

class RocketUI():
    """ 
    Class that manages the UI

    Augments:
        display_screen (object): screen display object
        system_info (dict): key info about the game screen

    Notes:

    """
    def __init__(self, display_screen, system_info):
        # Assign class members
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel = system_info['length_per_pixel']

        # Text object
        self.text_font_obj = pygame.font.SysFont("Arial", 12)

        # Create Systems used for the UI
        self.altimeter_manager = AltimeterManager(display_screen, system_info)
        self.orbit_manager = OrbitManager(display_screen, system_info, self.text_font_obj)

    def update(self, rocket, environment_manager):
        """ Update all the managers

        Args:
            rocket (object): rocket object
            environment_manager (manager): environment_manager
        """
        # Update the altimeter mangaer
        self.altimeter_manager.update(rocket, environment_manager)

        # Update the orbit display manager
        self.orbit_manager.update(rocket, environment_manager)