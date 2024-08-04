import numpy as np
from Algorithms.KeplerProblems import *
import pygame

class Graphics:
    """
    Class Structure that manages the graphics

    Augments:
        display_screen (object): screen display object
        system_info (dict): key info about the game screen
        sky_color (truple): Color of the current planet
        y_start_rocket_frame (double): Start of the y_min frame (IJK frame)

    """
    def __init__(self, display_screen, system_info, sky_color, y_start_rocket_frame):
        # Assign class members
        self.display_screen = display_screen
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.length_per_pixel_rocket_view = system_info['length_per_pixel']
        self.length_per_pixel_map_view = system_info['length_per_pixel_map']
        self.frame_mode = 'LOCK_ROCKET'
        self.selected_rocket = None

        # Background
        self.START_BG_COL = sky_color      # Color of the ground sky
        self.END_BG_COL = (34, 32, 52)     # Color of space

        # Init Map View Param
        self.y_min_map = -((self.HEIGHT/2)*self.length_per_pixel_map_view)
        self.y_max_map = ((self.HEIGHT/2)*self.length_per_pixel_map_view)
        self.x_min_map = -((self.WIDTH/2)*self.length_per_pixel_map_view)
        self.x_max_map = ((self.WIDTH/2)*self.length_per_pixel_map_view)

        # Init Frame on the surface of Earth (Assume starting on the Earth)
        self.y_min = y_start_rocket_frame
        self.y_max = (self.HEIGHT*self.length_per_pixel_rocket_view) + self.y_min
        self.x_min = -((self.WIDTH/2)*self.length_per_pixel_rocket_view)
        self.x_max = ((self.WIDTH/2)*self.length_per_pixel_rocket_view)

        # Assigning frame dimensions
        self.screen_frame_dim = {
            'rocket_view': [self.y_min, self.y_max, self.x_min, self.x_max],
            'map_view': [self.y_min_map, self.y_max_map, self.x_min_map, self.x_max_map],
        }

    def lock_frame_to_rocket(self, selected_rocket):
        """ Update the screen frame dim to follow the rocket
            Rocket is always in the middle of the screen

        Args:
            selected_rocket (object): Rocket Object
        """
        # This is just in case when there is no selected rocket
        if selected_rocket == None:
            return
        
        # Get the rocket IJK Position
        pos_I = selected_rocket.state[0]
        pos_J = selected_rocket.state[1]

        # Decompose the screen frame dim
        y_min = self.screen_frame_dim['rocket_view'][0]
        y_max = self.screen_frame_dim['rocket_view'][1]
        x_min = self.screen_frame_dim['rocket_view'][2]
        x_max = self.screen_frame_dim['rocket_view'][3]

        # Find half of the screen
        height_half = abs(y_max - y_min)/2
        width_half = abs(x_max - x_min)/2

        # Update the screen frame dim
        y_max = pos_J + height_half
        y_min = pos_J - height_half
        x_min = pos_I - width_half
        x_max = pos_I + width_half
        self.screen_frame_dim['rocket_view'] = [y_min, y_max, x_min, x_max]

    def map_rocket_to_screen(self, rocket, view):
        """ Draw the rocket on the screen

        Args:
            rocket (object): Rocket Object

        TODO:
            Make zoom work
        """
        # Find the screen frame dim
        y_max = self.screen_frame_dim[view][1]
        x_min = self.screen_frame_dim[view][2]
        if view == 'rocket_view':
            length_per_pixel = self.length_per_pixel_rocket_view
        else:
            length_per_pixel = self.length_per_pixel_map_view

        # Rotation in radians
        rotation_radians = np.deg2rad(rocket.struct_frame.rotation)

        # Convert the rocket IJK Center of Mass State to screen coordinates
        screen_coords_cg = ((rocket.state[0] - x_min) / length_per_pixel, (y_max - rocket.state[1]) / length_per_pixel)

        # Convert the rocket struct (screen coordinates frame) to screen coordinates (due to rotation)
        screen_coords_origin_x = rocket.struct_frame.origin[0]*np.cos(rotation_radians) - rocket.struct_frame.origin[1]*np.sin(rotation_radians)
        screen_coords_origin_y = rocket.struct_frame.origin[0]*np.sin(rotation_radians) + rocket.struct_frame.origin[1]*np.cos(rotation_radians)
        screen_coords_origin = (screen_coords_cg[0] + screen_coords_origin_x, screen_coords_cg[1] + screen_coords_origin_y)

        # Convert the rocket parts (screen coordinates frame) to screen coordinates (due to rotation)
        for part in rocket.struct_frame.parts:
            # Calc the dim
            part_center_screen_coords_x = part.relative_struct_real[0]*np.cos(rotation_radians) - part.relative_struct_real[1]*np.sin(rotation_radians)
            part_center_screen_coords_y = part.relative_struct_real[0]*np.sin(rotation_radians) + part.relative_struct_real[1]*np.cos(rotation_radians)
            part.rect.center = (screen_coords_origin[0] + part_center_screen_coords_x, screen_coords_origin[1] + part_center_screen_coords_y)
            # Update and Draw the part
            display_image = pygame.transform.rotate(part.image, -1*rocket.struct_frame.rotation)
            part.rect = display_image.get_rect(center=part.rect.center)
            part.mask = pygame.mask.from_surface(display_image)
            self.display_screen.blit(display_image, part.rect)

        # Testing Purpose: cg location and origin point
        pygame.draw.circle(self.display_screen, (255, 0, 0), screen_coords_cg, 1)
        pygame.draw.circle(self.display_screen, (0, 255, 0), screen_coords_origin, 1)

    def scaled_map(self, scale, view):
        """ Update the screen frame dim to zoom in and out

        Args:
            scale (double): Zoom factor
            view (string): Which view are you zooming
        """
        if view == 'map_view':
            self.screen_frame_dim[view] = [self.y_min_map * scale, self.y_max_map * scale, self.x_min_map * scale, self.x_max_map * scale]
            self.length_per_pixel_map_view = scale * 6378136.3 / 193.5 # TODO make the hard coded value not hard coded

    def map_object_to_screen(self, object, view):
        """ Draw a object on the screen

        Args:
            object (Object): object
            view (string): which view are you placing the object
        """
        # Find the screen frame dim
        y_max = self.screen_frame_dim[view][1]
        x_min = self.screen_frame_dim[view][2]
        if view == 'rocket_view':
            # TODO: make zooming work
            length_per_pixel = self.length_per_pixel_rocket_view
        elif view == 'map_view':
            length_per_pixel = self.length_per_pixel_map_view
            scale = (object.size / object.mask_rect_width) / length_per_pixel
            object.scaled_image(scale)

        # Convert the IJK State to screen coordinates
        screen_coords_state = ((object.state[0] - x_min) / length_per_pixel, (y_max - object.state[1]) / length_per_pixel)

        # Get the picture dim
        display_image_dim = (object.rect[2], object.rect[3])

        # The object state is the top part of the picture
        if object.location_init == 'top':
            # TODO: I think update logic so it returns based on the non transparent dim
            if (((screen_coords_state[1] + display_image_dim[1]/2) < 0) or             # state_y with the height is above the screen
                (screen_coords_state[1] - display_image_dim[1]/2 > self.HEIGHT) or     # state_y with the height is below the screen
                ((screen_coords_state[0] + (display_image_dim[0]/2)) < 0) or           # state_x with the width is left the screen
                ((screen_coords_state[0] - (display_image_dim[0]/2)) > self.WIDTH)):   # state_x with the width is right the screen
                return # Don't display
        # The object state is the center
        else:
            if (((screen_coords_state[1] + display_image_dim[1]/2) < 0) or             # state_y with the height is above the screen
                (screen_coords_state[1] - display_image_dim[1]/2 > self.HEIGHT) or     # state_y with the height is below the screen
                ((screen_coords_state[0] + (display_image_dim[0]/2)) < 0) or           # state_x with the width is left the screen
                ((screen_coords_state[0] - (display_image_dim[0]/2)) > self.WIDTH)):   # state_x with the width is right the screen
                return
        # Update and Draw the part
        object.rect.center = (screen_coords_state[0], screen_coords_state[1])
        display_image = pygame.transform.rotate(object.image, object.rotation)
        object.rect = display_image.get_rect(center=object.rect.center)
        object.mask = pygame.mask.from_surface(display_image)
        self.display_screen.blit(display_image, object.rect)

    def map_orbit_to_screen(self, pos, view, col=(255, 0, 0)):
        y_max = self.screen_frame_dim[view][1]
        x_min = self.screen_frame_dim[view][2]
        if view == 'rocket_view':
            length_per_pixel = self.length_per_pixel_rocket_view
        elif view == 'map_view':
            length_per_pixel = self.length_per_pixel_map_view

        center_of_mass = ((pos[0] - x_min) / length_per_pixel, (y_max - pos[1]) / length_per_pixel)

        if (center_of_mass[1] < 0) or (center_of_mass[1] > self.HEIGHT) or (center_of_mass[0] < 0) or (center_of_mass[0] > self.WIDTH): 
            return
        
        og_image = pygame.image.load('graphics/spites/map_orbit.png').convert_alpha()
        og_image = pygame.transform.scale_by(og_image, 0.4)
        rect = og_image.get_rect(center=center_of_mass)
        self.display_screen.blit(og_image, rect)
        # pygame.draw.circle(self.display_screen, col, center_of_mass, 1)

    def interpolate_color(self, color1, color2, factor):
        if factor > 1.0:
            factor = 1.0
        if factor < 0.0:
            factor = 0.0

        return (
            int(color1[0] + (color2[0] - color1[0]) * factor),
            int(color1[1] + (color2[1] - color1[1]) * factor),
            int(color1[2] + (color2[2] - color1[2]) * factor)
        )
    
    def map_orbit(self, rocket, mu):
        """ Display the orbit

        Args:
            rocket (Object): Object that you want to display for orbit
            mu (double): gravitational parameter
        """
        # Find the screen frame dim
        y_max = self.screen_frame_dim['map_view'][1]
        x_min = self.screen_frame_dim['map_view'][2]
        length_per_pixel = self.length_per_pixel_map_view

        # Find the trajectory points (1 deg apart)
        traj_points = []
        prev_point = [0.0, 0.0]
        for i in range(361):
            [traj_point, v] = COE2RV(
                rocket.semilatus_rectum, 
                rocket.eccentricity, 
                rocket.inclination, 
                rocket.long_of_asc_node, 
                rocket.arg_of_perigee, 
                np.deg2rad(i), 
                rocket.arg_of_latitude, 
                rocket.true_longitude, 
                rocket.long_of_periapsis, 
                mu)
            screen_coords_point = [(traj_point[0] - x_min) / length_per_pixel, (y_max - traj_point[1]) / length_per_pixel]
            if i == 0:
            # Assign prev_point if this is the first iteration
                prev_point = screen_coords_point
            # Plot the points that is already loaded if the next point is outside the screen border
            if ((screen_coords_point[1] < 0) or            # state_y with the height is above the screen
                (screen_coords_point[1] > self.HEIGHT) or  # state_y with the height is below the screen
                (screen_coords_point[0] < 0) or            # state_x with the width is left the screen
                (screen_coords_point[0] > self.WIDTH)):     # state_x with the width is right the screen
                if (len(traj_points) > 1): # must have at least two points
                    winner = self.edge_border_remap(prev_point, screen_coords_point)
                    if winner != None:
                        traj_points.append(winner)
                    pygame.draw.lines(self.display_screen, (255, 255, 255), False, traj_points, 1)
                traj_points = []
            else:
                if len(traj_points) == 0:
                    if ((prev_point[1] < 0) or            # state_y with the height is above the screen
                    (prev_point[1] > self.HEIGHT) or  # state_y with the height is below the screen
                    (prev_point[0] < 0) or            # state_x with the width is left the screen
                    (prev_point[0] > self.WIDTH)):     # state_x with the width is right the screen
                        winner = self.edge_border_remap(screen_coords_point, prev_point)
                        if winner != None:
                            traj_points.append(winner)
                    else:
                        traj_points.append(prev_point)
                traj_points.append(screen_coords_point)
            prev_point = screen_coords_point
        # Plot the leftovers
        if len(traj_points) > 1:
            pygame.draw.lines(self.display_screen, (255, 255, 255), False, traj_points, 1)


        [r_w, v] = COE2RV(rocket.semilatus_rectum, 
                        rocket.eccentricity, 
                        rocket.inclination, 
                        rocket.long_of_asc_node, 
                        rocket.arg_of_perigee, 
                        rocket.true_anomaly, 
                        rocket.arg_of_latitude, 
                        rocket.true_longitude,
                        rocket.long_of_periapsis, 
                        mu)
        # self.map_orbit_to_screen(r, 'map_view', col=(0, 255, 0))
        
        self.map_orbit_to_screen(r_w, 'map_view', col=(0, 255, 0))

    def update(self, rocket, env):
        """Update sprites

        Args:
            rocket (Object): the rocket you selected
            env (Class): environment manager object
        """
        # Update color of the sky
        self.START_BG_COL = env.sky_color
        bg_col = self.interpolate_color(self.END_BG_COL , self.START_BG_COL, env.rho / env.rho_limits[0])
        self.display_screen.fill(bg_col)

        # Lock to the current rocket
        self.selected_rocket = rocket
        if self.frame_mode == 'LOCK_ROCKET':
            self.lock_frame_to_rocket(self.selected_rocket)

    def update_map(self, rocket, mu):
        """Update the map screen

        Args:
            rocket (Object): the rocket you selected
            env (Class): environment manager object
        """
        # Update color of the background
        self.display_screen.fill(self.END_BG_COL)

        # Update the rocket orbit and rocket current location
        self.map_orbit_to_screen(rocket.state[:3], 'map_view', col=(0, 255, 0))
        self.map_orbit(rocket, mu)

    def edge_border_remap(self, point1, point2):
        """Find point if one point is inside the border and the second point is outside the border
            make sure that second point stops at the border

        Args:
            point1 (array[2]): Point inside the border
            point2 (array[2]): Point outside the border

        Returns:
            array[2]: Point that is on the border
        """
        
        # Setup for border edge points
        slope = None
        intercept = None
        intersections = []

        # Calculate the slope (m) and y-intercept (b) of the line y = mx + b
        if point2[0] != point1[0]:
            slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
            intercept = point1[1] - slope * point1[0]

        # Check for intersection with each of the four screen borders
        # Left border (x = 0)
        if slope is not None:
            y_left = slope * 0 + intercept
            if 0 <= y_left <= self.HEIGHT:
                intersections.append((0, y_left))
        
        # Right border (x = screen_width)
        if slope is not None:
            y_right = slope * self.WIDTH + intercept
            if 0 <= y_right <= self.HEIGHT:
                intersections.append((self.WIDTH, y_right))

        # Top border (y = 0)
        if slope is not None and slope != 0:
            x_top = (0 - intercept) / slope
            if 0 <= x_top <= self.WIDTH:
                intersections.append((x_top, 0))

        # Bottom border (y = screen_height)
        if slope is not None and slope != 0:
            x_bottom = (self.HEIGHT - intercept) / slope
            if 0 <= x_bottom <= self.WIDTH:
                intersections.append((x_bottom, self.HEIGHT))

        # If the line is vertical
        if slope is None:
            if point1[1] < point2[1]:  # Point outside is below the screen
                intersections.append((point1[0], self.HEIGHT))
            else:  # Point outside is above the screen
                intersections.append((point1[0], 0))

        # Return the closest intersection point found
        if intersections:
            winner = None
            condition = None
            temp = True
            for inter_point in intersections:
                r_mag = m.sqrt(abs(inter_point[0] - point1[0])**2 + abs(inter_point[1] - point1[1])**2)
                if temp:
                    winner = inter_point
                    condition = r_mag
                    temp = False
                elif condition > r_mag:
                    winner = inter_point
                    condition = r_mag
        return winner