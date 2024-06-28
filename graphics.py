from enum import Enum
import numpy as np
import pygame

# Define an enumeration
class FrameMode(Enum):
    FREE = 0
    LOCK_ROCKET = 1

class Graphics:
    def __init__(self, display_screen, system_info):
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel = system_info['length_per_pixel']

        # Init Frame on the surface of Earth
        earth_radius = 6378.1363 # TODO: Change to something better
        y_min = earth_radius
        y_max = (self.HEIGHT*self.length_per_pixel) + y_min
        x_min = -((self.WIDTH/2)*self.length_per_pixel)
        x_max = ((self.WIDTH/2)*self.length_per_pixel)
        self.sim_frame_dim = [
            y_min, 
            y_max, 
            x_min, 
            x_max
        ]

        self.frame_mode = FrameMode.LOCK_ROCKET
        self.selected_rocket = None

        self.frame_mode_func = {
            FrameMode.FREE: self.lock_frame_to_rocket(self.selected_rocket), # TODO: Update this
            FrameMode.LOCK_ROCKET: self.lock_frame_to_rocket(self.selected_rocket),
        }

    def lock_frame_to_rocket(self, selected_rocket):
        if selected_rocket == None:
            return
        x = selected_rocket.state[0]
        y = selected_rocket.state[1]
        y_min = self.sim_frame_dim[0]
        y_max = self.sim_frame_dim[1]
        x_min = self.sim_frame_dim[2]
        x_max = self.sim_frame_dim[3]
        height_half = abs(y_max - y_min)/2
        width_half = abs(x_max - x_min)/2

        y_max = y + height_half
        y_min = y - height_half

        x_min = x - width_half
        x_max = x + width_half

        self.sim_frame_dim = [y_min, y_max, x_min, x_max]

    def map_rocket_to_screen(self, rocket):
        y_max = self.sim_frame_dim[1]
        x_min = self.sim_frame_dim[2]

        center_of_mass = ((rocket.state[0] - x_min) / self.length_per_pixel, (y_max - rocket.state[1]) / self.length_per_pixel)
        origin_x = rocket.struct_frame.origin[0]*np.cos(np.deg2rad(rocket.struct_frame.rotation)) - rocket.struct_frame.origin[1]*np.sin(np.deg2rad(rocket.struct_frame.rotation))
        origin_y = rocket.struct_frame.origin[0]*np.sin(np.deg2rad(rocket.struct_frame.rotation)) + rocket.struct_frame.origin[1]*np.cos(np.deg2rad(rocket.struct_frame.rotation))
        origin_ = (center_of_mass[0] + origin_x, center_of_mass[1] + origin_y)

        for part in rocket.struct_frame.parts:
            center_x = part.relative_struct_real[0]*np.cos(np.deg2rad(rocket.struct_frame.rotation)) - part.relative_struct_real[1]*np.sin(np.deg2rad(rocket.struct_frame.rotation))
            center_y = part.relative_struct_real[0]*np.sin(np.deg2rad(rocket.struct_frame.rotation)) + part.relative_struct_real[1]*np.cos(np.deg2rad(rocket.struct_frame.rotation))
            part.rect.center = (origin_[0] + center_x, origin_[1] + center_y)
            display_image = pygame.transform.rotate(part.image, -1*rocket.struct_frame.rotation)
            display_rec = display_image.get_rect(center=part.rect.center)
            self.display_screen.blit(display_image, display_rec)

        pygame.draw.circle(self.display_screen, (255, 0, 0), center_of_mass, 1)
        pygame.draw.circle(self.display_screen, (0, 255, 0), origin_, 1)

    def map_object_to_screen(self, object):
        y_max = self.sim_frame_dim[1]
        x_min = self.sim_frame_dim[2]

        center_of_mass = ((object.state[0] - x_min) / self.length_per_pixel, (y_max - object.state[1]) / self.length_per_pixel)

        display_image_length = (object.rect[2], object.rect[3])

        if object.location_init == 'top':
            if object.display_mode == 'LOCKED_Y':
                if ((center_of_mass[1] + display_image_length[1]) < 0) or (center_of_mass[1] > self.HEIGHT):
                    return
                object.rect.midtop = (self.WIDTH/2, center_of_mass[1])
            elif object.display_mode == 'LOCKED_X':
                if ((center_of_mass[0] + (display_image_length[0]/2)) < 0) or ((center_of_mass[0] - (display_image_length[0]/2)) > self.WIDTH):
                    return
                object.rect.midtop = (center_of_mass[0], self.HEIGHT/2)
            else:
                if ((center_of_mass[1] + display_image_length[1]) < 0) or (center_of_mass[1] > self.HEIGHT) or ((center_of_mass[0] + (display_image_length[0]/2)) < 0) or ((center_of_mass[0] - (display_image_length[0]/2)) > self.WIDTH):
                    return
                object.rect.midtop = (center_of_mass[0], center_of_mass[1])
        else:
            if ((center_of_mass[1] + display_image_length[1]/2) < 0) or (center_of_mass[1] - display_image_length[1]/2 > self.HEIGHT) or ((center_of_mass[0] + (display_image_length[0]/2)) < 0) or ((center_of_mass[0] - (display_image_length[0]/2)) > self.WIDTH): 
                return
            object.rect.center = (center_of_mass[0], center_of_mass[1])
        self.display_screen.blit(object.image, object.rect)

    def update(self, rocket):
        self.selected_rocket = rocket

        if self.frame_mode == FrameMode.LOCK_ROCKET:
            self.lock_frame_to_rocket(self.selected_rocket)
