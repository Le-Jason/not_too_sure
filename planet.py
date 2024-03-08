import pygame
import math as m
BLUE = (0,96,255)

class Planet(pygame.sprite.Sprite):
    def __init__(self, win, group):
        super().__init__(group)
        self.image = pygame.image.load('graphics/earth.png').convert_alpha()
        self.rect = self.image.get_rect(center = win)
        self.center = win
        self.G = 6.673E-20       # gravitational coefficient [km^3/kg*s^2]
        self.m = 5.973320E24     # mass [kg]
        self.u = self.G * self.m # gravitational parameter [km^3/s^2]

    def update(self):
        pass

    def gravity_two_body(self, object):
        distance = m.sqrt((object.x - self.center[0])**2 + (object.y - self.center[1])**2)
        force = self.u * self.m / (distance**2)
        theta = m.atan2(object.y - self.center[1], object.x - self.center[0])
        force_x = -m.cos(theta) * force
        force_y = -m.sin(theta) * force
        print(force_x)

        return force_x, force_y

    def f(t, state):
        r1, r2, v1, v2 = state.reshape((4, 2))
        r = r2 - r1
        r_norm = np.linalg.norm(r)
        dv1dt = G * m2 * (r / r_norm**3)
        dv2dt = -G * m1 * (r / r_norm**3)
        dr1dt = v1
        dr2dt = v2
        return np.array([dr1dt, dr2dt, dv1dt, dv2dt]).flatten()

    def rk4(t, state, dt, f):
        k1 = f(t, state)
        k2 = f(t + dt/2, state + dt/2 * k1)
        k3 = f(t + dt/2, state + dt/2 * k2)
        k4 = f(t + dt, state + dt * k3)
        return state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)


