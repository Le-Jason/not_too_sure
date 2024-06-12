import pygame
import math as m
import numpy as np

from Algorithms.KeplerProblems import *

class goundRocket():
    def __init__(self, rocket, vab_pic, vab_pic_rec):
        self.length_per_pixel = 1.25 / 53
        self.earth_radius = 6378.1363

        y_min = self.earth_radius
        y_max = (720*self.length_per_pixel) + y_min
        x_min = -((1280/2)*self.length_per_pixel)
        x_max = ((1280/2)*self.length_per_pixel)

        parts = rocket.parts
        body_bottom = 0
        body_top = 0
        body_right = 0
        body_left = 0
        init = False
        idx = 0
        launch_pad = self.get_visible_rect(vab_pic)
        launch_pad_x = vab_pic_rec[2]/2
        launch_pad_y = launch_pad[1]

        # Create rocket frame
        origin_of_struct = (0, 0)

        for part in parts:
            if init == False:
                body_bottom = part.rect.bottom
                body_top = part.rect.top
                body_right = part.rect.right
                body_left = part.rect.left
                body_center = part.rect.center
                init = True
            else:
                if part.rect.bottom > body_bottom:
                    body_bottom = part.rect.bottom
                if part.rect.top < body_top:
                    idx += 1
                    body_top = part.rect.top
                    body_center = part.rect.center
                if part.rect.right > body_right:
                    body_right = part.rect.right
                if part.rect.left < body_left:
                    body_left = part.rect.left

        origin_of_struct = (0, (body_bottom - body_top)*self.length_per_pixel)
        for part in parts:
            relative_center_part_x = part.rect.center[0] - body_center[0]
            relative_center_part_y = part.rect.center[1] - body_top
            part.relative_struct_real = (relative_center_part_x, relative_center_part_y)
        
        cg_x = (rocket.cg_location[0] - body_center[0])*self.length_per_pixel
        cg_y = (rocket.cg_location[1] - body_top)*self.length_per_pixel
        cg_of_struct = (cg_x, cg_y)
        height_init = (body_bottom - body_top)*self.length_per_pixel
        origin_of_struct = (0, height_init + (launch_pad_y*self.length_per_pixel))

        self.cg_location = rocket.cg_location
        for i, part in enumerate(parts):
            if i == idx:
                self.struct_image = pygame.Surface((abs(body_right - body_left) , abs(body_top - body_bottom)))
                self.struct_image.fill((255 , 0 , 0))
                self.struct_rect = self.struct_image.get_rect()
                self.struct_rect.topleft = (part.rect.topleft[0], part.rect.topleft[1])
                self.cg_location_body = (self.cg_location[0] - part.rect.topleft[0], self.cg_location[1] - part.rect.topleft[1])

        for part in parts:
            self.init_relative(part)

        for part in parts:
            part.cg_total_location = (self.cg_location[0] - part.rect.center[0], self.cg_location[1] - part.rect.center[1])

        self.struct_rect.topleft = (launch_pad_x - ((body_right - body_left)/2), launch_pad_y - abs(body_top - body_bottom))
        self.parts = parts
        self.display_parts = parts
        self.angle = 0
        self.rotating = False

        self.moment_of_inertia = rocket.moment_of_inertia
    
    def rocket_rotate(self, motion):
        self.rotating = True
        if motion:
            self.angle += 1
        else:
            self.angle -= 1
        for part in self.parts:
            part.display_image = pygame.transform.rotate(part.image, self.angle)

    def rocket_fire(self):
        center = self.struct_rect.center
        thrust = [0, -1]
        flight_path_angle = m.radians(self.angle % 360)
        dx = -1*(thrust[0] * m.cos(flight_path_angle) - thrust[1] * m.sin(flight_path_angle))
        dy = thrust[0] * m.sin(flight_path_angle) + thrust[1] * m.cos(flight_path_angle)
        self.struct_rect.center = (center[0] + dx*2, center[1] + dy*2)

        center = self.cg_location
        thrust = [0, -1]
        flight_path_angle = m.radians(self.angle % 360)
        dx = -1*(thrust[0] * m.cos(flight_path_angle) - thrust[1] * m.sin(flight_path_angle))
        dy = thrust[0] * m.sin(flight_path_angle) + thrust[1] * m.cos(flight_path_angle)
        self.cg_location = (center[0] + dx*2, center[1] + dy*2)
        self.cg_location = center

    def init_relative(self, part):
        top_left = part.rect.topleft
        struct_top_left = self.struct_rect.topleft
        rel_x = top_left[0] - struct_top_left[0]
        rel_y = top_left[1] - struct_top_left[1]
        part.relative_struct = (rel_x, rel_y)

    def update_part_position(self):
        for part in self.parts:
            part.rect.topleft = (self.struct_rect[0] + part.relative_struct[0], self.struct_rect[1] + part.relative_struct[1])

    def update(self, display_screen):
        # display_screen.blit(self.struct_image, self.struct_rect)
        self.update_part_position()
        for part in self.parts:
            relative_struct = part.cg_total_location
            struct = self.struct_rect.center
            theta_rad = -1*m.radians(self.angle)
            x_new = relative_struct[0] * m.cos(theta_rad) - relative_struct[1] * m.sin(theta_rad)
            y_new = relative_struct[0] * m.sin(theta_rad) + relative_struct[1] * m.cos(theta_rad)
            part.rect = part.display_image.get_rect(center=(x_new + struct[0], y_new + struct[1]))
            part.display_rec = part.display_image.get_rect(center=part.rect.center)
            display_screen.blit(part.display_image, part.display_rec)
        
        theta_rad = -1*m.radians(self.angle)
        x_new = self.cg_location_body[0]
        y_new = self.cg_location_body[1] 
        print((self.cg_location[0] + struct[0], self.cg_location[1] + struct[1]))
        pygame.draw.circle(display_screen, (255, 0, 0), (x_new + struct[0], y_new + struct[1]), 1)
        pygame.draw.circle(display_screen, (255, 0, 0), (self.cg_location[0] + struct[0], self.cg_location[1] + struct[1]), 1)

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

class Rocket(pygame.sprite.Sprite):
    def __init__(self, pos, vel, win_settings, group, image=None, rect=None):
        super().__init__(group)

        self.const_win_x = win_settings[0] // 2
        self.const_win_y = win_settings[1] // 2

        self.win_scale_x = win_settings[0]/(2*win_settings[2])
        self.win_scale_y = -1*win_settings[1]/(2*win_settings[3])

        # Load and scale the rocket image
        self.image = pygame.image.load('graphics/rocket.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 5, self.image.get_height() // 5))

        # Rotate the planet image
        self.display_image = pygame.transform.rotate(self.image, 0.0)

        # Set the center of the planet image
        self.x_centered = (pos[0] * self.win_scale_x) + self.const_win_x # Where to put sprite center in the screen
        self.y_centered = (pos[1] * self.win_scale_y) + self.const_win_y # Where to put sprite center in the screen

        # Calculate the top-left corner coordinates to center the image
        self.x_centered_transform = self.x_centered - self.image.get_width() // 2
        self.y_centered_transform = self.y_centered - self.image.get_height() // 2
        self.rect = self.display_image.get_rect(center=(self.x_centered, self.y_centered))

        # Rocket Info
        self.x = pos[0]  # position on x-axis [km]
        self.y = pos[1]  # position on y-axis [km]
        self.vx = vel[0] # velocity on x-axis [km]
        self.vy = vel[1] # velocity on y-axis [km]
        self.angle = 90   # Angle about the z-axis [deg]
        self.mass = 100  # mass of veh [kg]
        self.orbit_traj = [] # orbital trajectory [km]
        self.period = 0.0

        # Orbit States
        self.kepler_elements = {
            'a': 3,
            'e': 3,
            'i': 3,
            'RAAN': 3,
            'w': 3,
            'v': 3,
        }
        self.prev_angle = np.degrees(m.atan2(self.vy, self.vx))

        self.font = pygame.font.Font('font/Pixeltype.ttf', 25)
        self.orbit_parameters_text = [f"Semi-major Axis: {self.kepler_elements['a']}",
                                    f"Eccentricity: {self.kepler_elements['e']}",
                                    f"Inclination: {np.degrees(self.kepler_elements['i'])}",
                                    f"RAAN: {np.degrees(self.kepler_elements['RAAN'])}",
                                    f"Argument of P: {np.degrees(self.kepler_elements['w'])}",
                                    f"True Anomaly: {np.degrees(self.kepler_elements['v'])}"]
        for line in self.orbit_parameters_text:
            self.font_surface = self.font.render(line, False, 'Blue')
    
    def rocket_customize(self):
        pass

    def rocket_rotate(self, motion):
        if motion:
            self.angle -= 1
        else:
            self.angle += 1
        self.x_centered = (self.x * self.win_scale_x) + self.const_win_x
        self.y_centered = (self.y * self.win_scale_y) + self.const_win_y

        self.display_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.display_image.get_rect(center=(self.x_centered, self.y_centered))

    def rocket_fire(self):
        flight_path_angle = (np.degrees(m.atan2(self.vy, self.vx) ) % 360)
        flight_path_angle = self.angle % 360
        deltaV = 0.1
        if flight_path_angle >= 0 and flight_path_angle <= 90:
            vx = m.cos(m.radians(flight_path_angle))
            vy = m.sin(m.radians(flight_path_angle))
        elif flight_path_angle <= 180:
            vx = -1 * m.cos(m.radians(180 - flight_path_angle))
            vy = m.sin(m.radians(180 - flight_path_angle))
        elif flight_path_angle <= 270:
            vx = -1 * m.sin(m.radians(270 - flight_path_angle))
            vy = -1 * m.cos(m.radians(270 - flight_path_angle))
        elif flight_path_angle <= 360:
            vx = m.cos(m.radians(360 - flight_path_angle))
            vy = -1 * m.sin(m.radians(360 - flight_path_angle))
        self.vx += deltaV * vx
        self.vy += deltaV * vy

    def update_image(self, state):
        self.x = state[0]
        self.y = state[1]
        self.vx = state[3]
        self.vy = state[4]

        self.x_centered = (self.x * self.win_scale_x) + self.const_win_x
        self.y_centered = (self.y * self.win_scale_y) + self.const_win_y

        # self.display_image = pygame.transform.rotate(self.image, np.degrees(m.atan2(self.vy, self.vx) - (np.pi / 2)))
        self.display_image = pygame.transform.rotate(self.image, self.angle - 90)
        self.rect = self.display_image.get_rect(center=(self.x_centered, self.y_centered))

        self.x_centered_transform = self.x_centered - self.image.get_width() // 2
        self.y_centered_transform = self.y_centered - self.image.get_height() // 2

        return
    
    def update_kep_state(self, mu):
        [p ,a ,eNorm ,i ,RAAN, w, truev] = RV2COE(np.array([self.x, self.y, 0]), np.array([self.vx, self.vy, 0]))
        self.kepler_elements['a'] = a
        self.kepler_elements['e'] = eNorm
        self.kepler_elements['i'] = np.degrees(i)
        self.kepler_elements['RAAN'] = np.degrees(RAAN)
        self.kepler_elements['w'] = np.degrees(w)
        self.kepler_elements['v'] = np.degrees(truev)
        self.orbit_parameters_text = [f"Semi-major Axis: {self.kepler_elements['a']:.3f}",
                                    f"Eccentricity: {self.kepler_elements['e']:.3f}",
                                    f"Inclination: {self.kepler_elements['i']:.3f}",
                                    f"RAAN: {self.kepler_elements['RAAN']:.3f}",
                                    f"Argument of P: {self.kepler_elements['w']:.3f}",
                                    f"True Anomaly: {self.kepler_elements['v']:.3f}"]
        for line in self.orbit_parameters_text:
            self.font_surface = self.font.render(line, False, 'Blue')

        self.period = 2 * np.pi * m.sqrt(a**3 / mu)