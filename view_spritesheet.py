import pygame
import os

pygame.init()

# Create display first
screen = pygame.display.set_mode((800, 600))

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

pygame.display.set_caption(f"Vehicle Spritesheet - {width}x{height}")

# Create a scrollable view
scroll_y = 0
scroll_speed = 20

font = pygame.font.SysFont(None, 24)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                scroll_y = max(0, scroll_y - scroll_speed)
            elif event.key == pygame.K_DOWN:
                scroll_y = min(height - 600, scroll_y + scroll_speed)
    
    screen.fill((40, 40, 40))
    
    # Draw the spritesheet
    screen.blit(vehicles_sheet, (0, -scroll_y))
    
    # Draw grid lines every 32 pixels to help see sprite boundaries
    for y in range(0, height, 32):
        pygame.draw.line(screen, (100, 100, 100), (0, y - scroll_y), (width, y - scroll_y), 1)
    
    for x in range(0, width, 112):  # Try 112px columns
        pygame.draw.line(screen, (100, 100, 100), (x, -scroll_y), (x, height - scroll_y), 1)
    
    # Instructions
    info = font.render(f"Use UP/DOWN to scroll (pos: {scroll_y}px) | ESC to close", True, (255, 255, 255))
    info_bg = pygame.Surface((info.get_width() + 10, info.get_height() + 10))
    info_bg.fill((40, 40, 40))
    screen.blit(info_bg, (5, 5))
    screen.blit(info, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nLook at the spritesheet to find the blue car")
print("Note its position and dimensions")
