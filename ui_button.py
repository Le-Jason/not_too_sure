import pygame
from rocket import *

class rocket_part_group():
    def __init__(self):
        self.parts = pygame.sprite.Group()
        self.idx = 0
        self.parts_idx = []
        self.is_follow = False

    def add(self, image, rec):
        self.parts.add(button_parts(image, rec))
        self.parts_idx.append(self.idx)
        self.idx += 1

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
        self.parts.update()

class button_parts(pygame.sprite.Sprite):
    def __init__(self, image, pos):
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
        self.title = []
        self.rec = []
        self.rec_rect = []

        self.background = pygame.Surface((275, 720), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.background.fill((70, 70, 70, 200))
        self.background_rect = self.background.get_rect(topleft=(0, 0))
        self.object_1 = rocket_part_group()

        self.debounce_threshold = 500
        self.last_update_time = 0

    def add(self, title, pos, size):
        self.title.append(title)
        self.rec.append(pygame.Surface((size[0], size[1]), pygame.SRCALPHA))
        self.rec[-1].fill((255, 0, 0, 0))
        self.rec_rect.append(self.rec[-1].get_rect(topleft=(pos[0], pos[1])))

    def draw(self, display_screen):
        for i in range(len(self.rec)):
            display_screen.blit(self.rec[i], self.rec_rect[i])

    def click(self, mouse_pos, display_screen, current_look):
        rocket_image = None
        for i in range(len(self.title)):
            if (self.rec_rect[i].collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])) or (current_look == self.title[i]):
                display_screen.blit(self.background, self.background_rect)
                current_look = self.title[i]
                current_time = pygame.time.get_ticks()

                if current_look == 'Command Pod':
                    mk1 = pygame.image.load('graphics/spites/commander_pod.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            mk1_rec = mk1.get_rect(topleft=(80, 80))
                            self.object_1.add('graphics/spites/commander_pod.png', mk1_rec)
                            self.last_update_time = current_time
                elif current_look == 'Fuel Tank':
                    mk1 = pygame.image.load('graphics/spites/small_fuel_tank.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/small_fuel_tank.png', mk1_rec)
                            self.last_update_time = current_time

                elif current_look == 'Rocket Engine':
                    mk1 = pygame.image.load('graphics/spites/small_rocket_engine.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/small_rocket_engine.png', mk1_rec)
                            self.last_update_time = current_time

                elif current_look == 'Controls':
                    mk1 = pygame.image.load('graphics/spites/decoupler.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/decoupler.png', mk1_rec)
                            self.last_update_time = current_time

                    mk2 = pygame.image.load('graphics/spites/heat_shield.png').convert_alpha()
                    mk2_rec = mk2.get_rect(topleft=(80 + 100, 80))
                    display_screen.blit(mk2, mk2_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk2_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/heat_shield.png', mk2_rec)
                            self.last_update_time = current_time

                elif current_look == 'Miscellaneous':
                    mk1 = pygame.image.load('graphics/spites/parachute.png').convert_alpha()
                    mk1_rec = mk1.get_rect(topleft=(80, 80))
                    display_screen.blit(mk1, mk1_rec)
                    if current_time - self.last_update_time > self.debounce_threshold:
                        if (mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                            self.object_1.add('graphics/spites/parachute.png', mk1_rec)
                            self.last_update_time = current_time

                elif current_look == 'Launch':
                    rocket_image = self.object_1.parts

        self.object_1.update(display_screen)

        return current_look, rocket_image