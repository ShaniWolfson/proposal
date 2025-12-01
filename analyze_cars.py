import pygame
import os

pygame.init()

# Create display first
screen = pygame.display.set_mode((1, 1))

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

# Let's analyze the layout by checking for patterns
# Assuming right-facing cars are in one column
# Let's try to find the spacing

# Check column 1 (right-facing, x=112 to 224)
# Look for non-transparent pixels to find where each car starts
print("\nAnalyzing right column (x=112-224)...")

cars_found = []
current_car_start = None
last_row_had_pixels = False

for y in range(height):
    has_pixels = False
    # Sample a few pixels in the right column to check if car is present
    for x in range(112, 224, 10):
        if x < width:
            color = vehicles_sheet.get_at((x, y))
            if color.a > 50:  # Not transparent
                has_pixels = True
                break
    
    if has_pixels and not last_row_had_pixels:
        current_car_start = y
    elif not has_pixels and last_row_had_pixels and current_car_start is not None:
        car_height = y - current_car_start
        if car_height > 5:  # Ignore tiny gaps
            cars_found.append((current_car_start, y, car_height))
            print(f"Car #{len(cars_found)}: y={current_car_start} to {y}, height={car_height}px")
        current_car_start = None
    
    last_row_had_pixels = has_pixels

# Handle last car if it goes to the end
if last_row_had_pixels and current_car_start is not None:
    car_height = height - current_car_start
    cars_found.append((current_car_start, height, car_height))
    print(f"Car #{len(cars_found)}: y={current_car_start} to {height}, height={car_height}px")

print(f"\nTotal cars found: {len(cars_found)}")
print("\nTo use a car, note its start Y position and height")

pygame.quit()
