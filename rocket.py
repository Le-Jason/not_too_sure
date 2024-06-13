import pygame
import math as m
import numpy as np

from Algorithms.KeplerProblems import *

class StructFrame():
    def __init__(self, parts, cg, length_per_pixel):
        body_bottom = 0
        body_top = 0
        body_right = 0
        body_left = 0
        init = False
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
                    body_top = part.rect.top
                    body_center = part.rect.center
                if part.rect.right > body_right:
                    body_right = part.rect.right
                if part.rect.left < body_left:
                    body_left = part.rect.left
        for part in parts:
            relative_center_part_x = part.rect.center[0] - body_center[0]
            relative_center_part_y = part.rect.center[1] - body_top
            part.relative_struct_real = (relative_center_part_x, relative_center_part_y)
        cg_x = (cg[0] - body_center[0])
        cg_y = (cg[1] - body_top)

        self.height = (body_bottom - body_top)*length_per_pixel
        self.width = (body_right - body_left)*length_per_pixel
        self.origin = (-cg_x, -cg_y)
        self.parts = parts
        self.rotation = 0

class goundRocket():
    def __init__(self, rocket, vab_pic, vab_pic_rec):
        self.length_per_pixel = 1.25 / 53
        self.earth_radius = 6378.1363
        self.G = 6.673E-20         # gravitational coefficient [km^3/kg*s^2]
        self.m = 5.973320E24       # mass [kg]
        self.mu = self.G * self.m   # gravitational parameter [km^3/s^2]

        y_min = self.earth_radius
        y_max = (720*self.length_per_pixel) + y_min
        x_min = -((1280/2)*self.length_per_pixel)
        x_max = ((1280/2)*self.length_per_pixel)
        self.screen_dim = [y_min, y_max, x_min, x_max]

        launch_pad = self.get_visible_rect(vab_pic)
        launch_pad_x = vab_pic_rec[2]/2
        launch_pad_y = launch_pad[3]

        # Create rocket frame
        self.struct_frame = StructFrame(rocket.parts, rocket.cg_location, self.length_per_pixel)

        self.state = [0, self.struct_frame.height + (launch_pad_y*self.length_per_pixel) + self.earth_radius + (self.struct_frame.origin[1]*self.length_per_pixel), 0 , 0, 0, 0]

    def map_real_to_screen(self, display_screen, screen_dim, length_per_pixel, struct_frame, state):
        y_max = screen_dim[1]
        x_min = screen_dim[2]

        center_of_mass = ((state[0] - x_min) / length_per_pixel, (y_max - state[1]) / length_per_pixel)
        origin_x = struct_frame.origin[0]*np.cos(np.deg2rad(struct_frame.rotation)) - struct_frame.origin[1]*np.sin(np.deg2rad(struct_frame.rotation))
        origin_y = struct_frame.origin[0]*np.sin(np.deg2rad(struct_frame.rotation)) + struct_frame.origin[1]*np.cos(np.deg2rad(struct_frame.rotation))
        origin_ = (center_of_mass[0] + origin_x, center_of_mass[1] + origin_y)

        for part in struct_frame.parts:
            center_x = part.relative_struct_real[0]*np.cos(np.deg2rad(struct_frame.rotation)) - part.relative_struct_real[1]*np.sin(np.deg2rad(struct_frame.rotation))
            center_y = part.relative_struct_real[0]*np.sin(np.deg2rad(struct_frame.rotation)) + part.relative_struct_real[1]*np.cos(np.deg2rad(struct_frame.rotation))
            part.rect.center = (origin_[0] + center_x, origin_[1] + center_y)
            display_image = pygame.transform.rotate(part.image, -1*struct_frame.rotation)
            display_rec = display_image.get_rect(center=part.rect.center)
            display_screen.blit(display_image, display_rec)

        pygame.draw.circle(display_screen, (255, 0, 0), center_of_mass, 1)
        pygame.draw.circle(display_screen, (0, 255, 0), origin_, 1)



    def rocket_rotate(self, motion):
        if motion:
            self.struct_frame.rotation += 1
        else:
            self.struct_frame.rotation -= 1

    def rocket_fire(self):
        temp_isp = 300
        temp_g0 =  9.80665
        temp_F = 20
        delta_m = temp_F / (temp_isp * temp_g0)
        temp_m0 = 1000
        delta_v = temp_isp*temp_g0*m.log(temp_m0 / (temp_m0 - (delta_m*1)))


        vector = [0, delta_v]
        vector_x = vector[0]*np.cos(np.deg2rad(-1*self.struct_frame.rotation)) - vector[1]*np.sin(np.deg2rad(-1*self.struct_frame.rotation))
        vector_y = vector[0]*np.sin(np.deg2rad(-1*self.struct_frame.rotation)) + vector[1]*np.cos(np.deg2rad(-1*self.struct_frame.rotation))

        print("X:"+str(vector_x))
        print("Y:"+str(vector_y))

        self.state = [self.state[0], self.state[1], 0, self.state[3] + vector_x, self.state[4] + vector_y, 0]

    def update(self, display_screen):
        self.state = self.rk4(0, self.state, 1, self.two_body_ode)
        self.map_real_to_screen(display_screen, self.screen_dim, self.length_per_pixel, self.struct_frame, self.state)

    def propagate_body(self, t, state, dt, f, timespan):
        traj = []
        while t < timespan:
            state = self.rk4(t, state, dt, f)
            t += dt
            traj.append([state[0], state[1], state[2]])
        return traj


    def two_body_ode(self, t, state):
        state = np.array(state)
        r = state[:3] - [0, 0, 0]
        a = -self.mu * r / np.linalg.norm(r) ** 3
        return np.array([state[3], state[4], state[5], 
                        a[0], a[1], a[2]])

    def rk4(self, t, state, dt, f):
    # RK4 Numerical Methods 
        k1 = f(t, state)
        k2 = f(t + dt/2, state + dt/2 * k1)
        k3 = f(t + dt/2, state + dt/2 * k2)
        k4 = f(t + dt, state + dt * k3)
        return state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

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