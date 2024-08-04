import math as m
import numpy as np

from Algorithms.KeplerProblems import *

class StructFrame():
    """ Class to determine the structure frame

    Augments:
        parts (Sprite Group): Sprite Group of rocket during creation level
        com_screen_coords (array of two): Location of center of mass in screen coords
        length_per_pixel (double): meters per pixel

    """
    def __init__(self, parts, com_screen_coords, length_per_pixel):
        # Determine the dimensions of the rocket structure in screen coordinates
        bottom_limit_screen_coords = 0
        top_limit_screen_coords = 0
        right_limit_screen_coords = 0
        left_limit_screen_coords = 0
        init = False
        for part in parts:
            if init == False:
                bottom_limit_screen_coords = part.rect.bottom
                top_limit_screen_coords = part.rect.top
                right_limit_screen_coords = part.rect.right
                left_limit_screen_coords = part.rect.left
                center_screen_coords = part.rect.center
                init = True
            else:
                if part.rect.bottom > bottom_limit_screen_coords:
                    bottom_limit_screen_coords = part.rect.bottom
                if part.rect.top < top_limit_screen_coords:
                    top_limit_screen_coords = part.rect.top
                    center_screen_coords = part.rect.center
                if part.rect.right > right_limit_screen_coords:
                    right_limit_screen_coords = part.rect.right
                if part.rect.left < left_limit_screen_coords:
                    left_limit_screen_coords = part.rect.left

        # Find where each "part" center is relative to the center of this frame
        for part in parts:
            relative_center_part_x = part.rect.center[0] - center_screen_coords[0]
            relative_center_part_y = part.rect.center[1] - top_limit_screen_coords
            part.relative_struct_real = (relative_center_part_x, relative_center_part_y)

        # Find the location of the center of mass relative to the structure frame
        center_of_mass_x_struct_frame_screen_coords = (com_screen_coords[0] - center_screen_coords[0])
        center_of_mass_y_struct_frame_screen_coords = (com_screen_coords[1] - top_limit_screen_coords)

        # Other parameter for the structure frame
        self.height = (bottom_limit_screen_coords - top_limit_screen_coords)*length_per_pixel
        self.width = (right_limit_screen_coords - left_limit_screen_coords)*length_per_pixel
        self.origin = (-center_of_mass_x_struct_frame_screen_coords, -center_of_mass_y_struct_frame_screen_coords)
        self.parts = parts
        self.rotation = 0

class Rocket():
    """
    Class Structure that creates the rocket object and also manages it

    Augments:
        rocket (Object): Special rocket class from rocket creation level
        length_per_pixel (double): meter per each pixel

    """
    def __init__(self, rocket, length_per_pixel):
        # Create rocket frame and parts
        self.struct_frame = StructFrame(rocket.parts, rocket.cg_location, length_per_pixel)
        self.parts = rocket.parts

        # Assign members
        self.collision = False
        self.state = [0, 6378140.3, 0 , 0, 0, 0]
        self.prev_state = [0, 6378140.3, 0 , 0, 0, 0]

        # Assign Orbital Mechanics Variables
        self.semilatus_rectum = 0
        self.semimajor_axis = 0
        self.eccentricity = 0
        self.inclination = 0
        self.long_of_asc_node = 0
        self.arg_of_perigee = 0
        self.true_anomaly = 0
        self.arg_of_latitude = 0
        self.true_longitude = 0
        self.long_of_periapsis = 0

        # Temp Values for air density
        self.cd = 0.2
        self.A = 0.2
        self.m = 0.2

        self.periapsis = 0.0
        self.apoapsis = 0.0

        self.periapsis_tof = 0.0
        self.apoapsis_tof = 0.0
        self.COE = None

    def rocket_rotate(self, motion):
        """ Rotate the rocket structural frame

        Augments:
            motion (double): flag to determine rotate
        """
        if motion:
            self.struct_frame.rotation += 1
        else:
            self.struct_frame.rotation -= 1

    def rocket_fire(self):
        """ Fire the rocket engine are add delta-V

        TODO:
            Implement a working model
            Right now this is temp
        """
        temp_isp = 300
        temp_g0 =  9.80665
        temp_F = 20
        delta_m = temp_F / (temp_isp * temp_g0)
        temp_m0 = 1000
        delta_v = 100*temp_isp*temp_g0*m.log(temp_m0 / (temp_m0 - (delta_m*1)))

        # Assume the rocket is already orientated up at initialization
        delta_v_vector = [0, delta_v]

        # Rotate the vector to match the rocket orientation
        rotation_rad = np.deg2rad(-1*self.struct_frame.rotation)
        delta_v_I = delta_v_vector[0]*np.cos(rotation_rad) - delta_v_vector[1]*np.sin(rotation_rad)
        delta_v_J = delta_v_vector[0]*np.sin(rotation_rad) + delta_v_vector[1]*np.cos(rotation_rad)

        # Add the delta-V to the rocket state
        self.state = [self.state[0], self.state[1], 0, self.state[3] + delta_v_I, self.state[4] + delta_v_J, 0]

    def update_apoapsis_periapsis(self, mu):
        """ Compute the apoapsis and periapsis and time of flight to them 

        Augments:
            mu [m^3/kg*s^2]: gravitational coefficient
        """
        # Safe guard from undefined semimajor_axis and eccentricity
        if (self.semimajor_axis == 999999100000.0) or (self.eccentricity == 999999100000.0):
            self.periapsis = 0
            self.apoapsis = 0
        else:
            # Compute the apoapsis and periapsis in the perifocal frame
            self.periapsis = (self.semimajor_axis * (1 - self.eccentricity))
            self.apoapsis = (self.semimajor_axis * (1 + self.eccentricity))
            
            # Compute the current position in the perifocal frame
            temp = self.semilatus_rectum / (1.0 + self.eccentricity * np.cos(self.true_anomaly))
            pos_PQW = [temp * np.cos(self.true_anomaly),
                    temp * np.sin(self.true_anomaly),
                    0.0]

            self.periapsis_tof = findTOF(pos_PQW, [self.periapsis, 0.0, 0.0], self.semilatus_rectum, mu)
            self.apoapsis_tof = findTOF(pos_PQW, [-self.apoapsis, 0.0, 0.0], self.semilatus_rectum, mu)

    def update_keplerian_elements(self, mu):
        """ Update the keplerian elements

        Augments:
            mu [m^3/kg*s^2]: gravitational coefficient
        """
        # Get the position and velocity vector
        pos = np.array(self.state[:3])
        vel = np.array(self.state[3:])

        # Update the keplerian elements
        [self.semilatus_rectum, 
        self.semimajor_axis, 
        self.eccentricity, 
        self.inclination, 
        self.long_of_asc_node, 
        self.arg_of_perigee, 
        self.true_anomaly, 
        self.arg_of_latitude, 
        self.true_longitude, 
        self.long_of_periapsis] = RV2COE(pos, vel, mu)

    def update(self, mu):
        """ Update rocket members

        Augments:
            mu [m^3/kg*s^2]: gravitational coefficient
        """
        self.update_keplerian_elements(mu)
        self.update_apoapsis_periapsis(mu)