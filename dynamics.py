import numpy as np
import pygame
from environment import *

class Dynamics:
    """
    Class Structure that manages the games dynamics

    """
    def __init__(self, system_info):
        # Create the environment managers
        self.env = Environment()

        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel_rocket_view = system_info['length_per_pixel']
        self.length_per_pixel_map_view = system_info['length_per_pixel_map']
        
        # TESTING
        self.overlap = (0,0)
        self.part_overlap = (0,0)

    def graphic_rocket_collision(self, rocket, obj_group, screen_dim):
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
                        collisions = pygame.sprite.spritecollide(part, obj_group, False, pygame.sprite.collide_mask)
                        for gnd in collisions:
                            offset = (gnd.rect.x - part.rect.x, gnd.rect.y - part.rect.y)
                            overlap = part.mask.overlap(gnd.mask, offset)
                            self.overlap = (part.rect.x + overlap[0], part.rect.y + overlap[1])
                            self.part_overlap = (part.rect.centerx, part.rect.centery)
                            pos_from_part = (self.overlap[0] - self.part_overlap[0], self.overlap[1] - self.part_overlap[1])
                            self.apply_moment(rocket, np.array([0, 9.81*10]), self.overlap, screen_dim)

    def apply_moment(self,rocket, force, pos_from_part, screen_dim):
        length_per_pixel = self.length_per_pixel_rocket_view
        # Find the screen frame dim
        y_max = screen_dim['rocket_view'][1]
        x_min = screen_dim['rocket_view'][2]

        # Convert the rocket IJK Center of Mass State to screen coordinates
        screen_coords_cg = ((rocket.state[0] - x_min) / length_per_pixel, (y_max - rocket.state[1]) / length_per_pixel)
        distance = np.array([pos_from_part[0] - screen_coords_cg[0], pos_from_part[1] - screen_coords_cg[1]]) * length_per_pixel
        moment = np.cross(distance, force)

        rocket.sum_moment -= moment # TODO: reverse this logic

    
    def rk4_angular_update(self, theta, omega, torque, inertia, dt):
        # Define the derivatives
        def dtheta_dt(theta, omega):
            return omega
        
        def domega_dt(theta, omega):
            return torque / inertia

        # Compute the RK4 coefficients
        k1_theta = dtheta_dt(theta, omega)
        k1_omega = domega_dt(theta, omega)

        k2_theta = dtheta_dt(theta + 0.5 * dt * k1_theta, omega + 0.5 * dt * k1_omega)
        k2_omega = domega_dt(theta + 0.5 * dt * k1_theta, omega + 0.5 * dt * k1_omega)

        k3_theta = dtheta_dt(theta + 0.5 * dt * k2_theta, omega + 0.5 * dt * k2_omega)
        k3_omega = domega_dt(theta + 0.5 * dt * k2_theta, omega + 0.5 * dt * k2_omega)

        k4_theta = dtheta_dt(theta + dt * k3_theta, omega + dt * k3_omega)
        k4_omega = domega_dt(theta + dt * k3_theta, omega + dt * k3_omega)

        # Update the angle and angular velocity
        theta_new = theta + (dt / 6.0) * (k1_theta + 2 * k2_theta + 2 * k3_theta + k4_theta)
        omega_new = omega + (dt / 6.0) * (k1_omega + 2 * k2_omega + 2 * k3_omega + k4_omega)

        return theta_new, omega_new

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
    
    def update_rocket(self, rocket, obj_group, screen_dim):
        """ Update the rocket state

            Augments:
                rocket (object): rocket object
                obj_group (Sprite Group): the objects that you can collide with

        """
        self.graphic_rocket_collision(rocket, obj_group, screen_dim)
        [rocket.ang_state[0], rocket.ang_state[1]] = self.rk4_angular_update(rocket.ang_state[0], rocket.ang_state[1], rocket.sum_moment, rocket.struct_frame.moment_of_inertia/10, 4/60)
        rocket.sum_moment = 0
        if rocket.collision:
            rocket.state = [rocket.prev_state[0], rocket.prev_state[1], rocket.prev_state[2],
                            0, 0, 0]
            rocket.ang_state = rocket.prev_ang_state
        else:
            rocket.prev_state = rocket.state
            rocket.prev_ang_state = rocket.ang_state
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