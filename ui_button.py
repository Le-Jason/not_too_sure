import pygame
from rocket import *
from data.part_data import *
from rocket_parts import *
import json

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

class vab_ui_button:
    def __init__(self):
        self.label = []
        self.rec = []
        self.rec_rect = []

        self.background = pygame.Surface((275, 720), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.background.fill((70, 70, 70, 200))
        self.background_rect = self.background.get_rect(topleft=(0, 0))
        self.object_1 = rocket_part_group()

        self.debounce_threshold = 500
        self.last_update_time = 0

    def add(self, title, pos, size):
        self.label.append(title)
        self.rec.append(pygame.Surface((size[0], size[1]), pygame.SRCALPHA))
        self.rec[-1].fill((255, 0, 0, 0))
        self.rec_rect.append(self.rec[-1].get_rect(topleft=(pos[0], pos[1])))

    def draw(self, display_screen):
        for i in range(len(self.rec)):
            display_screen.blit(self.rec[i], self.rec_rect[i])

    def click(self, mouse_pos, display_screen, current_look):
        rocket_image = None
        for i in range(len(self.label)):
            if (self.rec_rect[i].collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])) or (current_look == self.label[i]):
                display_screen.blit(self.background, self.background_rect)
                current_look = self.label[i]
                current_time = pygame.time.get_ticks()

                if current_look == 'Command Pod':
                    mk1 = pygame.image.load('graphics/spites/commander_pod.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(77, 85))
                    mk2 = pygame.image.load('graphics/part_holder.png').convert_alpha()
                    mk2_rec = mk2.get_rect(topleft=(70, 80))
                    mk3 = pygame.image.load('graphics/part_holder.png').convert_alpha()
                    mk3_rec = mk3.get_rect(topleft=(170, 80))
                    # display_screen.blit(mk2, mk2_rec)
                    # display_screen.blit(mk3, mk3_rec)
                    # display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            mk1_rec = mk1.get_rect(topleft=(80, 80))
                            self.object_1.add('graphics/spites/commander_pod.png', mk1_rec, mk1_prop, 'CMD')
                            self.last_update_time = current_time
                elif current_look == 'Fuel Tank':
                    mk1 = pygame.image.load('graphics/spites/small_fuel_tank.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/small_fuel_tank.png', mk1_rec, fuel_tank_prop, 'FUEL')
                            self.last_update_time = current_time

                elif current_look == 'Rocket Engine':
                    mk1 = pygame.image.load('graphics/spites/small_rocket_engine.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/small_rocket_engine.png', mk1_rec, rocket_engine_prop, 'ENG')
                            self.last_update_time = current_time

                elif current_look == 'Controls':
                    mk1 = pygame.image.load('graphics/spites/decoupler.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/decoupler.png', mk1_rec, decoupler_prop, 'DECOUPLER')
                            self.last_update_time = current_time

                    mk2 = pygame.image.load('graphics/spites/heat_shield.png').convert_alpha()
                    mk2_rec = mk2.get_rect(topleft=(80 + 100, 80))
                    display_screen.blit(mk2, mk2_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk2_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/heat_shield.png', mk2_rec, heat_shield_prop, 'HEAT')
                            self.last_update_time = current_time

                elif current_look == 'Miscellaneous':
                    mk1 = pygame.image.load('graphics/spites/parachute.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/parachute.png', mk1_rec, parachute_prop, 'CHUTES')
                            self.last_update_time = current_time

                elif current_look == 'Launch':
                    rocket_image = self.object_1

        self.object_1.update(display_screen)

        return current_look, rocket_image

class SurroundingImageButton2(pygame.sprite.Sprite):
    def __init__(self, image_name, surrounding_image_name, name):
        super().__init__()
        # Image and Surrounding Image Variables
        self.surrounding_state = 'low'
        self.image_name = image_name
        self.surrounding_image_name = surrounding_image_name

        # Images Rect for Image
        self.og_image = pygame.image.load(f'{image_name}.png').convert_alpha()
        self.image = self.og_image
        self.rect = self.image.get_rect(center=(0, 0))

        # Images Rect for Background
        self.og_bg_image = pygame.image.load(f'{surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
        self.bg_image = self.og_bg_image
        self.bg_rect = self.bg_image.get_rect(center=(0, 0))
        self.bg_mask = pygame.mask.from_surface(self.bg_image)

        # Scale variables for Image
        self.og_image_width = self.rect.width
        self.og_image_height = self.rect.height
        self.scale_image = 1.0
        self.scale_image_min = 0.5
        self.scale_image_max = 1.5
        self.scale_image_direction = -1
        self.scale_image_speed = 0.1

        # Scale variables for Background
        self.og_bg_width = self.bg_rect.width
        self.og_bg_height = self.bg_rect.height
        self.scale_bg = 1.0
        self.scale_bg_min = 0.5
        self.scale_bg_max = 1.5

        # Part Label
        with open('data/part_label.json', 'r') as file:
            data = json.load(file)
        self.data = data[name]
        if data[name]['type'] == "pod":
            self.label = PodPartLabel(name, self.data)
        elif data[name]['type'] == "engine":
            self.label = EnginePartLabel(name, self.data)
        elif data[name]['type'] == "tank":
            self.label = TankPartLabel(name, self.data)
        elif data[name]['type'] == "heat_shield":
            self.label = HeatShieldPartLabel(name, self.data)
        elif data[name]['type'] == "decoupler":
            self.label = DecouplerPartLabel(name, self.data)
        else:
            self.label = PartLabel(name, self.data)

        # Part
        self.part = RocketPart(name)

    def set_image_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_image_relative_position(self, x, y):
        temp_x = self.rect.center[0]
        temp_y = self.rect.center[1]
        self.rect.center = (x + temp_x, y + temp_y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_background_position(self, x, y):
        self.bg_rect.center = (x, y)
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.bg_rect.center = (x, y)
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

    def set_image_state(self, state):
        self.image_state = state
        self.og_image = pygame.image.load(f'{self.image_name}{self.image_state}.png').convert_alpha()

    def set_image_scale_bounds(self, min, max):
        self.scale_image_min = min
        self.scale_image_max = max
    
    def set_image_scale_speed(self, speed):
        self.scale_image_speed = speed

    def set_background_state(self, state):
        self.surrounding_state = state
        self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()

    def set_bg_scale_bounds(self, min, max):
        self.scale_bg_min = min
        self.scale_bg_max = max

    def set_state(self, state):
        self.set_image_state(state)
        self.set_background_state(state)

    def check_for_hover(self, mouse_position):
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)):
                if self.surrounding_state == 'low':
                    self.surrounding_state = 'high'
                    self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
                if (self.scale_image <= self.scale_image_min) or (self.scale_image >= self.scale_image_max):
                    self.scale_image_direction *= -1
                self.scale_image += self.scale_image_direction*self.scale_image_speed

        else:
            if self.surrounding_state == 'high':
                self.surrounding_state = 'low'
                self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
                self.scale_image = 1.0

    def check_for_input(self, mouse_position, group):
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)) and pygame.mouse.get_pressed()[0]:
                group.add(self.part)

    def update(self, mouse_position, group):
        self.check_for_hover(mouse_position)
        self.check_for_input(mouse_position, group)

    def draw(self, display_surface):
        self.image = pygame.transform.scale(self.og_image, (self.og_image_width * self.scale_image, self.og_image_height * self.scale_image))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.bg_image = pygame.transform.scale(self.og_bg_image, (self.og_bg_width * self.scale_bg, self.og_bg_height * self.scale_bg))
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

        display_surface.blit(self.bg_image, self.bg_rect)
        display_surface.blit(self.image, self.rect)

    def draw_hover(self, display_surface):
        mouse_position = pygame.mouse.get_pos()
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)):
                self.label.draw(display_surface, mouse_position)

class SurroundingImageButton(pygame.sprite.Sprite):
    def __init__(self, image_name, surrounding_image_name, name):
        super().__init__()
        # Image and Surrounding Image Variables
        self.image_state = 'low'
        self.surrounding_state = 'low'
        self.image_name = image_name
        self.surrounding_image_name = surrounding_image_name
        
        # Images Rect for Image
        self.og_image = pygame.image.load(f'{image_name}{self.image_state}.png').convert_alpha()
        self.image = self.og_image
        self.rect = self.image.get_rect(center=(0, 0))

        # Images Rect for Background
        self.og_bg_image = pygame.image.load(f'{surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
        self.bg_image = self.og_bg_image
        self.bg_rect = self.bg_image.get_rect(center=(0, 0))
        self.bg_mask = pygame.mask.from_surface(self.bg_image)

        # Scale variables for Image
        self.og_image_width = self.rect.width
        self.og_image_height = self.rect.height
        self.scale_image = 1.0

        # Scale variables for Background
        self.og_bg_width = self.bg_rect.width
        self.og_bg_height = self.bg_rect.height
        self.scale_bg = 1.0

        self.parts = []
        self.label = LabelFollower(name)

    def set_image_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_background_position(self, x, y):
        self.bg_rect.center = (x, y)
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.bg_rect.center = (x, y)
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

    def set_image_state(self, state):
        self.image_state = state
        self.og_image = pygame.image.load(f'{self.image_name}{self.image_state}.png').convert_alpha()

    def set_background_state(self, state):
        self.surrounding_state = state
        self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()

    def set_state(self, state):
        self.set_image_state(state)
        self.set_background_state(state)

    def add_parts(self, parts):
        self.parts.append(parts)

    def check_for_hover(self, mouse_position):
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)):
                if self.surrounding_state == 'low':
                    self.surrounding_state = 'med'
                    self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
        else:
            if self.surrounding_state == 'med':
                self.surrounding_state = 'low'
                self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()

    def check_for_input(self, mouse_position):
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)) and pygame.mouse.get_pressed()[0]:
                self.surrounding_state = 'high'
                self.og_bg_image = pygame.image.load(f'{self.surrounding_image_name}{self.surrounding_state}.png').convert_alpha()
                self.image_state = 'high'
                self.og_image = pygame.image.load(f'{self.image_name}{self.image_state}.png').convert_alpha()
    
    def update(self, mouse_position):
        self.check_for_hover(mouse_position)
        self.check_for_input(mouse_position)

    def update_parts(self, mouse_position, display_surface, group):
        if self.image_state == 'high':
            # Draw the part boxes
            for part in self.parts:
                part.update(mouse_position, group)
                part.draw(display_surface)

            # Draw the label if its hovered over
            for part in self.parts:
                part.draw_hover(display_surface)

    def draw_label(self, mouse_position, display_surface):
        # This is for the label
        if self.bg_rect.collidepoint(mouse_position[0], mouse_position[1]):
            local_x = mouse_position[0] - self.bg_rect.x
            local_y = mouse_position[1] - self.bg_rect.y
            if self.bg_mask.get_at((local_x, local_y)):
                self.label.draw(display_surface, mouse_position)

    def draw(self, display_surface):
        self.image = pygame.transform.scale(self.og_image, (self.og_image_width * self.scale_image, self.og_image_height * self.scale_image))
        self.rect = self.image.get_rect(center=self.rect.center)

        self.bg_image = pygame.transform.scale(self.og_bg_image, (self.og_bg_width * self.scale_bg, self.og_bg_height * self.scale_bg))
        self.bg_rect = self.bg_image.get_rect(center=self.bg_rect.center)

        display_surface.blit(self.bg_image, self.bg_rect)
        display_surface.blit(self.image, self.rect)

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


class PartLabel():
    def __init__(self, text, data):
        # Big background
        self.background = pygame.Surface((265, 230), pygame.SRCALPHA) # Create a surface with per-pixel alpha
        self.background.fill((100, 100, 100, 255))
        self.background_rect = self.background.get_rect(topleft=(0, 0))

        # Setting up image
        self.image = pygame.image.load(data['image']).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))

        # Setting up image background
        self.image_background = pygame.Surface((75, 75), pygame.SRCALPHA) # Create a surface with per-pixel alpha
        self.image_background.fill((50, 50, 50, 255))
        self.image_background_rect = self.image_background.get_rect(topleft=(0, 0))

        # Setting up key info
        self.info_background = pygame.Surface((175, 75), pygame.SRCALPHA) # Create a surface with per-pixel alpha
        self.info_background.fill((50, 50, 50, 255))
        self.info_background_rect = self.info_background.get_rect(topleft=(0, 0))

        # Setting up the info text
        self.info_text_1 = LabelText(f"Mass: {data['mass']} t", 'font/Pixeltype.ttf', '#4dfed1', 15)
        self.info_text_2 = LabelText(f"Tolerance: {data['Tolerance Impact']} m/s Impact", 'font/Pixeltype.ttf', '#4dfed1', 15)
        self.info_text_3 = LabelText(f"Tolerance: {data['Tolerance Pressure']} kPA Pressure", 'font/Pixeltype.ttf', '#4dfed1', 15)
        self.info_text_4 = LabelText(f"Max. Temp. Skin: {data['Max Temperature']} K", 'font/Pixeltype.ttf', '#4dfed1', 15)

        # Setting up manufacturer background
        self.manuf_background = pygame.Surface((255, 30), pygame.SRCALPHA) # Create a surface with per-pixel alpha
        self.manuf_background.fill((150, 150, 150, 255))
        self.manuf_background_rect = self.manuf_background.get_rect(topleft=(0, 0))

        # Setting up manufacturer text
        self.manuf_text_1 = LabelText(f"Manufacturer:", 'font/Pixeltype.ttf', '#4dfed1', 15)
        self.manuf_text_2 = LabelText(f"{data['Manufacturer']}", 'font/Pixeltype.ttf', '#4dfed1', 15)

        # Setting up description background
        self.description_background = pygame.Surface((255, 80), pygame.SRCALPHA) # Create a surface with per-pixel alpha
        self.description_background.fill((50, 50, 50, 255))
        self.description_background_rect = self.description_background.get_rect(topleft=(0, 0))

        # Setting up description text
        self.description_text_1 = TextBox(f"{data['Description']}", 'font/Pixeltype.ttf', '#93c47d', 15, 255)

        # Setting up cost text
        self.cost_text = TextBox(f"Cost: ${data['Cost']}", 'font/Pixeltype.ttf', '#f4fc03', 15, 255)

        # Texts Setup
        self.text_title = LabelText(text, 'font/Pixeltype.ttf', '#f4fc03', 20)

    def set_position(self, x, y):
        self.background_rect.topleft = (x + 10, y + 10)
        self.background_rect = self.background.get_rect(topleft=self.background_rect.topleft)

        self.image_background_rect.topleft = (self.background_rect.topleft[0] + 5, self.background_rect.topleft[1] + 20)
        self.image_background_rect = self.image_background.get_rect(topleft=self.image_background_rect.topleft)

        self.rect.center = (self.image_background_rect.center[0], self.image_background_rect.center[1])
        self.rect = self.image.get_rect(center=self.rect.center)

        self.info_background_rect.topleft = (self.image_background_rect.topright[0] + 5, self.image_background_rect.topright[1])
        self.info_background_rect = self.info_background.get_rect(topleft=self.info_background_rect.topleft)

        self.manuf_background_rect.topleft = (self.image_background_rect.bottomleft[0], self.image_background_rect.bottomleft[1] + 5)
        self.manuf_background_rect = self.manuf_background.get_rect(topleft=self.manuf_background_rect.topleft)

        self.description_background_rect.topleft = (self.manuf_background_rect.bottomleft[0], self.manuf_background_rect.bottomleft[1])
        self.description_background_rect = self.description_background.get_rect(topleft=self.description_background_rect.topleft)
        
        self.info_text_1.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_background_rect.topleft[1] + 5)
        self.info_text_2.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_1.rect.topleft[1] + 10)
        self.info_text_3.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_2.rect.topleft[1] + 10)
        self.info_text_4.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_3.rect.topleft[1] + 10)

        self.manuf_text_1.set_position_top_left(self.manuf_background_rect.topleft[0] + 5, self.manuf_background_rect.topleft[1] + 5)
        self.manuf_text_2.set_position_top_left(self.manuf_background_rect.topleft[0] + 5, self.manuf_text_1.rect.topleft[1] + 10)

        self.description_text_1.set_position_top_left(self.description_background_rect.topleft[0] + 5, self.description_background_rect.topleft[1] + 5)

        self.cost_text.set_position_top_left(self.description_background_rect.bottomleft[0] + 5, self.description_background_rect.bottomleft[1] + 5)

        self.text_title.set_position_top_left(self.background_rect.topleft[0] + 5, self.background_rect.topleft[1] + 5)

    def draw(self, display_surface, mouse_position):
        local_x = mouse_position[0]
        local_y = mouse_position[1]
        self.set_position(local_x, local_y)
        display_surface.blit(self.background, self.background_rect)
        display_surface.blit(self.image_background, self.image_background_rect)
        display_surface.blit(self.image, self.rect)
        display_surface.blit(self.info_background, self.info_background_rect)
        display_surface.blit(self.manuf_background, self.manuf_background_rect)
        display_surface.blit(self.description_background, self.description_background_rect)
        self.info_text_1.draw(display_surface)
        self.info_text_2.draw(display_surface)
        self.info_text_3.draw(display_surface)
        self.info_text_4.draw(display_surface)
        self.manuf_text_1.draw(display_surface)
        self.manuf_text_2.draw(display_surface)
        self.description_text_1.draw(display_surface)
        self.cost_text.draw(display_surface)
        self.text_title.draw(display_surface)

class PodPartLabel(PartLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Crew capacity: {data['Crew Capacity']}", 'font/Pixeltype.ttf', '#4dfed1', 15)
        self.info_text_6 = LabelText(f"Electric Charge: {data['Electric Charge']}", 'font/Pixeltype.ttf', '#93c47d', 15)
        self.info_text_7 = LabelText(f"Monopropellant: {data['Monopropellant']}", 'font/Pixeltype.ttf', '#93c47d', 15)

    def set_position(self, x, y):
        # Do parent set_position
        super().set_position(x, y)
        self.info_text_5.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_4.rect.topleft[1] + 10)
        self.info_text_6.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_5.rect.topleft[1] + 10)
        self.info_text_7.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_6.rect.topleft[1] + 10)

    def draw(self, display_surface, mouse_position):
        # Do parent draw
        super().draw(display_surface, mouse_position)
        self.info_text_5.draw(display_surface)
        self.info_text_6.draw(display_surface)
        self.info_text_7.draw(display_surface)

class EnginePartLabel(PartLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Thrust (ASL): {data['Thrust (ASL)']} kN", 'font/Pixeltype.ttf', '#93c47d', 15)
        self.info_text_6 = LabelText(f"Thrust (Vac.): {data['Thrust (Vac)']} kN", 'font/Pixeltype.ttf', '#93c47d', 15)

    def set_position(self, x, y):
        # Do parent set_position
        super().set_position(x, y)
        self.info_text_5.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_4.rect.topleft[1] + 20)
        self.info_text_6.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_5.rect.topleft[1] + 10)

    def draw(self, display_surface, mouse_position):
        # Do parent draw
        super().draw(display_surface, mouse_position)
        self.info_text_5.draw(display_surface)
        self.info_text_6.draw(display_surface)

class TankPartLabel(PartLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Liquid Fuel: {data['Liquid Fuel']}", 'font/Pixeltype.ttf', '#93c47d', 15)
        self.info_text_6 = LabelText(f"Oxidizer: {data['Oxidizer']}", 'font/Pixeltype.ttf', '#93c47d', 15)

    def set_position(self, x, y):
        # Do parent set_position
        super().set_position(x, y)
        self.info_text_5.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_4.rect.topleft[1] + 20)
        self.info_text_6.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_5.rect.topleft[1] + 10)

    def draw(self, display_surface, mouse_position):
        # Do parent draw
        super().draw(display_surface, mouse_position)
        self.info_text_5.draw(display_surface)
        self.info_text_6.draw(display_surface)

class HeatShieldPartLabel(PartLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Ejection Force: {data['Ejection Force']}", 'font/Pixeltype.ttf', '#93c47d', 15)
        self.info_text_6 = LabelText(f"Ablator: {data['Ablator']}", 'font/Pixeltype.ttf', '#93c47d', 15)

    def set_position(self, x, y):
        # Do parent set_position
        super().set_position(x, y)
        self.info_text_5.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_4.rect.topleft[1] + 20)
        self.info_text_6.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_5.rect.topleft[1] + 10)

    def draw(self, display_surface, mouse_position):
        # Do parent draw
        super().draw(display_surface, mouse_position)
        self.info_text_5.draw(display_surface)
        self.info_text_6.draw(display_surface)

class DecouplerPartLabel(PartLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Ejection Force: {data['Ejection Force']}", 'font/Pixeltype.ttf', '#93c47d', 15)

    def set_position(self, x, y):
        # Do parent set_position
        super().set_position(x, y)
        self.info_text_5.set_position_top_left(self.info_background_rect.topleft[0] + 5, self.info_text_4.rect.topleft[1] + 20)

    def draw(self, display_surface, mouse_position):
        # Do parent draw
        super().draw(display_surface, mouse_position)
        self.info_text_5.draw(display_surface)

class LabelFollower():
    def __init__(self, text):
        # Setting up the middle part
        self.background = pygame.Surface((len(text) * 8, 20), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.background.fill((50, 50, 50, 255))
        self.background_rect = self.background.get_rect(topleft=(0, 0))

        # Setting up the outside part
        self.foreground = pygame.Surface((len(text) * 8 + 5, 20 + 5), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.foreground.fill((200, 200, 200, 255))
        self.foreground_rect = self.foreground.get_rect(topleft=(0, 0))

        self.foreground_1 = pygame.Surface((len(text) * 8 + 2, 20 + 2), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.foreground_1.fill((10, 10, 10, 255))
        self.foreground_1_rect = self.foreground_1.get_rect(topleft=(0, 0))

        self.foreground_2 = pygame.Surface((len(text) * 8 + 7, 20 + 7), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.foreground_2.fill((10, 10, 10, 255))
        self.foreground_2_rect = self.foreground_2.get_rect(topleft=(0, 0))

        # Texts
        self.color = '#f4fc03'     # Default to yellow
        font = 'font/Pixeltype.ttf'
        self.font = pygame.font.Font(font, 20)
        self.font_surface = self.font.render(text, False, self.color)
        self.font_rect = self.font_surface.get_rect(center=(500, 350))
        self.text = text

    def set_position(self, x, y):
        self.background_rect.center = (x + (self.background_rect.width/2 + 10), y + (self.background_rect.height))
        self.background_rect = self.background.get_rect(center=self.background_rect.center)

        self.foreground_rect.center = (x + (self.background_rect.width/2 + 10), y + (self.background_rect.height))
        self.foreground_rect = self.foreground.get_rect(center=self.foreground_rect.center)

        self.foreground_1_rect.center = (x + (self.background_rect.width/2 + 10), y + (self.background_rect.height))
        self.foreground_1_rect = self.foreground_1.get_rect(center=self.foreground_1_rect.center)

        self.foreground_2_rect.center = (x + (self.background_rect.width/2 + 10), y + (self.background_rect.height))
        self.foreground_2_rect = self.foreground_2.get_rect(center=self.foreground_2_rect.center)

        self.font_rect.center = (x + (self.background_rect.width/2 + 10), y + (self.background_rect.height))
        self.font_rect = self.font_surface.get_rect(center=self.font_rect.center)


    def draw(self, display_surface, mouse_position):
        local_x = mouse_position[0]
        local_y = mouse_position[1]
        self.set_position(local_x, local_y)
        display_surface.blit(self.foreground_2, self.foreground_2_rect)
        display_surface.blit(self.foreground, self.foreground_rect)
        display_surface.blit(self.foreground_1, self.foreground_1_rect)
        display_surface.blit(self.background, self.background_rect)
        display_surface.blit(self.font_surface, self.font_rect)

class LabelText():
    def __init__(self, text, font_file, color, size):
        self.color = color
        font = pygame.font.Font(font_file, size)
        self.surface = font.render(text, False, color)
        self.rect = self.surface.get_rect(center=(0, 0))
        self.text = text

    def set_position_top_left(self, x, y):
        self.rect.topleft = (x, y)
        self.rect = self.surface.get_rect(topleft=self.rect.topleft)

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def draw(self, display_surface):
        display_surface.blit(self.surface, self.rect)

class TextBox():
    def __init__(self, text, font_file, color, text_size, width):
        self.color = color
        font = pygame.font.Font(font_file, text_size)
        self.font = font
        self.wrapped_text = self.wrap_text(text, width)
        self.surface = font.render(self.wrapped_text, False, color)
        self.rect = self.surface.get_rect(center=(0, 0))
        self.text = text
        self.width = width

    def set_position_top_left(self, x, y):
        self.rect.topleft = (x, y)
        self.rect = self.surface.get_rect(topleft=self.rect.topleft)

    def set_position(self, x, y):
        self.rect.center = (x, y)
        self.rect = self.surface.get_rect(center=self.rect.center)

    def wrap_text(self, text, width):
        # Split text into lines based on the width of the box
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + word + ' '
            if self.font.size(test_line)[0] <= width:
                current_line = test_line
            else:
                current_line = current_line + '\n'
                lines.append(current_line)
                current_line = word + ' '

        current_line = current_line + '\n'
        lines.append(current_line)
        return ''.join(lines)

    def draw(self, display_surface):
        y_offset = self.rect.topleft[1]
        lines = self.wrapped_text.split('\n')
        for line in lines:
            text_surface = self.font.render(line, False, self.color)
            display_surface.blit(text_surface, (self.rect.topleft[0], y_offset))
            y_offset += self.font.get_height()