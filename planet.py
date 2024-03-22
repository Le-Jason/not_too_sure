import pygame
import math as m
import numpy as np
BLUE = (0,96,255)

class Planet(pygame.sprite.Sprite):
    def __init__(self, win_settings, group):
        super().__init__(group)
        self.radius = 6378.1363

        # Scale Image from the real radius to game 
        self.win_scale = win_settings[2] / self.radius

        # Load and scale the planet image
        self.image = pygame.image.load('graphics/earth.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // self.win_scale, self.image.get_height() // self.win_scale))

        # Rotate the planet image
        self.angle = 0
        self.display_image = pygame.transform.rotate(self.image, 0.0)

        # Set the center of the planet image
        self.x_centered = win_settings[0] // 2 # Where to put sprite center in the screen
        self.y_centered = win_settings[1] // 2 # Where to put sprite center in the screen

        # Calculate the top-left corner coordinates to center the image
        self.x_centered_transform = self.x_centered - self.image.get_width() // 2
        self.y_centered_transform = self.y_centered - self.image.get_height() // 2
        self.rect = self.display_image.get_rect(center=(self.x_centered, self.y_centered))

        # Planet Info
        self.x = 0                 # position on x-axis [km]
        self.y = 0                 # position on y-axis [km]
        self.G = 6.673E-20         # gravitational coefficient [km^3/kg*s^2]
        self.m = 5.973320E24       # mass [kg]
        self.mu = self.G * self.m   # gravitational parameter [km^3/s^2]
        self.rot_vel = 7.292115E-5 # rotational velocity [rad/s]

    def update(self):
        pass

    def update_image(self, MET_TIME):
        self.angle = self.rot_vel * MET_TIME
        self.display_image = pygame.transform.rotate(self.image, np.degrees(self.angle))
        self.rect = self.display_image.get_rect(center=(self.x_centered, self.y_centered))
        return
    
    def propagate_body(self, t, state, dt, f, timespan):
        traj = []
        while t < timespan:
            state = self.rk4(t, state, dt, f)
            t += dt
            traj.append([state[0], state[1], state[2]])
        return traj


    def two_body_ode(self, t, state):
        state = np.array(state)
        r = state[:3] - [self.x, self.y, 0]
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


