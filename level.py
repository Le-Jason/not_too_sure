from sprite import *
from planet import *
from camera import *
from rocket import *
from level import *
from ui_button import *
from dynamics import *
from graphics import *
from object import *
from ui import *
import pygame
from sys import exit
from abc import abstractmethod
from utils import *
from player import *

class BaseLevels():
    def __init__(self, display_surface, game_state_manager, system_info):
        self.display_surface = display_surface
        self.game_state_manager = game_state_manager
        self.system_info = system_info

        # Debounce Variables
        self.last_press_time = [0]
        self.debounce_time = 250

    @abstractmethod
    def initialization(self):
        pass

    @abstractmethod
    def run(self):
        pass

class Level(BaseLevels):
    def __init__(self, display, gameStateManager, display_surface, system_info, start_time,
                VAB_object):
        # Displays and Game Manager
        self.display = display
        self.gameStateManager = gameStateManager
        self.display_surface = display_surface
        self.level = 'rocket' # Level start view

        # Create Manager Classes
        self.dynamics = Dynamics(system_info)
        self.graphics = Graphics(display_surface, system_info, self.dynamics.env.sky_color, self.dynamics.env.radius)
        self.ui = RocketUI(display_surface, system_info)

        # Create Level Sprites
        pygame.display.set_caption('Gound Level')
        self.earth = Background_Objects('graphics/ui/earth.png', [0, 0, 0 , 0, 0, 0], system_info['length_per_pixel'], size=6378136.3*2)
        self.vab = Background_Objects('graphics/spites/launch_pad_2.png', [0, 6378143.3, 0 , 0, 0, 0], system_info['length_per_pixel'])
        self.gnd = Background_Objects('graphics/ground.png', [0, 6378136.3, 0 , 0, 0, 0], system_info['length_per_pixel'], location_init='top')
        self.object_group = pygame.sprite.Group()
        self.object_group.add(self.gnd)
        self.object_group.add(self.vab)

        # System Level
        self.WIDTH = system_info['WIDTH']
        self.HEIGHT = system_info['HEIGHT']
        self.TIME_STEP = system_info['TIME_STEP']
        self.length_per_pixel = system_info['length_per_pixel']
        self.start_time = start_time

        self.VAB_object = VAB_object
        self.init = False

        # Used for key press debounce
        self.debounce_threshold = 500 # Wait for 500 ticks
        self.last_update_time = 0     # Counter for last updated time

        # Used for scaling
        self.scale = 1.0
        self.scale_increment = 0.01

    def run(self):
        # Wait til the VAB level get a working rocket
        if self.init == False:
            self.init = True
            self.rocket = Rocket(self.VAB_object.rocket, self.length_per_pixel)

        # Start level
        if self.init == True:
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()
            # Fire the current rocket engines
            if keys[pygame.K_SPACE]:
                self.rocket.rocket_fire()
            # Rotate the rocket clockwise
            if keys[pygame.K_RIGHT]:
                self.rocket.rocket_rotate(True)
            # Rotate the rocket counter-clockwise
            if keys[pygame.K_LEFT]:
                self.rocket.rocket_rotate(False)
            # Scale the level up
            if keys[pygame.K_UP]:
                self.scale += self.scale_increment
            # Scale the level down
            if keys[pygame.K_DOWN]:
                self.scale -= self.scale_increment
            # Switch the level views
            if keys[pygame.K_m]:
                if current_time - self.last_update_time > self.debounce_threshold:
                    if self.level == 'rocket':
                        self.level = 'map'
                    else:
                        self.level = 'rocket'
                    self.last_update_time = current_time

            # Update Models
            self.dynamics.update(self.rocket)

            # Update Graphics
            self.gnd.update_state(self.rocket)
            self.graphics.update(self.rocket, self.dynamics.env)
            self.graphics.map_object_to_screen(self.gnd, 'rocket_view')
            self.graphics.map_object_to_screen(self.vab, 'rocket_view')
            self.graphics.map_rocket_to_screen(self.rocket, 'rocket_view')
            if self.level == 'rocket':
                self.ui.update(self.rocket, self.dynamics.env)
            if self.level == 'map':
                self.graphics.update_map(self.rocket, self.dynamics.env.mu)
                # self.earth.scaled_image(self.scale)
                self.graphics.scaled_map(self.scale, 'map_view')
                self.graphics.map_object_to_screen(self.earth, 'map_view')
                self.ui.update(self.rocket, self.dynamics.env)

            # pygame.draw.circle(self.display_surface, (255, 0, 0), self.dynamics.overlap, 1)
            # pygame.draw.circle(self.display_surface, (255, 0, 0), self.dynamics.part_overlap, 1)

            # # Update Models
            self.dynamics.update_rocket(self.rocket, self.object_group, self.graphics.screen_frame_dim)
            self.rocket.update(self.dynamics.env.mu)

class VAB(BaseLevels):
    def __init__(self, display_surface, game_state_manager, system_info, player):
        super().__init__(display_surface, game_state_manager, system_info)
        # Set variables for each level
        self.length_per_pixel = self.system_info['length_per_pixel']
        self.player = player
        self.start_money = self.player.money

        # Set Background
        self.vab_bg = Main_Menu_Objects('graphics/vab_bg.png')
        self.vab_bg.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT']/2)
        self.vab_bg.set_scale(self.system_info['WIDTH'] / 1920)

        self.ui = Image('graphics/spites/vab_ui.png', 'topleft')
        self.money_and_symmetry = MoneySymmetryMenu(self.player)

        self.pod_button = SideCategoryButton('graphics/ui/vab/pod_', 'graphics/ui/vab/left_button_vab_ui_', 'Pod')
        self.pod_button.set_position(27, 75)

        self.fuel_button = SideCategoryButton('graphics/ui/vab/fuel_', 'graphics/ui/vab/left_button_vab_ui_', 'Tank')
        self.fuel_button.set_position(27, 75+49)

        self.engine_button = SideCategoryButton('graphics/ui/vab/engine_', 'graphics/ui/vab/left_button_vab_ui_', 'Engine')
        self.engine_button.set_position(27, 75+49+49)

        self.control_button = SideCategoryButton('graphics/ui/vab/control_', 'graphics/ui/vab/left_button_vab_ui_', 'Control')
        self.control_button.set_position(27, 75+49+49+49)

        self.struct_button = SideCategoryButton('graphics/ui/vab/struct_', 'graphics/ui/vab/left_button_vab_ui_', 'Structure')
        self.struct_button.set_position(27, 75+49+49+49+49)

        self.aero_button = SideCategoryButton('graphics/ui/vab/aero_', 'graphics/ui/vab/left_button_vab_ui_', 'Aero-Structure')
        self.aero_button.set_position(27, 75+49+49+49+49+49)

        self.misc_button = SideCategoryButton('graphics/ui/vab/misc_', 'graphics/ui/vab/left_button_vab_ui_', 'Miscellaneous')
        self.misc_button.set_position(27, 75+49+49+49+49+49+49)

        self.science_button = SideCategoryButton('graphics/ui/vab/science_', 'graphics/ui/vab/left_button_vab_ui_', 'Science')
        self.science_button.set_position(27, 75+49+49+49+49+49+49+49)

        self.set_up_button_parts()

        self.parts_background = SurfaceImage((275, 720), (70, 70, 70, 200), loc='topleft')

        self.roaming_parts = pygame.sprite.Group()

        self.rocket = None
        self.current_menu = 'NA'
        self.king = 0

        self.ui_feature = [self.ui, self.parts_background]

        self.buttons = [
            self.pod_button,
            self.fuel_button,
            self.engine_button,
            self.control_button,
            self.struct_button,
            self.aero_button,
            self.misc_button,
            self.science_button,
        ]

    def initialization(self):
        pygame.mixer.music.load('music/intro.mp3')
        pygame.mixer.music.play(-1)
        pygame.display.set_caption('VAB')

    def run(self):
        # Section to see if any buttons/keys are pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            if len(self.roaming_parts) > 0:
                last_sprite = self.roaming_parts.sprites()[-1]
                if last_sprite.being_moved == True:
                    self.roaming_parts.remove(last_sprite)

        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        ### PRI BUTTON LOGIC ###
        if mouse_buttons[0]:
            for button in self.buttons:
                if button.check_for_hover(mouse_pos):
                    button.set_state('high')
                    button.label.draw(self.display_surface, mouse_pos)
                    break
        for index, button in enumerate(self.buttons, start=1):
            if button.background_state == 'high' and self.king != index:
                for other_button in self.buttons:
                    if other_button != button:
                        other_button.set_state('low')
                self.king = index
                break
        sub_button = []
        for button in self.buttons:
            if button.image_state == 'high':
                if button.name == 'Pod':
                    sub_button = self.sub_pod_buttons
                elif button.name == 'Tank':
                    sub_button = self.sub_fuel_buttons
                elif button.name == 'Engine':
                    sub_button = self.sub_engine_buttons
                elif button.name == 'Control':
                    sub_button = self.sub_control_buttons
                elif button.name == 'Structure':
                    sub_button = self.sub_struct_buttons
                elif button.name == 'Aero-Structure':
                    sub_button = self.sub_aero_buttons
                elif button.name == 'Miscellaneous':
                    sub_button = self.sub_misc_buttons
                elif button.name == 'Science':
                    sub_button = self.sub_science_buttons

        touched_recently = False
        if mouse_buttons[0]:
            if PygameUtils.is_mouse_pressed_without_debounce(self.last_press_time, self.debounce_time):
                # if you press one of the sub cat buttons
                for sub_but in sub_button:
                    if sub_but.check_for_hover(mouse_pos) and sub_but.check_for_debounce():
                        if len(self.roaming_parts) > 0:
                            if (self.roaming_parts.sprites()[-1].being_moved):
                                self.roaming_parts.remove(self.roaming_parts.sprites()[-1])
                        self.roaming_parts.add(RocketNode(sub_but.name))
                        break
                # if you not pressing one of the sub cat buttons
                else:
                    if (self.rocket is not None):
                        if (len(self.roaming_parts) > 0):
                            if (self.roaming_parts.sprites()[-1].being_moved == False):
                                hover_node = PygameUtils.check_for_hover_tree(mouse_pos, self.rocket)
                                if hover_node is not None:
                                    self.rocket.delete_child(hover_node)
                                    new_part = hover_node.copy()
                                    new_part.being_moved = True
                                    self.roaming_parts.add(new_part)
                                    touched_recently = True
                                    self.rocket.calculate_money()
                        else:
                            hover_node = PygameUtils.check_for_hover_tree(mouse_pos, self.rocket)
                            if hover_node is not None:
                                self.rocket.delete_child(hover_node)
                                new_part = hover_node.copy()
                                new_part.being_moved = True
                                self.roaming_parts.add(new_part)
                                touched_recently = True
                                self.rocket.calculate_money()
                    # If the current itemed is held
                    if (len(self.roaming_parts) > 0):
                        if (self.roaming_parts.sprites()[-1].being_moved == True):
                            # If not touching a feature
                            # If no parts are in the rocket
                            # and there is a roaming part
                            if (self.rocket is None) and (len(self.roaming_parts) > 0) and (self.am_i_touching_ui_features(mouse_pos) == False):
                                if self.roaming_parts.sprites()[-1].type != "pod":
                                    # TODO: add a message on the screen
                                    print("First Part Must be Pod Type")
                                else:
                                    self.rocket = RocketNode(self.roaming_parts.sprites()[-1].name)
                                    self.rocket.set_absolute_position(mouse_pos[0], mouse_pos[1])
                                    self.roaming_parts.remove(self.roaming_parts.sprites()[-1])
                                    self.rocket.calculate_money()
                            elif ((self.am_i_touching_ui_features(mouse_pos) == False) and (len(self.roaming_parts) > 0)):
                                # This handles if the part that is being held on the main rocket
                                if (self.rocket.add_child(self.roaming_parts.sprites()[-1], other_options=(touched_recently == False))):
                                    self.roaming_parts.remove(self.roaming_parts.sprites()[-1])
                                    self.rocket.calculate_money()
                                elif (touched_recently == False):
                                    self.roaming_parts.sprites()[-1].being_moved = False
                                    self.rocket.calculate_money()
                        # If no itemed is not held
                        else:
                            for roam_parts in self.roaming_parts:
                                if PygameUtils.check_for_hover(mouse_pos, roam_parts):
                                    self.roaming_parts.remove(roam_parts)
                                    self.roaming_parts.add(roam_parts)
                                    self.roaming_parts.sprites()[-1].being_moved = True
                                    self.rocket.calculate_money()
                                    break


        self.vab_bg.update()

        self.display_surface.blit(self.vab_bg.image, self.vab_bg.rect)
        self.parts_background.draw(self.display_surface)

        if self.current_menu == 'Launch':
            self.game_state_manager.set_state('level')

        self.ui.draw(self.display_surface)

        if self.rocket is not None:
            self.player.money = self.start_money - self.rocket.calculate_money()
        else:
            self.player.money = self.start_money
        self.money_and_symmetry.draw(self.display_surface, mouse_pos, mouse_buttons)
        for button in self.money_and_symmetry.buttons:
            if PygameUtils.check_for_hover(mouse_pos, button.background):
                button.label.draw(self.display_surface, mouse_pos)
        if PygameUtils.check_for_hover(mouse_pos, self.money_and_symmetry.symmetry.background):
            self.money_and_symmetry.symmetry.label.draw(self.display_surface, mouse_pos)

        for button in self.buttons:
            button.draw(self.display_surface, mouse_pos)

        for parts in self.roaming_parts:
            parts.update(mouse_pos)


        # Draw the sub button first
        for sub_but in sub_button:
            sub_but.draw(self.display_surface, mouse_pos)
        # Draw the parts
        for parts in self.roaming_parts:
            parts.draw(self.display_surface)
        # Then check for label
        for sub_but in sub_button:
            if sub_but.check_for_hover(mouse_pos):
                sub_but.label.draw(self.display_surface, mouse_pos)
                break

        if self.rocket is not None:
            self.rocket.update_flags()
            self.rocket.draw(self.display_surface)
            if (self.money_and_symmetry.weight_center.state == 1):
                self.rocket.draw_weight(self.display_surface)
            if (self.money_and_symmetry.thrust_center.state == 1):
                self.rocket.draw_thrust(self.display_surface)

    def set_up_button_parts(self):
        # Commander Pods
        self.sub_pod_buttons = []
        test_button = SubCategoryButton('graphics/spites/commander_pod', 'graphics/ui/vab/part_bg_', 'Mk1 Command Pod')
        test_button.set_position(110, 120)
        test_button.set_image_scale_speed(0.005)
        test_button.set_image_scale_bounds(0.95,1.05)
        test_button.set_image_relative_position(0, -4)

        self.sub_pod_buttons.append(test_button)

        # Fuel Button
        self.sub_fuel_buttons = []
        part_tank = SubCategoryButton('graphics/spites/small_fuel_tank', 'graphics/ui/vab/part_bg_', 'FL-T200 Fuel Tank')
        part_tank.set_position(110, 120)
        part_tank.set_image_scale_speed(0.005)
        part_tank.set_image_scale_bounds(0.95,1.05)
        part_tank.set_image_relative_position(0, -4)

        self.sub_fuel_buttons.append(part_tank)

        # Engine Button
        self.sub_engine_buttons = []
        small_rocket_engine = SubCategoryButton('graphics/spites/small_rocket_engine', 'graphics/ui/vab/part_bg_', 'LV-T45 Liquid Fuel Engine')
        small_rocket_engine.set_position(110, 120)
        small_rocket_engine.set_image_scale_speed(0.005)
        small_rocket_engine.set_image_scale_bounds(0.95,1.05)
        small_rocket_engine.set_image_relative_position(0, -2)

        self.sub_engine_buttons.append(small_rocket_engine)

        # Controls Button
        self.sub_control_buttons = []
        decoupler_parts = SubCategoryButton('graphics/spites/decoupler', 'graphics/ui/vab/part_bg_', 'TD-12 Decoupler')
        decoupler_parts.set_position(110, 120)
        decoupler_parts.set_image_scale_speed(0.005)
        decoupler_parts.set_image_scale_bounds(0.95,1.05)
        decoupler_parts.set_image_relative_position(0, -30)

        heat_shield_parts = SubCategoryButton('graphics/spites/heat_shield', 'graphics/ui/vab/part_bg_', 'Heat Shield (1.25m)')
        heat_shield_parts.set_position(210, 120)
        heat_shield_parts.set_image_scale_speed(0.005)
        heat_shield_parts.set_image_scale_bounds(0.95,1.05)
        heat_shield_parts.set_image_relative_position(0, -30)

        radial_decoupler_parts = SubCategoryButton('graphics/spites/radial_decoupler', 'graphics/ui/vab/part_bg_', 'TT-38K Radial Decoupler')
        radial_decoupler_parts.set_position(110, 220)
        radial_decoupler_parts.set_image_scale_speed(0.005)
        radial_decoupler_parts.set_image_scale_bounds(0.95,1.05)
        radial_decoupler_parts.set_image_relative_position(0, 0)

        self.sub_control_buttons.append(decoupler_parts)
        self.sub_control_buttons.append(heat_shield_parts)
        self.sub_control_buttons.append(radial_decoupler_parts)

        # Struct Button
        self.sub_struct_buttons = []

        # Aero Button
        self.sub_aero_buttons = []
        basic_fins_parts = SubCategoryButton('graphics/spites/basic_fins', 'graphics/ui/vab/part_bg_', 'Basic Fin')
        basic_fins_parts.set_position(110, 120)
        basic_fins_parts.set_image_scale_speed(0.005)
        basic_fins_parts.set_image_scale_bounds(0.95,1.05)
        basic_fins_parts.set_image_relative_position(-10, 0)

        self.sub_aero_buttons.append(basic_fins_parts)

        # Miscellaneous Button
        self.sub_misc_buttons = []
        small_parachute = SubCategoryButton('graphics/spites/parachute', 'graphics/ui/vab/part_bg_', 'Mk16 Parachute')
        small_parachute.set_position(110, 120)
        small_parachute.set_image_scale_speed(0.005)
        small_parachute.set_image_scale_bounds(0.95,1.05)
        small_parachute.set_image_relative_position(0, -25)

        self.sub_misc_buttons.append(small_parachute)

        # Science Button
        self.sub_science_buttons = []

    def am_i_touching_ui_features(self, mouse_position):
        for feature in self.ui_feature:
            local_x = mouse_position[0] - feature.rect.x
            local_y = mouse_position[1] - feature.rect.y
            if feature.rect.collidepoint(mouse_position[0], mouse_position[1]):
                if feature.mask.get_at((local_x, local_y)):
                    return True
        return False

class Start(BaseLevels):
    def __init__(self, display_surface, game_state_manager, system_info):
        super().__init__(display_surface, game_state_manager, system_info)

        self.title_text = NoSurroundingButton('Space Simulator', 'font/Pixeltype.ttf', 200)
        self.title_text.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.25)
        self.title_text.set_color('#b5cfff')

        self.earth_bg = Main_Menu_Objects('graphics/title_earth.png')
        self.earth_bg.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 1.3)
        self.earth_bg.set_rotation(0.05)

        self.space_bg = Main_Menu_Objects('graphics/space_background.png')
        self.space_bg.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT']/2)
        self.space_bg.set_scale(self.system_info['WIDTH'] / 1920)

        self.start_button = NoSurroundingButton('Start Game', 'font/Pixeltype.ttf', 100)
        self.start_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.45)

        self.settings_button = NoSurroundingButton('Settings', 'font/Pixeltype.ttf', 100)
        self.settings_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.60)

        self.quit_button = NoSurroundingButton('Quit', 'font/Pixeltype.ttf', 100)
        self.quit_button.set_position(self.system_info['WIDTH']/2, self.system_info['HEIGHT'] * 0.75)

        # Sprite sheet information
        sprite_sheet_image = 'graphics/penguin_suit_ani.png'
        frame_width = 64
        frame_height = 64

        # Define animations with start index and number of frames
        animations = {
            'idle': [(0, 1), (0,)],    # Idle animation frames 0 to 3
            'waving': [(0, 3), (700, 100, 700)], # Running animation frames 4 to 7
        }
        self.penguin = MainMenuSprite(sprite_sheet_image, frame_width, frame_height, animations)

    def initialization(self):
        pygame.mixer.music.load('music/intro.mp3')
        pygame.mixer.music.play(-1)
        pygame.display.set_caption('Main Menu')

        self.penguin.set_position(self.system_info['WIDTH'], self.system_info['HEIGHT'], 0)
        self.penguin.set_rotation(10)
        self.penguin.set_velocity(-20, -40, 0)
        self.penguin.set_acceleration(0.0, 1.2, 0.0)
        self.penguin.set_animation('waving')


    def run(self):
        self.earth_bg.update()
        self.penguin.update()
        self.space_bg.update()

        self.display_surface.blit(self.space_bg.image, self.space_bg.rect)
        self.display_surface.blit(self.earth_bg.image, self.earth_bg.rect)
        self.display_surface.blit(self.penguin.image, self.penguin.rect)

        self.start_button.update(pygame.mouse.get_pos(), actions=[self.switch_levels])
        self.settings_button.update(pygame.mouse.get_pos())
        self.quit_button.update(pygame.mouse.get_pos(), actions=[self.quit_game])

        self.display_surface.blit(self.title_text.font_surface, self.title_text.font_rect)
        self.display_surface.blit(self.start_button.font_surface, self.start_button.font_rect)
        self.display_surface.blit(self.settings_button.font_surface, self.settings_button.font_rect)
        self.display_surface.blit(self.quit_button.font_surface, self.quit_button.font_rect)

    def quit_game(self):
        pygame.quit()
        exit()

    def switch_levels(self):
        self.game_state_manager.set_state('VAB')

class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.prev_state = None

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        self.prev_state = self.currentState
        self.currentState = state