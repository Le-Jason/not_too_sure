import numpy as np
import pygame
from environment import *

class Dynamics:
    def __init__(self):
        self.env = Environment()

    def graphic_rocket_collision(self, rocket, obj_group):
    # Detects is the rocket parts collide with obj_group
    # Rocket Class
    # Object Sprite Group
            rocket.collision = False
            for part in rocket.parts:
                if pygame.sprite.spritecollide(part, obj_group, False):
                    if pygame.sprite.spritecollide(part, obj_group, False, pygame.sprite.collide_mask):
                        rocket.collision = True

    def two_body_ode(self, t, state):
    # Two Body ODE function
    # t = given time
    # state = [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
        state = np.array(state)
        r = state[:3] - [0, 0, 0]
        a = -self.env.mu * r / np.linalg.norm(r) ** 3

        return np.array([state[3], state[4], state[5], 
                        a[0], a[1], a[2]])

    def rk4(self, t, state, dt, f):
    # RK4 Numerical Methods 
    # t = given time
    # state = [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
    # dt = time step
    # f = integrator function
        k1 = f(t, state)
        k2 = f(t + dt/2, state + dt/2 * k1)
        k3 = f(t + dt/2, state + dt/2 * k2)
        k4 = f(t + dt, state + dt * k3)
        return state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    
    def update_rocket(self, rocket, obj_group):
        self.graphic_rocket_collision(rocket, obj_group)
        if rocket.collision:
            rocket.state = [rocket.prev_state[0], rocket.prev_state[1], rocket.prev_state[2],
                            0, 0, 0]
        else:
            rocket.prev_state = rocket.state
            rocket.state = self.rk4(0, rocket.state, 1, self.two_body_ode)

    def update(self):
        self.env.update()