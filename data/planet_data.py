planet_data = {
    'Earth': {
        'G': 6.673E-11,         # gravitational coefficient [m^3/kg*s^2]
        'm': 5.973320E24,       # mass [kg]
        'radius': 6378136.3,    # radius [m]
        'rot_vel': 7.292115E-5, # rotational velocity [rad/s]

        #  Exponential Atmospheric Model Table
        'nom_rho': [1.225, 3.899e-2, 1.774e-2, 3.972e-3, 1.057e-3, 3.206e-4], # [kg/m**3] Nominal Density
        'base_alt':[0,     25000,    30000,    40000,    50000,    60000],    # [m] Base Altitude
        'H':       [7249,  6349,     6682,     7554,     8382,     7714],     # [m] Scale Factor

        # Sky Color
        'sky_color': (99, 155, 255), # RGB Color
    }
}