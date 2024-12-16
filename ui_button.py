import pygame
from rocket import *
from data.part_data import *
from rocket_parts import *
import json
from labels import *
from utils import *
from abc import abstractmethod

class rocket_part_group():
    def __init__(self):
        self.parts = pygame.sprite.Group()
        self.idx = 0
        self.parts_idx = []
        self.type = []
        self.is_follow = False

        self.cg_location = [0, 0]
        self.moment_of_inertia = 0

    def add(self, image, rec, prop, type):
        self.parts.add(button_parts(image, rec, prop))
        self.parts_idx.append(self.idx)
        self.type.append(type)
        self.idx += 1

    def calc_center_of_mass(self):
        tot_mass = 0
        dx_mass = 0
        dy_mass = 0
        for part in self.parts:
            top_left = part.rect.topleft
            tot_mass += part.cg_location[2]
            dx_mass += part.cg_location[2]*(part.cg_location[0]+top_left[0])
            dy_mass += part.cg_location[2]*(part.cg_location[1]+top_left[1])
        cg_x = dx_mass / tot_mass
        cg_y = dy_mass / tot_mass
        return [cg_x, cg_y]

    def calc_moment_of_inertia(self):
        area_pix_sqrt_to_m_sqrt = 16 / 4096
        I_tot = 0
        for part in self.parts:
            top_left = part.rect.topleft
            r_sqrt = (((part.cg_location[0]+top_left[0])-self.cg_location[0])**2) + (((part.cg_location[1]+top_left[1])-self.cg_location[1])**2) * area_pix_sqrt_to_m_sqrt
            I_tot += part.moment_of_inertia + part.mass*r_sqrt
        return I_tot

    def player_input(self):
        mouse_buttons = pygame.mouse.get_pressed()
        current_mouse_pos = pygame.mouse.get_pos()
        for part in self.parts:
            if part.rect.collidepoint(current_mouse_pos) and (mouse_buttons[0] == True) and (self.is_follow == False):
                part.alr_snap = False
                if (part.snap_parent != None):
                    part.snap_parent.btm_conn = False
                    part.snap_parent.top_conn = False
                part.mouse_follow_active = True
                self.is_follow = True
            elif (mouse_buttons[0] == False):
                self.check_connection()
                part.mouse_follow_active = False
                if self.is_follow:
                    self.cg_location = self.calc_center_of_mass()
                    self.moment_of_inertia = self.calc_moment_of_inertia()
                self.is_follow = False

    def check_connection(self):
        child = None
        if self.is_follow == True:
            for part in self.parts:
                if part.mouse_follow_active == True:
                    child = part
                    break
            else:
                return
            for parent in self.parts:
                if parent == child:
                    pass
                else:
                    bot_tol = 10
                    top_tol = 20
                    left_tol = 30
                    right_tol = 30
                    if parent.top_conn == False:
                        bot_check = ((parent.rect.top + bot_tol) >= child.rect.bottom)
                        top_check = ((parent.rect.top - top_tol) <= child.rect.bottom)
                        left_check = ((parent.rect.left + left_tol) >= child.rect.left)
                        right_check = ((parent.rect.right - right_tol) <= child.rect.right)
                        snap_tol = bot_check and top_check and left_check and right_check
                        if snap_tol:
                            parent.top_conn = True
                            child.snap_parent = parent
                            child.snap_to_object(1)
                    if parent.btm_conn == False:
                        bot_check = ((parent.rect.bottom + bot_tol) >= child.rect.top)
                        top_check = ((parent.rect.bottom - top_tol) <= child.rect.top)
                        left_check = ((parent.rect.left + left_tol) >= child.rect.left)
                        right_check = ((parent.rect.right - right_tol) <= child.rect.right)
                        snap_tol = bot_check and top_check and left_check and right_check
                        if snap_tol:
                            parent.btm_conn = True
                            child.snap_parent = parent
                            child.snap_to_object(0)

    def update(self, display_screen):
        self.player_input()
        self.parts.draw(display_screen)
        pygame.draw.circle(display_screen, (255, 0, 0), (self.cg_location[0], self.cg_location[1]), 1)
        self.parts.update()

class button_parts(pygame.sprite.Sprite):
    def __init__(self, image, pos, properties):
        super().__init__()

        mouse_pos = pygame.mouse.get_pos()
        self.image = pygame.image.load(image).convert_alpha()
        self.trans_rect = self.get_visible_rect()
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1]))
        self.mouse_follow_active = False
        self.prev_mouse_pos = mouse_pos
        self.snap = False
        self.alr_snap = False
        self.snap_parent = None

        self.top_conn = False
        self.btm_conn = False

        self.relative_struct_real = (0, 0)

        self.cg_location = self.mass_location(properties)
        self.moment_of_inertia = self.moment_of_inertia_calc(properties)
        self.mass = properties['mass']

        self.mask = pygame.mask.from_surface(self.image)

    def mass_location(self, properties):
        location = self.trans_rect
        x = location[0] + location[2]/2
        y = location[1] + location[3]/2
        return [x, y , properties['mass']]

    def moment_of_inertia_calc(self, properties):
        I = 0

        area_pix_sqrt_to_m_sqrt = 16 / 4096
        volume_pixel = 0
        width, height = self.image.get_size()
        for x in range(width):
            for y in range(height):
                pixel_color = self.image.get_at((x, y))
                if pixel_color.a > 0:
                    volume_pixel += 1

        density = properties['mass'] / volume_pixel

        for x in range(width):
            for y in range(height):
                pixel_color = self.image.get_at((x, y))
                if pixel_color.a > 0:
                    r_pixel_sqrt = ((self.cg_location[0] - x) ** 2) + ((self.cg_location[1] - y) ** 2 )
                    dA_pixel = 1
                    dm = density * dA_pixel
                    I += r_pixel_sqrt * dm
        I *= area_pix_sqrt_to_m_sqrt # convert to pixels to m
        return I

    def follow_mouse(self):
        current_mouse_pos = pygame.mouse.get_pos()
        if self.mouse_follow_active:
            self.rect.move_ip(current_mouse_pos[0] - self.prev_mouse_pos[0],
                            current_mouse_pos[1] - self.prev_mouse_pos[1])
        self.prev_mouse_pos = current_mouse_pos

    def snap_to_object(self, side):
        if self.alr_snap == False:
            # side == 0 is bot and side == 1 is top
            if side == 0:
                location = self.snap_parent.rect.bottomleft
                btm_parent_offset = (0, self.snap_parent.rect[3] - (self.snap_parent.trans_rect[1] + self.snap_parent.trans_rect[3]))
                top_child_offset = (0, self.trans_rect[1])
                self.rect.topleft = (location[0] - btm_parent_offset[0] - top_child_offset[0], location[1] - btm_parent_offset[1] - top_child_offset[1])
                self.alr_snap = True
            else:
                location = self.snap_parent.rect.topleft
                top_parent_offset = (0, self.snap_parent.trans_rect[1])
                btm_child_offset = (0, self.rect[3] - (self.trans_rect[1] + self.trans_rect[3]))
                self.rect.bottomleft = (location[0] + top_parent_offset[0] + btm_child_offset[0], location[1] + top_parent_offset[1] + btm_child_offset[1])
                self.alr_snap = True
        pass

    def get_visible_rect(self):
        rect = self.image.get_rect()
        mask = pygame.mask.from_surface(self.image)
        non_transparent_pixels = mask.outline()

        # Find the minimum bounding box of the non-transparent pixels
        min_x = min(pixel[0] for pixel in non_transparent_pixels)
        max_x = max(pixel[0] for pixel in non_transparent_pixels)
        min_y = min(pixel[1] for pixel in non_transparent_pixels)
        max_y = max(pixel[1] for pixel in non_transparent_pixels)
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Adjust the position of the rectangle to match the sprite's position
        x, y = rect.topleft
        return pygame.Rect(x + min_x, y + min_y, width, height)

    def update(self):
        self.follow_mouse()

class VABButton():
    def __init__(self, image_name, background_name, name, image_state='', background_state=''):
        # Image Variables
        self.image_name = image_name
        self.image_state = image_state
        self.image = Image(f'{image_name}{image_state}.png')

        # Background Variables
        self.background_name = background_name
        self.background_state = background_state
        self.background = Image(f'{background_name}{background_state}.png')

        # Other variables
        self.state = 0
        self.name = name
        self.debounce_threshold = 250
        self.last_update_time = 0

    def state_flip(self):
        if self.state == 1:
            self.state = 0
        elif self.state == 0:
            self.state = 1
        else:
            raise ValueError("State should only be zero or one")

    def set_image_position(self, x, y, loc='center'):
        self.image.set_position(x, y, loc)

    def set_background_position(self, x, y, loc='center'):
        self.background.set_position(x, y, loc)

    def set_position(self, x, y, loc='center'):
        self.set_image_position(x, y, loc)
        self.set_background_position(x, y, loc)

    def set_image_relative_position(self, x, y):
        temp_x = self.image.rect.center[0]
        temp_y = self.image.rect.center[1]
        self.image.set_position(x + temp_x, y + temp_y)

    def set_image_state(self, state):
        self.image_state = state
        self.image.set_image(f'{self.image_name}{self.image_state}.png')

    def set_background_state(self, state):
        self.background_state = state
        self.background.set_image(f'{self.background_name}{self.background_state}.png')

    def set_image_scale_bounds(self, min, max):
        self.image.scale.set_bounds(min, max)

    def set_image_scale_speed(self, speed):
        self.image.scale.set_speed(speed)

    def set_bg_scale_bounds(self, min, max):
        self.background.scale.set_bounds(min, max)

    def set_state(self, state):
        self.set_image_state(state)
        self.set_background_state(state)

    def check_for_hover(self, mouse_position):
        local_x = mouse_position[0] - self.background.rect.x
        local_y = mouse_position[1] - self.background.rect.y
        if self.background.rect.collidepoint(mouse_position[0], mouse_position[1]):
            if self.background.mask.get_at((local_x, local_y)):
                return True
        return False

    def check_for_debounce(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_update_time > self.debounce_threshold):
            self.last_update_time = current_time
            return True
        return False

    @abstractmethod
    def draw(self, display_surface, mouse_position):
        pass

class SubCategoryButton(VABButton):
    def __init__(self, image_name, background_name, name):
        super().__init__(image_name, background_name, name, background_state='low')

        with open('data/part_label.json', 'r') as file:
            data = json.load(file)
        self.data = data[name]
        if data[name]['type'] == "pod":
            self.label = PodVABPartInformationLabel(name, self.data)
        elif data[name]['type'] == "engine":
            self.label = EngineVABPartInformationLabel(name, self.data)
        elif data[name]['type'] == "tank":
            self.label = TankVABPartInformationLabel(name, self.data)
        elif data[name]['type'] == "heat_shield":
            self.label = HeatShieldVABPartInformationLabel(name, self.data)
        elif data[name]['type'] == "decoupler":
            self.label = DecouplerVABPartInformationLabel(name, self.data)
        elif data[name]['type'] == "fins":
            self.label = FinsVABPartInformationLabel(name, self.data)
        else:
            self.label = VABPartInformationLabel(name, self.data)

    def draw(self, display_surface, mouse_position):
        # if there is hover and change color based on hover
        if self.check_for_hover(mouse_position):
            if self.background_state == 'low':
                self.background_state = 'high'
                self.background.set_image(f'{self.background_name}{self.background_state}.png')
            self.image.scale.update()
        else:
            if self.background_state == 'high':
                self.background_state = 'low'
                self.background.set_image(f'{self.background_name}{self.background_state}.png')
                self.image.scale.current = 1.0

        self.background.draw(display_surface)
        self.image.draw(display_surface)

class VABButtonWithLabel(VABButton):
    def __init__(self, image_name, background_name, name, image_state='', background_state=''):
        super().__init__(image_name, background_name, name, image_state=image_state, background_state=background_state)
        self.label = LabelFollower(name)

    def draw(self, display_surface, mouse_position):
        self.background.draw(display_surface)
        self.image.draw(display_surface)

class MoneySymmetryMenu():
    def __init__(self, player):
        file_location = 'graphics/ui/vab'
        self.player = player
        self.overlay = Image(f'{file_location}/money_and_symmetry.png', loc='bottomleft')
        self.money_counter = TextBox(f"{self.player.money}", 'font/Pixeltype.ttf', '#6abe30', 35, 255)
        self.weight_center = VABButtonWithLabel(f'{file_location}/weight', f'{file_location}/weight_bg_', 'Center of Mass', background_state='low')
        self.thrust_center = VABButtonWithLabel(f'{file_location}/thruster', f'{file_location}/thruster_bg_', 'Thruster Force Center', background_state='low')
        self.aero_center = VABButtonWithLabel(f'{file_location}/aerocenter', f'{file_location}/aerocenter_bg_', 'Aerodynamic Center', background_state='low')
        self.symmetry = VABButtonWithLabel(f'{file_location}/symmetry_single', f'{file_location}/symmetry_bg_', 'Symmetry', background_state='low')

        info = pygame.display.Info()
        self.weight_center.set_position(0, info.current_h, loc='bottomleft')
        self.thrust_center.set_position(0, info.current_h, loc='bottomleft')
        self.aero_center.set_position(0, info.current_h, loc='bottomleft')
        self.symmetry.set_position(0, info.current_h, loc='bottomleft')
        self.money_counter.set_position_top_right(195, 655)
        self.buttons = [self.weight_center, self.thrust_center,
                        self.aero_center]

        # Debounce Variables
        self.last_press_time = [0]
        self.debounce_time = 250

    def draw(self, display_surface, mouse_position, mouse_button):
        self.overlay.draw(display_surface)
        for button in self.buttons:
            if PygameUtils.check_for_input(mouse_button, mouse_position, button.background, self.last_press_time, self.debounce_time):
                button.state_flip()
            elif PygameUtils.check_for_hover(mouse_position, button.background):
                button.set_background_state('med')
            else:
                if button.state == 1:
                    button.set_background_state('high')
                else:
                    button.set_background_state('low')
            button.draw(display_surface, mouse_position)
        if PygameUtils.check_for_input(mouse_button, mouse_position, self.symmetry.background, self.last_press_time, self.debounce_time):
            file_location = 'graphics/ui/vab'
            if self.symmetry.image.image_file == f'{file_location}/symmetry_single.png':
                self.symmetry.image.set_image(f'{file_location}/symmetry_two.png')
            else:
                self.symmetry.image.set_image(f'{file_location}/symmetry_single.png')
        elif PygameUtils.check_for_hover(mouse_position, self.symmetry.background):
            self.symmetry.set_background_state('med')
        else:
            self.symmetry.set_background_state('low')
        self.symmetry.draw(display_surface, mouse_position)
        self.money_counter.update_text(f"{int(self.player.money)}")
        self.money_counter.set_position_top_right(195, 655)
        self.money_counter.draw(display_surface)

class SideCategoryButton(VABButton):
    def __init__(self, image_name, background_name, name):
        super().__init__(image_name, background_name, name, image_state='low', background_state='low')
        self.label = LabelFollower(name)

    def draw(self, display_surface, mouse_position):
        # If there is hover and change color based on hover
        if self.check_for_hover(mouse_position):
            if self.background_state == 'low':
                self.background_state = 'med'
                self.background.set_image(f'{self.background_name}{self.background_state}.png')
        else:
            if self.background_state == 'med':
                self.background_state = 'low'
                self.background.set_image(f'{self.background_name}{self.background_state}.png')

        self.background.draw(display_surface)
        self.image.draw(display_surface)

class NoSurroundingButton():
    def __init__(self, text, font, size):
        self.color = '#f7f7f7'     # Default to yellow
        self.highlight = '#f4fc03' # Default to white
        self.font = pygame.font.Font(font, size)
        self.font_surface = self.font.render(text, False, self.color)
        self.font_rect = self.font_surface.get_rect(center=(500, 350))
        self.text = text
        self.clickable = False

    def set_color(self, color):
        self.color = color
        self.font_surface = self.font.render(self.text, False, self.color)

    def set_highlight(self, highlight):
        self.highlight = highlight

    def set_position(self, x, y):
        self.font_rect.center = (x, y)
        self.font_rect = self.font_surface.get_rect(center=self.font_rect.center)

    def check_for_input(self, mouse_position, actions):
        if (self.font_rect.collidepoint(mouse_position) and pygame.mouse.get_pressed()[0]) and mouse_position[0] in range(self.font_rect.left, self.font_rect.right) and (mouse_position[1] in range(self.font_rect.top, self.font_rect.bottom)):
            for act in actions:
                act()

    def change_color(self, mouse_position):
        if mouse_position[0] in range(self.font_rect.left, self.font_rect.right) and mouse_position[1] in range(self.font_rect.top, self.font_rect.bottom):
            self.font_surface = self.font.render(self.text, False, self.color)
        else:
            self.font_surface = self.font.render(self.text, False, self.highlight)

    def update(self, mouse_position, actions=[]):
        self.change_color(mouse_position)
        self.check_for_input(mouse_position, actions)


class Image(pygame.sprite.Sprite):
    def __init__(self, image_file, loc='center'):
        super().__init__()
        # Load the image and set up initial properties
        self.image_file = image_file
        self.og_image = pygame.image.load(image_file).convert_alpha()
        self.image = self.og_image
        self.mask = pygame.mask.from_surface(self.image)
        self.set_location(loc)

        # Dimension Variables
        self.og_width = self.rect.width
        self.og_height = self.rect.height

        # Scaling Variables
        self.scale = ImageScale()
        self.scale.set_bounds(0.5, 0.5)

    def set_location(self, loc):
        if loc == 'center':
            self.rect = self.image.get_rect(center=(0, 0))
        elif loc == 'topleft':
            self.rect = self.image.get_rect(topleft=(0, 0))
        elif loc == 'bottomleft':
            info = pygame.display.Info()
            self.rect = self.image.get_rect(bottomleft=(0, info.current_h))
        else:
            raise ValueError("Invalid location specified. Use 'center' or 'topleft' or 'bottomleft")

    def set_position(self, x, y, loc='center'):
        if loc == 'center':
            self.rect.center = (x, y)
        elif loc == 'topleft':
            self.rect.topleft = (x, y)
        elif loc == 'bottomleft':
            self.rect.bottomleft = (x, y)
        else:
            raise ValueError("Invalid location specified. Use 'center' or 'topleft' or 'bottomleft")

    def set_image(self, image_file):
        self.og_image = pygame.image.load(image_file).convert_alpha()
        self.image = self.og_image
        self.image_file = image_file

    def draw(self, display_surface):
        scaled_width = int(self.og_width * self.scale.current)
        scaled_height = int(self.og_height * self.scale.current)

        self.image = pygame.transform.scale(self.og_image, (scaled_width, scaled_height))
        self.rect = self.image.get_rect(center=self.rect.center)
        display_surface.blit(self.image, self.rect)

class SurfaceImage(Image):
    def __init__(self, size=(200,200), color=(70, 70, 70, 200), loc='center'):
        self.og_image = pygame.Surface(size, pygame.SRCALPHA)
        self.og_image.fill(color)
        self.image = self.og_image
        self.mask = pygame.mask.from_surface(self.image)
        self.set_location(loc)

        # Dimension Variables
        self.og_width = self.rect.width
        self.og_height = self.rect.height

        # Scaling Variables
        self.scale = ImageScale()
        self.scale.set_bounds(0.5, 0.5)

class ImageScale():
    def __init__(self):
        self.current = 1.0
        self.min = 0.5
        self.max = 1.5
        self.direction = 1
        self.speed = 0.1

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.direction = direction

    def change_direction(self):
        self.direction *= -1

    def set_bounds(self, min, max):
        self.min = min
        self.max = max

    def update(self):
        if (self.current <= self.min) or (self.current >= self.max):
            self.change_direction()
        self.current += self.direction * self.speed
