import time
from core import *

class PygameUtils:
    @staticmethod
    def is_mouse_pressed_without_debounce(last_press_time, debounce_time):
        # last press time is a array so it can be pass by reference
        current_time = time.time()
        if ((current_time - last_press_time[0]) >= (debounce_time/1000)):
            temp = current_time
            last_press_time[0] = temp
            return True
        return False

    @staticmethod
    def check_for_hover(mouse_position, sprite):
        local_x = mouse_position[0] - sprite.rect.x
        local_y = mouse_position[1] - sprite.rect.y
        if sprite.rect.collidepoint(mouse_position[0], mouse_position[1]):
            if sprite.mask.get_at((local_x, local_y)):
                return True
        return False

    @staticmethod
    def check_for_input(mouse_button, mouse_position, sprite, last_press_time, debounce_time):
        check = False
        hover_check = PygameUtils.check_for_hover(mouse_position, sprite)
        input_check = mouse_button[0]
        if (hover_check and input_check):
            check = PygameUtils.is_mouse_pressed_without_debounce(last_press_time, debounce_time)
        return check

    @staticmethod
    def check_for_hover_tree(mouse_position, root):
        hover_node = PygameUtils.check_for_hover(mouse_position, root)
        if hover_node == True:
            return root

        for child in root.children:
            hover_node = PygameUtils.check_for_hover_tree(mouse_position, child)
            if hover_node is not None:
                return hover_node

        return None

    @staticmethod
    def find_center_offset(image):
        """Calculate the average position of all non-transparent pixels."""
        width, height = image.get_size()
        total_x, total_y, count = 0, 0, 0

        for y in range(height):
            for x in range(width):
                if image.get_at((x, y))[3] > 0:  # Check alpha value
                    total_x += x
                    total_y += y
                    count += 1

        if count == 0:
            return 0, 0  # Fallback in case the image is completely transparent

        # Calculate average position
        return total_x // count, total_y // count

    @staticmethod
    def get_top_right_non_transparent_pixel(sprite):
        image = sprite.image
        # Get the dimensions of the surface
        width, height = image.get_size()

        # Start from the top-right corner (x = width-1, y = 0)
        for x in range(width-1, -1, -1):
            for y in range(height):
                # Get the color of the current pixel at (x, y)
                color = image.get_at((x, y))

                # Check if the pixel is not transparent
                if color[3] != 0:  # The alpha value (index 3) determines transparency
                    return (x + sprite.rect.left), (y + sprite.rect.top)

        # If no non-transparent pixel is found, return None
        return None

    @staticmethod
    def get_top_left_non_transparent_pixel(sprite):
        image = sprite.image
        # Get the dimensions of the surface
        width, height = image.get_size()

        # Start from the top-left corner (x = 0, y = 0)
        for x in range(width):
            for y in range(height):
                # Get the color of the current pixel at (x, y)
                color = image.get_at((x, y))

                # Check if the pixel is not transparent
                if color[3] != 0:  # The alpha value (index 3) determines transparency
                    return (x + sprite.rect.left), (y + sprite.rect.top)

        # If no non-transparent pixel is found, return None
        return None

    @staticmethod
    def get_bottom_left_non_transparent_pixel(sprite):
        image = sprite.image
        # Get the dimensions of the surface
        width, height = image.get_size()

        # Start from the bottom-left corner (x = 0, y = width-1)
        for x in range(width):
            for y in range(height-1, -1, -1):
                # Get the color of the current pixel at (x, y)
                color = image.get_at((x, y))

                # Check if the pixel is not transparent
                if color[3] != 0:  # The alpha value (index 3) determines transparency
                    return (x + sprite.rect.left), (y + sprite.rect.top)

        # If no non-transparent pixel is found, return None
        return None

    @staticmethod
    def get_bottom_right_non_transparent_pixel(sprite):
        image = sprite.image
        # Get the dimensions of the surface
        width, height = image.get_size()

        # Start from the top-left corner (x = width-1, y = height-1)
        for x in range(width-1, -1, -1):
            for y in range(height-1, -1, -1):
                # Get the color of the current pixel at (x, y)
                color = image.get_at((x, y))

                # Check if the pixel is not transparent
                if color[3] != 0:  # The alpha value (index 3) determines transparency
                    return (x + sprite.rect.left), (y + sprite.rect.top)

        # If no non-transparent pixel is found, return None
        return None

    @staticmethod
    def vector_average(vec_1, vec_2):
        result = Vector3()
        result.x = (vec_1.x + vec_2.x) / 2.0
        result.y = (vec_1.y + vec_2.y) / 2.0
        result.z = (vec_1.z + vec_2.z) / 2.0
        return result

    @staticmethod
    def clamp(value, min_value, max_value):
        return max(min(value, max_value), min_value)

import numpy as np

class PolyInterpolator:
    def __init__(self, x_values, y_values):
        self.x_values = np.array(x_values)
        self.y_values = np.array(y_values)

    def interpolator(self, *coefficients):
        # For simplicity, using polynomial interpolation using numpy
        # This could be adjusted depending on the exact nature of PolyInterpolator in the Java code
        # Returns a 1D polynomial based on coefficients
        return np.poly1d(coefficients)

    @staticmethod
    def eval(angle, poly_coefficients):
        # Evaluates the polynomial at a given angle
        return np.polyval(poly_coefficients, angle)

from abc import ABC, abstractmethod

# EventObject equivalent class (to hold event data)
class EventObject:
    def __init__(self, source):
        self.source = source  # You can add more attributes depending on what data is needed.

# StateChangeListener equivalent in Python
class StateChangeListener(ABC):
    @abstractmethod
    def state_changed(self, event: EventObject):
        pass

# ChangeSource class that mimics the Java interface
class ChangeSource:
    def __init__(self):
        self.listeners = []  # A list to store listeners

    def add_change_listener(self, listener: StateChangeListener):
        """Add a listener to the list"""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def remove_change_listener(self, listener: StateChangeListener):
        """Remove a listener from the list"""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def notify_change(self, event: EventObject):
        """Notify all listeners of the state change"""
        for listener in self.listeners:
            listener.state_changed(event)

# Implementing a listener class
class ConcreteListener(StateChangeListener):
    def state_changed(self, event: EventObject):
        print(f"State changed! Event source: {event.source}")