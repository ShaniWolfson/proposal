import pygame
import os

pygame.init()

# Create a display first
screen = pygame.display.set_mode((800, 600))

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

# Resize window to fit the scaled spritesheet
screen = pygame.display.set_mode((width * 2, height * 2))
pygame.display.set_caption("Vehicle Spritesheet Preview - Press ESC to close")

# Scale up for visibility
scaled = pygame.transform.scale(vehicles_sheet, (width * 2, height * 2))

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    screen.fill((50, 50, 50))
    screen.blit(scaled, (0, 0))
    
    # Draw grid lines to show individual sprites (assuming 32x32)
    for x in range(0, width * 2, 64):
        pygame.draw.line(screen, (255, 255, 0), (x, 0), (x, height * 2), 1)
    for y in range(0, height * 2, 64):
        pygame.draw.line(screen, (255, 255, 0), (0, y), (width * 2, y), 1)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nLook for the blue car with blue windows in the display.")
print("Each cell is 32x32 pixels.")
print("Count from top-left: row 0 is top, column 0 is left.")
