import pygame
import os

pygame.init()

# Create a temporary display first
temp_screen = pygame.display.set_mode((100, 100))

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

# Spritesheet is 224x960
# 2 columns (left-facing and right-facing), 30 rows (15 cars x 2)
# Each sprite is 112x32
car_width = 63
car_height = 45
cols = 2  # left, right, up, down
rows = 30  # 15 cars, each with 2 views (left and right)

# Create display to show all cars with labels
scale = 3
display_width = cols * car_width * scale + 100
display_height = rows * car_height * scale + 100
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Vehicle Spritesheet - All Cars")

font = pygame.font.SysFont(None, 20)
small_font = pygame.font.SysFont(None, 16)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    screen.fill((40, 40, 40))
    
    # Draw column headers
    directions = ["Left", "Right"]
    for col in range(cols):
        label = font.render(directions[col], True, (255, 255, 0))
        x = 50 + col * car_width * scale + (car_width * scale - label.get_width()) // 2
        screen.blit(label, (x, 5))
    
    # Draw each car sprite
    for row in range(rows):
        # Row label (show which car and which view)
        car_num = (row // 2) + 1
        view = "view1" if row % 2 == 0 else "view2"
        row_label = small_font.render(f"Car{car_num}-{view}", True, (255, 255, 0))
        screen.blit(row_label, (5, 30 + row * car_height * scale + car_height * scale // 2))
        
        for col in range(cols):
            # Extract sprite
            sprite = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
            x = col * car_width
            y = row * car_height
            sprite.blit(vehicles_sheet, (0, 0), pygame.Rect(x, y, car_width, car_height))
            
            # Scale up
            scaled = pygame.transform.scale(sprite, (car_width * scale, car_height * scale))
            
            # Draw on screen
            draw_x = 50 + col * car_width * scale
            draw_y = 30 + row * car_height * scale
            screen.blit(scaled, (draw_x, draw_y))
            
            # Draw grid box
            pygame.draw.rect(screen, (100, 100, 100), 
                           (draw_x, draw_y, car_width * scale, car_height * scale), 1)
            
            # Draw coordinates
            coord_text = small_font.render(f"({col},{row})", True, (150, 150, 150))
            screen.blit(coord_text, (draw_x + 2, draw_y + 2))
    
    # Instructions
    info = font.render("Press ESC to close - Find the blue car and note its row number", True, (255, 255, 255))
    screen.blit(info, (10, display_height - 25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nFind the blue car with blue windows and note which Car number and which column (Left/Right)")
print("Then use that information in the drive scene code.")
