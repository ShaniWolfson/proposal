import pygame
import os

pygame.init()

# Create display first
temp_screen = pygame.display.set_mode((100, 100))

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

# Right-facing cars are in the right column (x=112 to 224)
# Car positions from analysis:
cars = [
    (7, 64, 57),    # Car 1
    (71, 128, 57),  # Car 2
    (135, 192, 57), # Car 3
    (199, 256, 57), # Car 4
    (265, 320, 55), # Car 5
    (331, 384, 53), # Car 6
    (395, 448, 53), # Car 7
    (459, 512, 53), # Car 8
    (528, 576, 48), # Car 9
    (587, 640, 53), # Car 10
    (649, 704, 55), # Car 11
    (713, 768, 55), # Car 12
    (775, 832, 57), # Car 13
    (840, 896, 56), # Car 14
    (907, 960, 53), # Car 15
]

# Create display to show right-facing cars
scale = 2
car_display_width = 112 * scale
padding = 20
display_width = car_display_width + 150
display_height = len(cars) * (60 * scale) + 100

screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Right-Facing Cars Only")

font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

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
    
    # Draw title
    title = font.render("Right-Facing Cars (Right Column)", True, (255, 255, 0))
    screen.blit(title, (10, 10))
    
    # Draw each car
    y_offset = 50
    for i, (start_y, end_y, car_height) in enumerate(cars):
        car_num = i + 1
        
        # Extract the car sprite from right column
        car_x = 112
        car_width = 112
        
        car_sprite = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
        car_sprite.blit(vehicles_sheet, (0, 0), pygame.Rect(car_x, start_y, car_width, car_height))
        
        # Scale up
        scaled_car = pygame.transform.scale(car_sprite, (car_width * scale, car_height * scale))
        
        # Draw car
        car_y = y_offset + i * (60 * scale)
        screen.blit(scaled_car, (padding, car_y))
        
        # Draw border around car
        pygame.draw.rect(screen, (100, 255, 100), 
                        (padding, car_y, car_width * scale, car_height * scale), 2)
        
        # Draw label
        label = font.render(f"Car #{car_num}", True, (255, 255, 255))
        screen.blit(label, (padding + car_width * scale + 20, car_y))
        
        # Draw dimensions
        dims = small_font.render(f"y={start_y}, h={car_height}", True, (200, 200, 200))
        screen.blit(dims, (padding + car_width * scale + 20, car_y + 25))
    
    # Instructions
    info = small_font.render("Press ESC to close - Choose which car you want", True, (255, 255, 255))
    screen.blit(info, (10, display_height - 25))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nWhich car number do you want to use? (1-15)")
