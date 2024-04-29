import pygame
import math as m
import numpy as np

from Algorithms.KeplerProblems import *

class goundRocket():
    def __init__(self, parts, vab_pic, vab_pic_rec):
        self.parts = parts
        # TODO: Get the transparent part to make the rocket init on the launch pad
        for part in parts:
            pass

    def update(self, display_screen):
        self.parts.draw(display_screen)

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