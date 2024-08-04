from data.planet_data import *
import math as m
import numpy as np

class Environment:
    def __init__(self):
        self.mu = 0 # gravitational parameter [m^3/s^2]
        self.rho = 0 # Atmospheric Density [kg/m**3]
        self.radius = 0 # planet radius [m]
        self.sky_color = (0, 0, 0) # the current planet sky color

        # Density Exponential Model
        self.nom_rho = 0
        self.base_alt = 0
        self.H = 1
        self.rho_limits = [planet_data['Earth']['nom_rho'][0], 0]

    def update(self, rocket):
        # Update the class members
        G = planet_data['Earth']['G']
        mass = planet_data['Earth']['m']
        self.mu = G*mass
        self.radius = planet_data['Earth']['radius']
        self.sky_color = planet_data['Earth']['sky_color']

        # Determine the altitudes
        rocket_position = rocket.state[:3]
        rocket_position_unit_vector = np.array(rocket_position) / np.linalg.norm(rocket_position)
        h_ellp = m.sqrt((rocket.state[0] - (self.radius*rocket_position_unit_vector[0]))**2 + 
                                                (rocket.state[1] - (self.radius*rocket_position_unit_vector[1]))**2 + 
                                                (rocket.state[2] - (self.radius*rocket_position_unit_vector[2]))**2)

        # Density Exponential Model
        if h_ellp < 25000:
            self.nom_rho = planet_data['Earth']['nom_rho'][0]
            self.base_alt = planet_data['Earth']['base_alt'][0]
            self.H = planet_data['Earth']['H'][0]
        elif h_ellp < 30000:
            self.nom_rho = planet_data['Earth']['nom_rho'][1]
            self.base_alt = planet_data['Earth']['base_alt'][1]
            self.H = planet_data['Earth']['H'][1]
        elif h_ellp < 40000:
            self.nom_rho = planet_data['Earth']['nom_rho'][2]
            self.base_alt = planet_data['Earth']['base_alt'][2]
            self.H = planet_data['Earth']['H'][2]
        elif h_ellp < 50000:
            self.nom_rho = planet_data['Earth']['nom_rho'][3]
            self.base_alt = planet_data['Earth']['base_alt'][3]
            self.H = planet_data['Earth']['H'][3]
        elif h_ellp < 60000:
            self.nom_rho = planet_data['Earth']['nom_rho'][4]
            self.base_alt = planet_data['Earth']['base_alt'][4]
            self.H = planet_data['Earth']['H'][4]
        elif h_ellp < 70000:
            self.nom_rho = planet_data['Earth']['nom_rho'][5]
            self.base_alt = planet_data['Earth']['base_alt'][5]
            self.H = planet_data['Earth']['H'][5]
        elif h_ellp >= 70000:
            # No Density
            self.nom_rho = 0
        self.update_density(h_ellp)

    def update_density(self, h_ellp):
        # Exponential Model
        # Assumes a spherically symmetrical distribution of particles
        self.rho = self.nom_rho * m.exp(-1* (h_ellp - self.base_alt)/ self.H)