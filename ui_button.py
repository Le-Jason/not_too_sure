import pygame
from rocket import *
from data.part_data import *

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
                    display_screen.blit(mk2, mk2_rec)
                    display_screen.blit(mk3, mk3_rec)
                    display_screen.blit(mk1, mk1_rec)
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