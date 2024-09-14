import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the screen dimensions and create a window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Plotting the hyperbola [(x^2/a^2) – (y^2/b^2)] = 1')

# Define the hyperbola parameters
a = 5
b = 3

# Scale and translate function coordinates to screen coordinates
def to_screen_coords(x, y, width, height, scale):
    screen_x = int(x * scale + width // 2)
    screen_y = int(height // 2 - y * scale)
    return screen_x, screen_y

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill((255, 255, 255))

    # Define the range of x values and scaling factor
    x_start, x_end = -10, 10
    scale = 20  # Scale to fit the function within the window

    # Calculate the points for the right branch of the hyperbola
    points_right = []
    x = a
    while x <= x_end:
        y = b * math.sqrt((x**2 / a**2) - 1)
        screen_x, screen_y = to_screen_coords(x, y, width, height, scale)
        if 0 <= screen_x < width and 0 <= screen_y < height:
            points_right.append((screen_x, screen_y))
        x += 0.1

    # Calculate the points for the left branch of the hyperbola
    points_left = []
    x = -a
    while x >= x_start:
        y = b * math.sqrt((x**2 / a**2) - 1)
        screen_x, screen_y = to_screen_coords(x, y, width, height, scale)
        if 0 <= screen_x < width and 0 <= screen_y < height:
            points_left.append((screen_x, screen_y))
        x -= 0.1

    # Draw the lines for both branches
    if len(points_right) > 1:
        pygame.draw.lines(screen, (0, 0, 0), False, points_right, 2)

    if len(points_left) > 1:
        pygame.draw.lines(screen, (0, 0, 0), False, points_left, 2)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()