import pygame

class VABPartInformationLabel():
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

class PodVABPartInformationLabel(VABPartInformationLabel):
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

class EngineVABPartInformationLabel(VABPartInformationLabel):
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

class TankVABPartInformationLabel(VABPartInformationLabel):
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

class HeatShieldVABPartInformationLabel(VABPartInformationLabel):
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

class DecouplerVABPartInformationLabel(VABPartInformationLabel):
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

class FinsVABPartInformationLabel(VABPartInformationLabel):
    def __init__(self, text, data):
        super().__init__(text, data)
        self.info_text_5 = LabelText(f"Lifting Surface (Wing Area): {data['Lifting Surface']}", 'font/Pixeltype.ttf', '#93c47d', 15)

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

    def update_text(self, text):
        self.wrapped_text = self.wrap_text(text, self.width)
        self.surface = self.font.render(self.wrapped_text, False, self.color)

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