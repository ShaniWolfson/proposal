import pygame
import os

pygame.init()
screen = pygame.display.set_mode((1, 1))  # Minimal display

# Load the vehicles spritesheet
vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
veh_files = os.listdir(vehicles_path)
veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()

width, height = vehicles_sheet.get_size()
print(f"Spritesheet size: {width}x{height}")

# Assuming 32x32 sprites
sprite_width = 32
sprite_height = 32

rows = height // sprite_height
cols = width // sprite_width

print(f"Grid: {cols} columns x {rows} rows = {cols * rows} sprites")
print("\nAnalyzing sprites for blue color...")

# Look for sprites with significant blue color
blue_sprites = []

for row in range(rows):
    for col in range(cols):
        x = col * sprite_width
        y = row * sprite_height
        
        # Extract sprite
        sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        sprite.blit(vehicles_sheet, (0, 0), (x, y, sprite_width, sprite_height))
        
        # Sample some pixels to check for blue
        blue_count = 0
        total_opaque = 0
        
        for sx in range(0, sprite_width, 2):
            for sy in range(0, sprite_height, 2):
                color = sprite.get_at((sx, sy))
                if color.a > 128:  # Opaque enough
                    total_opaque += 1
                    r, g, b = color.r, color.g, color.b
                    # Check if blue is dominant (b > r and b > g)
                    if b > r and b > g and b > 100:
                        blue_count += 1
        
        if total_opaque > 0:
            blue_ratio = blue_count / total_opaque
            if blue_ratio > 0.3:  # At least 30% blue pixels
                blue_sprites.append((row, col, blue_ratio))
                print(f"  Row {row}, Col {col}: {blue_ratio*100:.1f}% blue")

print(f"\nFound {len(blue_sprites)} sprites with significant blue color")

if blue_sprites:
    # Sort by blue ratio to find the most blue one
    blue_sprites.sort(key=lambda x: x[2], reverse=True)
    best = blue_sprites[0]
    print(f"\nMost blue sprite: Row {best[0]}, Col {best[1]} ({best[2]*100:.1f}% blue)")
    print(f"Extract with: ({best[1] * sprite_width}, {best[0] * sprite_height}, {sprite_width}, {sprite_height})")

pygame.quit()
