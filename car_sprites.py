"""
Car Sprite Sheet Loader
Loads and slices a vertical sprite sheet of cars where each row contains
a single car in four directions: left, right, front, back.
Uses alpha detection for precise sprite boundary detection.
"""

import pygame


def find_contiguous_ranges(bool_list):
    """Return list of (start, end) inclusive-exclusive ranges where bool_list is True."""
    ranges = []
    start = None
    for i, v in enumerate(bool_list):
        if v and start is None:
            start = i
        if not v and start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(bool_list)))
    return ranges


def detect_columns_rows_by_alpha(surface, expected_cols=4, min_nontransparent_pixels=1):
    """
    Detect horizontal (columns) and vertical (rows) spans where alpha > 0 exists.
    Returns lists of (start, end) pixel indices for columns and rows.
    """
    w, h = surface.get_size()

    # Get alpha overview: try surfarray array_alpha for speed; fallback to manual per-pixel scan
    try:
        import pygame.surfarray as surfarray
        import numpy as np
        alpha = surfarray.array_alpha(surface)  # 2D numpy array shape (w, h)? sometimes (h,w)
        # Ensure shape is (h, w)
        if alpha.shape[0] == w and alpha.shape[1] == h:
            alpha = alpha.T
        # alpha is now shape (h, w)
        # 1D boolean projections
        x_proj = (alpha.sum(axis=0) >= min_nontransparent_pixels)  # length w
        y_proj = (alpha.sum(axis=1) >= min_nontransparent_pixels)  # length h
        x_bool = x_proj.tolist()
        y_bool = y_proj.tolist()
    except Exception:
        # Fallback: manual scan (slower) but avoids dependency on surfarray/numpy
        x_bool = [False] * w
        y_bool = [False] * h
        for x in range(w):
            for y in range(h):
                if surface.get_at((x, y))[3] > 0:
                    x_bool[x] = True
                    break
        for y in range(h):
            for x in range(w):
                if surface.get_at((x, y))[3] > 0:
                    y_bool[y] = True
                    break

    x_ranges = find_contiguous_ranges(x_bool)
    y_ranges = find_contiguous_ranges(y_bool)

    # If we found more columns than expected, merge nearby ones
    if expected_cols and len(x_ranges) > expected_cols:
        # Merge ranges that are close together to form expected_cols groups
        # Calculate gaps between ranges
        gaps = []
        for i in range(len(x_ranges) - 1):
            gap = x_ranges[i + 1][0] - x_ranges[i][1]
            gaps.append((gap, i))
        
        # Sort by gap size (largest first) and keep the largest gaps as separators
        gaps.sort(reverse=True)
        separator_indices = sorted([g[1] for g in gaps[:expected_cols - 1]])
        
        # Merge ranges into groups
        merged = []
        current_start = x_ranges[0][0]
        for i, (start, end) in enumerate(x_ranges):
            if i in separator_indices:
                merged.append((current_start, x_ranges[i][1]))
                if i + 1 < len(x_ranges):
                    current_start = x_ranges[i + 1][0]
            elif i == len(x_ranges) - 1:
                merged.append((current_start, end))
        
        x_ranges = merged
    
    # If we found fewer than expected columns, try splitting the widest x_range into equal parts
    elif expected_cols and len(x_ranges) < expected_cols:
        if len(x_ranges) == 1:
            start, end = x_ranges[0]
            width = end - start
            part = width // expected_cols
            if part > 0:
                x_ranges = [(start + i * part, start + (i + 1) * part) for i in range(expected_cols)]
                # last part take the remainder:
                x_ranges[-1] = (x_ranges[-1][0], end)

    return x_ranges, y_ranges


def trim_surface_alpha(surface):
    """Return a new Surface trimmed to bounding box of non-transparent pixels."""
    w, h = surface.get_size()
    # try fast surfarray method
    try:
        import pygame.surfarray as surfarray
        import numpy as np
        alpha = surfarray.array_alpha(surface)
        # alpha shape (h, w) expected
        rows = (alpha.sum(axis=1) > 0)
        cols = (alpha.sum(axis=0) > 0)
        y_ranges = find_contiguous_ranges(rows.tolist())
        x_ranges = find_contiguous_ranges(cols.tolist())
        if not x_ranges or not y_ranges:
            return surface  # nothing non-transparent
        x0, x1 = x_ranges[0]
        y0, y1 = y_ranges[0]
        return surface.subsurface(pygame.Rect(x0, y0, x1 - x0, y1 - y0)).copy()
    except Exception:
        # Fallback: manual pixel scan
        left, right, top, bottom = w, 0, h, 0
        found = False
        for x in range(w):
            for y in range(h):
                if surface.get_at((x, y))[3] > 0:
                    found = True
                    left = min(left, x)
                    right = max(right, x)
                    top = min(top, y)
                    bottom = max(bottom, y)
        if not found:
            return surface
        return surface.subsurface(pygame.Rect(left, top, right - left + 1, bottom - top + 1)).copy()


def load_car_sprites(path, expected_cols=4, directions=None, split_first_col=False):
    """
    Load image and slice into sprites using alpha-detection.
    
    Args:
        path (str): Path to the sprite sheet image
        expected_cols (int): Number of columns (directions per car). Default is 4.
        directions (list): List of direction names. If None, uses ["left", "right", "front", "back"]
        split_first_col (bool): If True, split the first detected column into 2 separate sprites (left/right)
        
    Returns:
        dict: Dictionary mapping row_index -> {direction: surface}
    """
    sheet = pygame.image.load(path).convert_alpha()
    x_ranges, y_ranges = detect_columns_rows_by_alpha(sheet, expected_cols=expected_cols)

    if not x_ranges or not y_ranges:
        raise RuntimeError("Could not detect any non-empty columns/rows in the sprite sheet.")

    # If first column needs splitting (contains left+right views)
    if split_first_col and len(x_ranges) > 0:
        first_col = x_ranges[0]
        col_width = first_col[1] - first_col[0]
        mid_point = first_col[0] + col_width // 2
        # Split first column into two halves
        x_ranges = [(first_col[0], mid_point), (mid_point, first_col[1])] + list(x_ranges[1:])

    # Normalize directions
    if directions is None:
        directions = ["left", "right", "front", "back"]
    if len(directions) != len(x_ranges):
        raise ValueError(f"directions length ({len(directions)}) must match detected columns ({len(x_ranges)})")

    sprites = {}
    for row_idx, (y0, y1) in enumerate(y_ranges):
        sprites[row_idx] = {}
        for col_idx, (x0, x1) in enumerate(x_ranges):
            rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
            sub = sheet.subsurface(rect).copy()

            # Trim transparent border inside that rect (so each sprite is tightly cropped)
            trimmed = trim_surface_alpha(sub)
            
            # For left and right views: crop to exactly 25 pixels tall from the top
            dir_name = directions[col_idx]
            if dir_name in ["left", "right"]:
                current_h = trimmed.get_height()
                if current_h > 33:
                    cropped = trimmed.subsurface(pygame.Rect(0, 0, trimmed.get_width(), 33)).copy()
                    trimmed = cropped
            
            sprites[row_idx][dir_name] = trimmed

    return sprites


# Demo usage:
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1040, 800))
    pygame.display.set_caption("Car Sprite Sheet Demo - Alpha Detection")
    clock = pygame.time.Clock()

    # Use the '90s vehicles sprite sheet
    path = "art/backgrounds/date_drive/'90s vehicles.png"

    # First detect how many columns the sheet actually has
    print("\n=== Detecting sprite sheet structure ===")
    test_sheet = pygame.image.load(path).convert_alpha()
    x_ranges, y_ranges = detect_columns_rows_by_alpha(test_sheet, expected_cols=4)
    num_cols = len(x_ranges)
    print(f"Detected {num_cols} columns, {len(y_ranges)} rows")
    
    # The first column contains both left and right views, so we need to split it
    # This gives us 4 total directions
    directions = ["left", "right", "front", "back"]
    split_first = True
    
    print(f"Using directions: {directions}")
    print(f"Splitting first column: {split_first}")

    sprites = load_car_sprites(path, expected_cols=4, directions=directions, split_first_col=split_first)
    print(f"Loaded {len(sprites)} cars from sprite sheet")
    print(f"Directions: {list(sprites[0].keys())}")
    
    # Show first row, all directions in a row for visual check
    current_car = 0
    
    # Try to initialize font, but don't crash if it fails
    try:
        font = pygame.font.SysFont('arial', 24)
        small_font = pygame.font.SysFont('arial', 18)
    except:
        font = None
        small_font = None

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE or ev.key == pygame.K_DOWN:
                    current_car = (current_car + 1) % len(sprites)
                elif ev.key == pygame.K_UP:
                    current_car = (current_car - 1) % len(sprites)

        screen.fill((40, 40, 40))
        
        # Draw all directions of current car
        x = 50
        y = 300
        scale = 3
        
        for i, d in enumerate(directions):
            surf = sprites[current_car][d]
            
            # Scale up 3x for better visibility
            scaled = pygame.transform.scale(surf, (surf.get_width() * scale, surf.get_height() * scale))
            screen.blit(scaled, (x, y))
            
            # Draw direction label
            if font:
                dir_text = font.render(d.upper(), True, (255, 255, 0))
                text_rect = dir_text.get_rect(center=(x + scaled.get_width() // 2, y - 30))
                screen.blit(dir_text, text_rect)
            
            # Draw bounding box
            pygame.draw.rect(screen, (100, 100, 100), (x, y, scaled.get_width(), scaled.get_height()), 1)
            
            # Show original size
            if small_font:
                size_text = small_font.render(f"{surf.get_width()}x{surf.get_height()}", True, (150, 150, 150))
                screen.blit(size_text, (x, y + scaled.get_height() + 5))
            
            # Move x position for next sprite (add spacing)
            x += scaled.get_width() + 30

        # Draw info
        if font:
            title = font.render(f"Car #{current_car} of {len(sprites)-1}", True, (255, 255, 255))
            screen.blit(title, (20, 20))
            
            info = small_font.render(f"Total cars: {len(sprites)} | Alpha-detected boundaries", True, (200, 200, 200))
            screen.blit(info, (20, 50))
        
        if small_font:
            instructions = [
                "SPACE/DOWN: Next car",
                "UP: Previous car",
                "ESC/Close: Quit"
            ]
            for i, instruction in enumerate(instructions):
                inst_text = small_font.render(instruction, True, (150, 150, 150))
                screen.blit(inst_text, (20, 700 + i * 25))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
