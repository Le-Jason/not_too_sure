import pygame

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
        self.is_follow = False
        for part in self.parts:
            if part.mouse_follow_active == True:
                self.is_follow = True
        for i, part in enumerate(self.parts):
            print(f"{i}: {self.is_follow}")
            if part.rect.collidepoint(current_mouse_pos) and (mouse_buttons[0] == True) and (self.is_follow == False):
                part.mouse_follow_active = True
            elif (mouse_buttons[0] == False):
                part.mouse_follow_active = False
        

    def update(self, display_screen):
        self.player_input()
        self.parts.draw(display_screen)
        self.parts.update()

class button_parts(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()

        mouse_pos = pygame.mouse.get_pos()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1]))
        self.mouse_follow_active = False
        self.prev_mouse_pos = mouse_pos

        self.update_time = 1
        self.last_update_time = 0

    def follow_mouse(self):
        current_mouse_pos = pygame.mouse.get_pos()
        if self.mouse_follow_active:
            self.rect.move_ip(current_mouse_pos[0] - self.prev_mouse_pos[0],
                            current_mouse_pos[1] - self.prev_mouse_pos[1])
        self.prev_mouse_pos = current_mouse_pos

    def update(self):
        self.follow_mouse()

class vab_ui_button:
    def __init__(self, title, pos, size):
        self.title = title
        self.rec = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.rec.fill((255, 0, 0, 0))  # Fill the surface with a transparent red color
        self.rec_rect = self.rec.get_rect(topleft=(pos[0], pos[1]))

        self.background = pygame.Surface((275, 720), pygame.SRCALPHA)  # Create a surface with per-pixel alpha
        self.background.fill((70, 70, 70, 200))
        self.background_rect = self.background.get_rect(topleft=(0, 0))

        self.mk1 = pygame.image.load('graphics/spites/commander_pod.png').convert_alpha()
        self.mk1_rec = self.mk1.get_rect(topleft=(80, 80))

        self.active = 0
        self.object_1 = rocket_part_group()

        self.mouse_pos = (0,0)

        self.debounce_threshold = 500
        self.last_update_time = 0

        self.selected_object = None

    def add(self, title, pos, size):
        self.title.append(title)
        

    def click(self, mouse_pos, display_screen, current_look):
        if (self.rec_rect.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])) or (current_look == self.title):
            display_screen.blit(self.background, self.background_rect)
            current_look = self.title
            current_time = pygame.time.get_ticks()

            if current_look == 'Command Pod':
                display_screen.blit(self.mk1, self.mk1_rec)
                if current_time - self.last_update_time > self.debounce_threshold:
                    if (self.mk1_rec.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0])):
                        mk1_rec = self.mk1.get_rect(topleft=(80, 80))
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

        self.object_1.update(display_screen)

        self.mouse_pos = mouse_pos

        return current_look