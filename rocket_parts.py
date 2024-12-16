import pygame
from utils import *
from data.part_data import *
import json

class RocketNode(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.children = []
        self.child_stick = []

        # Setting up data
        with open('data/part_label.json', 'r') as file:
            data = json.load(file)
        self.data = data[name]
        self.type = self.data["type"]
        self.clear_stick_type()

        # Setting up image
        self.image = pygame.image.load(self.data['image']).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)

        # Variables
        self.being_moved = True
        self.STICKY_DISTANCE = 50
        self.descendants_num = 0
        self.center_of_mass = (0.0, 0.0)
        self.center_of_thrust = (None, None)

    def calculate_total_mass(self):
        mass = float(self.data['mass'])
        for child in self.children:
            mass += child.calculate_total_mass()
        return mass

    def calculate_total_thrust(self):
        thrust = None
        if self.type == "engine":
            thrust = float(self.data["Thrust (ASL)"])
        for child in self.children:
            thrust_child = child.calculate_total_thrust()
            if (thrust_child is not None) and (thrust is not None):
                thrust += thrust_child
            elif (thrust_child is not None):
                thrust = thrust_child
        return thrust

    def calculate_delta_mass_wrt_CoM(self):
        edge = self.non_transparent_edges()
        center_x = (edge['left'] + edge['right']) / 2.0
        center_y = (edge['top'] + edge['bottom']) / 2.0
        dx_mass = float(self.data['mass']) * center_x
        dy_mass = float(self.data['mass']) * center_y
        for child in self.children:
            dx_child, dy_child = child.calculate_delta_mass_wrt_CoM()
            dx_mass += dx_child
            dy_mass += dy_child
        return dx_mass, dy_mass

    def calculate_delta_thrust_wrt_CoT(self):
        dx_thrust = None
        dy_thrust = None
        if self.type == "engine":
            edge = self.non_transparent_edges()
            center_x = (edge['left'] + edge['right']) / 2.0
            bottom = edge['bottom']
            dx_thrust = float(self.data["Thrust (ASL)"]) * center_x
            dy_thrust = float(self.data["Thrust (ASL)"]) * bottom
        for child in self.children:
            dx_child, dy_child = child.calculate_delta_thrust_wrt_CoT()
            # Not checking dy because dx and dy should be populated with non None at
            # the same time
            if (dx_child is not None) and (dx_thrust is not None):
                dx_thrust += dx_child
                dy_thrust += dy_child
            elif (dx_child is not None):
                dx_thrust = dx_child
                dy_thrust = dy_child

        if (dx_thrust is not None) and (dy_thrust is None):
            raise ValueError("X and Y Thrust should be either None or not at the same time")
        elif (dy_thrust is not None) and (dx_thrust is None):
            raise ValueError("X and Y Thrust should be either None or not at the same time")

        return dx_thrust, dy_thrust

    def calculate_center_of_mass(self):
        total_mass = self.calculate_total_mass()
        dx_mass, dy_mass = self.calculate_delta_mass_wrt_CoM()
        cg_x = dx_mass / total_mass
        cg_y = dy_mass / total_mass
        return cg_x, cg_y

    def calculate_center_of_thrust(self):
        total_thrust = self.calculate_total_thrust()
        dx_thrust, dy_thrust = self.calculate_delta_thrust_wrt_CoT()
        if (total_thrust is None) or (dx_thrust is None) or (dy_thrust is None):
            return None, None
        ct_x = dx_thrust / total_thrust
        ct_y = dy_thrust / total_thrust
        return ct_x, ct_y

    def draw_weight(self, display_surface, color="#fcea00", radius=2):
        pygame.draw.circle(display_surface, "#0F0E0E", self.center_of_mass, radius+1)
        pygame.draw.circle(display_surface, color, self.center_of_mass, radius)

    def draw_thrust(self, display_surface, color="#fa8000", radius=2):
        if (self.center_of_thrust[0] is not None) and (self.center_of_thrust[1] is not None):
            pygame.draw.circle(display_surface, "#0F0E0E", self.center_of_thrust, radius+1)
            pygame.draw.circle(display_surface, color, self.center_of_thrust, radius)

    def calculate_money(self):
        cost = float(self.data['Cost'])
        for child in self.children:
            cost += child.calculate_money()
        return cost

    def clear_stick_type(self):
        self.stick_type = {
            "top": None,
            "bottom": None,
            "right": None,
            "left": None,
        }
        if "top" in self.data["stick"]:
            self.stick_type["top"] = True
        if "bottom" in self.data["stick"]:
            self.stick_type["bottom"] = True
        if "right" in self.data["stick"]:
            self.stick_type["right"] = True
        if "left" in self.data["stick"]:
            self.stick_type["left"] = True

    def copy(self):
        """Deep copy of the current node and all its children."""
        # Create a new instance of the current node
        new_node = RocketNode(self.name)

        # Copy the image, rect, and mask (this depends on how you want to handle them)
        new_node.image = self.image  # In real case, you may want to deep copy the surface.
        new_node.rect = self.rect    # Same for the rect (it could be deep copied).
        new_node.mask = self.mask    # Same for the mask (you could create a new mask if necessary).

        # Recursively copy all children and add them to the new node
        for child in self.children:
            new_node.add_child(child.copy())  # Recursively copy each child and add to the new node

        return new_node

    def add_child(self, child, other_options=True):
        if other_options == False:
            return False
        elif isinstance(child, RocketNode):
            success = self.stick_sprites(child)
            if success:
                if len(self.children) != len(self.child_stick):
                    raise ValueError("Children and Sticking is not the same size")
            return success
        else:
            raise ValueError("Adding child must be RocketNode type")

    def delete_child(self, child):
        if isinstance(child, RocketNode):
            # Try to remove the child by object reference
            if child in self.children:
                index = self.children.index(child)  # Get the index of the child node
                self.stick_type[self.child_stick[index]] = True
                if self.child_stick[index] == 'top':
                    child.stick_type['bottom'] = True
                elif self.child_stick[index] == 'bottom':
                    child.stick_type['top'] = True
                elif self.child_stick[index] == 'left':
                    child.stick_type['right'] = True
                elif self.child_stick[index] == 'right':
                    child.stick_type['left'] = True

                # Remove the child from both self.children and self.child_stick using the same index
                del self.children[index]
                del self.child_stick[index]
                return True  # Successfully deleted
            check_if_children_was_deleted = False
            for child_in_here in self.children:
                check_if_children_was_deleted = child_in_here.delete_child(child)
            return (False or check_if_children_was_deleted)  # Child node not found in the list
        else:
            raise ValueError("Deleting child must be RocketNode type")

    def delete_all_children(self):
        for child in self.children:
            child.delete_all_children()
        self.children = []
        self.child_stick = []

    def count_all_descendants(self):
        # Start by counting the immediate children
        count = len(self.children)
        # Recursively count the descendants of each child node
        for child in self.children:
            count += child.count_all_descendants()
        return count

    def set_absolute_position(self, x, y):
        # Get mouse position
        local_x = x
        local_y = y

        # Find the offset for the non-transparent pixel
        offset_x, offset_y = PygameUtils.find_center_offset(self.image)

        # Find the offset wrt to the center of the image
        width, height = self.image.get_size()
        offset_x = width/2 - offset_x
        offset_y = height/2 - offset_y

        relative_x = self.rect.centerx - (local_x + offset_x)
        relative_y = self.rect.centery - (local_y + offset_y)

        # Set the position of the sprite
        self.rect.center = (local_x + offset_x, local_y + offset_y)

        # Set the children
        for child in self.children:
            child.set_relative_position(-1*relative_x, -1*relative_y)

    def set_relative_position(self, relative_x, relative_y, relative='center'):
        if relative == 'center':
            self.rect.center = (self.rect.centerx + relative_x,
                                self.rect.centery + relative_y)
        elif relative == 'right':
            self.rect.right += relative_x
        elif relative == 'left':
            self.rect.left += relative_x
        elif relative == 'bottom':
            self.rect.bottom += relative_y
            self.rect.centerx += relative_x
        elif relative == 'top':
            self.rect.top += relative_y
            self.rect.centerx += relative_x
        for child in self.children:
            child.set_relative_position(relative_x, relative_y, relative=relative)

    def update_flags(self):
        # Used to reduced lag
        if (self.descendants_num != self.count_all_descendants()):
            self.center_of_mass = self.calculate_center_of_mass()
            self.center_of_thrust = self.calculate_center_of_thrust()
            self.descendants_num = self.count_all_descendants()
        return

    def update(self, mouse_position):
        if self.being_moved:
            local_x = mouse_position[0]
            local_y = mouse_position[1]
            self.set_absolute_position(local_x, local_y)

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)
        for child in self.children:
            child.draw(display_surface)

    def non_transparent_edges(self):
        x_coords = []
        y_coords = []
        edges = {
            'left': None,
            'right': None,
            'top': None,
            'bottom': None,
        }

        for y in range(self.mask.get_size()[1]):
            for x in range(self.mask.get_size()[0]):
                if self.mask.get_at((x, y)):  # Check if the pixel is not transparent
                    x_coords.append(x)
                    y_coords.append(y)

        if x_coords and y_coords:
            left = min(x_coords)
            right = max(x_coords)
            top = min(y_coords)
            bottom = max(y_coords)

            edges['left'] = left + self.rect.left
            edges['right'] = right + self.rect.left
            edges['top'] = top + self.rect.top
            edges['bottom'] = bottom + self.rect.top
        return edges

    def stick_sprites(self, sprite):
    # TODO: Might have a issues with one sprite has priority than another sprite where it makes no sense
        success = False
        if sprite.rect.colliderect(self.rect.inflate(self.STICKY_DISTANCE, self.STICKY_DISTANCE)):
            edges1 = sprite.non_transparent_edges()
            edges2 = self.non_transparent_edges()

            distances = {
                'left': abs(edges2['left'] - edges1['right']),
                'right': abs(edges1['left'] - edges2['right']),
                'top': abs(edges2['top'] - edges1['bottom']),
                'bottom': abs(edges1['top'] - edges2['bottom']),
            }

            closest_edge = min(distances, key=lambda k: abs(distances[k]))

            # Snap based on the closest edge
            if closest_edge == 'left' and (((self.stick_type["left"]) and (sprite.stick_type["right"])) or ((sprite.type == 'fins') or (sprite.type == 'radial_decoupler') or (self.type == 'radial_decoupler'))):
                distance = edges2['left'] - edges1['right']
                sprite.set_relative_position(distance, 0, relative='right')
                top_right_pixel = PygameUtils.get_top_right_non_transparent_pixel(sprite)
                bottom_left_pixel = PygameUtils.get_bottom_left_non_transparent_pixel(self)
                if (top_right_pixel[1] < bottom_left_pixel[1]):
                    self.child_stick.append("left")
                    self.stick_type["left"] = False
                    sprite.stick_type["right"] = False
                    success = True
                else:
                    sprite.set_relative_position(-distance, 0, relative='right')
            elif closest_edge == 'right' and (((self.stick_type["right"]) and (sprite.stick_type["left"])) or ((sprite.type == 'fins') or (sprite.type == 'radial_decoupler') or (self.type == 'radial_decoupler'))) :
                distance = edges1['left'] - edges2['right']
                sprite.set_relative_position(-1*distance, 0, relative='left')
                top_left_pixel = PygameUtils.get_top_left_non_transparent_pixel(sprite)
                bottom_right_pixel = PygameUtils.get_bottom_right_non_transparent_pixel(self)
                if (top_left_pixel[1] < bottom_right_pixel[1]):
                    self.child_stick.append("right")
                    self.stick_type["right"] = False
                    sprite.stick_type["left"] = False
                    success = True
                else:
                    sprite.set_relative_position(distance, 0, relative='left')
            elif closest_edge == 'top' and ((self.stick_type["top"]) and (sprite.stick_type["bottom"])):
                distance_vertical = edges2['top'] - edges1['bottom']
                distance_lateral = self.rect.centerx - sprite.rect.centerx
                self.stick_type["top"] = False
                sprite.stick_type["bottom"] = False
                self.child_stick.append("top")
                sprite.set_relative_position(distance_lateral, distance_vertical, relative='bottom')
                success = True
            elif closest_edge == 'bottom' and ((self.stick_type["bottom"]) and (sprite.stick_type["top"])):
                distance_vertical = edges1['top'] - edges2['bottom']
                distance_lateral = self.rect.centerx - sprite.rect.centerx
                self.stick_type["bottom"] = False
                sprite.stick_type["top"] = False
                self.child_stick.append("bottom")
                sprite.set_relative_position(distance_lateral, -1*distance_vertical, relative='top')
                success = True
        if success:
            self.children.append(sprite)
            return True
        is_children_stick = False
        for child in self.children:
            is_children_stick = child.add_child(sprite)
        return (success or is_children_stick)


class RocketManager():
    def __init__(self):
        self.parts = pygame.sprite.Group()
        self.STICKY_DISTANCE = 50

    def add_part(self, rocket_part):
        temp_rocket_part = rocket_part
        temp_rocket_part.being_moved = False
        self.parts.add(temp_rocket_part)

    def remove_part(self, rocket_part):
        rocket_part.clear_stick_type()
        self.parts.remove(rocket_part)

    def update():
        pass

    def draw(self, display_surface):
        if len(self.parts) > 0:
            self.parts.draw(display_surface)

    def stick_sprites(self, sprite):
    # TODO: Might have a issues with one sprite has priority than another sprite where it makes no sense
        success = False
        success_part = None
        for part in self.parts:
            if sprite.rect.colliderect(part.rect.inflate(self.STICKY_DISTANCE, self.STICKY_DISTANCE)):
                edges1 = sprite.non_transparent_edges()
                edges2 = part.non_transparent_edges()

                distances = {
                    'left': abs(edges2['left'] - edges1['right']),
                    'right': abs(edges1['left'] - edges2['right']),
                    'top': abs(edges2['top'] - edges1['bottom']),
                    'bottom': abs(edges1['top'] - edges2['bottom']),
                }

                closest_edge = min(distances, key=lambda k: abs(distances[k]))

                # Snap based on the closest edge
                if closest_edge == 'left' and (((part.stick_type["left"]) and (sprite.stick_type["right"])) or ((sprite.type == 'fins'))):
                    distance = edges2['left'] - edges1['right']
                    part.stick_type["left"] = False
                    sprite.stick_type["right"] = False
                    sprite.rect.right += distance
                    success = True
                    success_part = part
                elif closest_edge == 'right' and (((part.stick_type["right"]) and (sprite.stick_type["left"])) or ((sprite.type == 'fins'))) :
                    distance = edges1['left'] - edges2['right']
                    part.stick_type["right"] = False
                    sprite.stick_type["left"] = False
                    sprite.rect.left -= distance
                    success = True
                    success_part = part
                elif closest_edge == 'top' and ((part.stick_type["top"]) and (sprite.stick_type["bottom"])):
                    distance_vertical = edges2['top'] - edges1['bottom']
                    distance_lateral = part.rect.centerx - sprite.rect.centerx
                    part.stick_type["top"] = False
                    sprite.stick_type["bottom"] = False
                    sprite.rect.bottom += distance_vertical
                    sprite.rect.centerx += distance_lateral
                    success = True
                    success_part = part
                elif closest_edge == 'bottom' and ((part.stick_type["bottom"]) and (sprite.stick_type["top"])):
                    distance_vertical = edges1['top'] - edges2['bottom']
                    distance_lateral = part.rect.centerx - sprite.rect.centerx
                    part.stick_type["bottom"] = False
                    sprite.stick_type["top"] = False
                    sprite.rect.top -= distance_vertical
                    sprite.rect.centerx += distance_lateral
                    success = True
                    success_part = part
        if success == True:
            success_part.add_child(sprite)
            sprite.being_moved = False
            return True
        else:
            return False

class RocketPart(pygame.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        super().__init__()

        # Setting up data
        with open('data/part_label.json', 'r') as file:
            data = json.load(file)
        self.data = data[name]
        self.type = self.data["type"]
        self.clear_stick_type()

        # Setting up image
        self.image = pygame.image.load(self.data['image']).convert_alpha()
        self.rect = self.image.get_rect(center=(0, 0))
        self.mask = pygame.mask.from_surface(self.image)

        # Variables
        self.being_moved = True # Since init is moving it

    def clear_stick_type(self):
        self.stick_type = {
            "top": None,
            "bottom": None,
            "right": None,
            "left": None,
        }
        if "top" in self.data["stick"]:
            self.stick_type["top"] = True
        if "bottom" in self.data["stick"]:
            self.stick_type["bottom"] = True
        if "right" in self.data["stick"]:
            self.stick_type["right"] = True
        if "left" in self.data["stick"]:
            self.stick_type["left"] = True

    def set_position(self, x, y):
        # Get mouse position
        local_x = x
        local_y = y

        # Find the offset for the non-transparent pixel
        offset_x, offset_y = PygameUtils.find_center_offset(self.image)

        # Find the offset wrt to the center of the image
        width, height = self.image.get_size()
        offset_x = width/2 - offset_x
        offset_y = height/2 - offset_y

        # Set the position of the sprite
        self.rect.center = (local_x + offset_x, local_y + offset_y)

    def update(self, mouse_position):
        if self.being_moved:
            local_x = mouse_position[0]
            local_y = mouse_position[1]
            self.set_position(local_x, local_y)

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)

    def non_transparent_edges(self):
        x_coords = []
        y_coords = []
        edges = {
            'left': None,
            'right': None,
            'top': None,
            'bottom': None,
        }

        for y in range(self.mask.get_size()[1]):
            for x in range(self.mask.get_size()[0]):
                if self.mask.get_at((x, y)):  # Check if the pixel is not transparent
                    x_coords.append(x)
                    y_coords.append(y)

        if x_coords and y_coords:
            left = min(x_coords)
            right = max(x_coords)
            top = min(y_coords)
            bottom = max(y_coords)

            edges['left'] = left + self.rect.left
            edges['right'] = right + self.rect.left
            edges['top'] = top + self.rect.top
            edges['bottom'] = bottom + self.rect.top
        return edges