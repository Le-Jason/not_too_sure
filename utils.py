import time

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