import numpy as np
import pygame
from environment import *

class Dynamics:
    """
    Class Structure that manages the games dynamics

    """
    def __init__(self):
        # Create the environment managers
        self.env = Environment()

    def graphic_rocket_collision(self, rocket, obj_group):
            """ Determine if the current rocket has collided

            Augments:
                rocket (Object): the rocket type of the rocket
                obj_group (Sprite Group): the objects that you can collide with
            """
            rocket.collision = False
            for part in rocket.parts:
                if pygame.sprite.spritecollide(part, obj_group, False):
                    if pygame.sprite.spritecollide(part, obj_group, False, pygame.sprite.collide_mask):
                        rocket.collision = True

    def dynamic_model_combine(self, t, state, rocket):
        """ Combine all the acceleration

            Augments:
                t (double): time stamp
                state (array of six): state of the object
                rocket (object): used to determine the air resistance

            Return:
                Derivative State
        """
        # Two Body Acceleration
        a_gravity = self.two_body_ode(t, state)

        # Air Resistance Acceleration
        a_drag = self.air_density(t, state, rocket)

        # Combine Acceleration
        a_total = a_gravity # + a_drag #TODO commented out to speed up testing

        return np.array([state[3], state[4], state[5], 
                        a_total[0], a_total[1], a_total[2]])

    def air_density(self, t, state, rocket):
        """ Compute Air Resistance Acceleration

            Augments:
                t (double): time stamp
                state (array of six): state of the object
                rocket (object): used to determine the air resistance

            Return:
                a_drag (array of three): air drag on the current rocket
        """
        vel = state[3:]
        v_rel = np.linalg.norm(vel)
        if v_rel != 0:
            a_drag = -0.5 * self.env.rho * v_rel**2 * rocket.cd * rocket.A / rocket.m * (vel / v_rel)
        else:
            a_drag = np.zeros(3)
        return a_drag

    def two_body_ode(self, t, state):
        """ Compute Two Body Acceleration

            Augments:
                t (double): time stamp
                state (array of six): state of the object

            Return:
                a_gravity (array of three): acceleration due to gravity
        """
        pos = np.array(state[:3])
        r = np.linalg.norm(pos)
        a_gravity = -self.env.mu * pos / r**3
        return a_gravity

    def rk4(self, t, state, dt, f, rocket):
        """ Runge-Kutta Integration Method

            Augments:
                t (double): time stamp
                state (array of six): state of the object
                dt (double): delta time (frame rate based)
                f (function): function to use for the integration
                rocket (object): rocket object

            Return:
                state: integrated state
        """
        k1 = f(t, state, rocket)
        k2 = f(t + dt/2, state + dt/2 * k1, rocket)
        k3 = f(t + dt/2, state + dt/2 * k2, rocket)
        k4 = f(t + dt, state + dt * k3, rocket)
        return state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    
    def update_rocket(self, rocket, obj_group):
        """ Update the rocket state

            Augments:
                rocket (object): rocket object
                obj_group (Sprite Group): the objects that you can collide with

        """
        self.graphic_rocket_collision(rocket, obj_group)
        if rocket.collision:
            rocket.state = [rocket.prev_state[0], rocket.prev_state[1], rocket.prev_state[2],
                            0, 0, 0]
        else:
            rocket.prev_state = rocket.state
            rocket.state = self.rk4(0, rocket.state, 4/60, self.dynamic_model_combine, rocket)


    def update(self, rocket):
        """ Update the dynamics manager

        Args:
            rocket (Object): rocket object

        TODO:
            Maybe start combining the function updates
        """
        # Update the environment manager
        self.env.update(rocket)