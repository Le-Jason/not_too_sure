import pygame

class Node:
    def __init__(self, value, x, y):
        self.value = value
        self.children = []
        self.x = x
        self.y = y

    def add_child(self, child):
        self.children.append(child)

    def draw(self, screen, font):
        # Draw the node
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 20)
        text = font.render(str(self.value), True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

        # Draw edges to children
        for child in self.children:
            pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (child.x, child.y), 2)
            child.draw(screen, font)

    def count_all_descendants(self):
        # Start by counting the immediate children
        count = len(self.children)
        # Recursively count the descendants of each child node
        for child in self.children:
            count += child.count_all_descendants()
        return count

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 24)

# Create a simple tree
root = Node(1, 400, 50)
root.add_child(Node(2, 200, 150))
root.add_child(Node(3, 600, 150))
root.children[0].add_child(Node(4, 100, 250))
root.children[0].add_child(Node(5, 300, 250))
print(f"Root node has {root.count_all_descendants()} total descendants.")  # Output: 5

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    root.draw(screen, font)
    pygame.display.flip()

pygame.quit()