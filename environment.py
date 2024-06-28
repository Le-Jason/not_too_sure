from data.planet_data import *

class Environment:
    def __init__(self):
        self.mu = 0 # gravitational parameter [km^3/s^2]

    def update(self):
        G = planet_data['Earth']['G']
        m = planet_data['Earth']['m']
        self.mu = G*m