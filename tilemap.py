import pygame
import json
import re
import os

# Need pygame for Rect in load_collision_map
if not pygame.get_init():
    pygame.init()
class TileMap:
    """Loads and renders tilemaps from JavaScript layer files."""
    
    def __init__(self, tileset_paths, tile_size=16):
        """
        Args:
            tileset_paths: List of paths to tileset images
            tile_size: Size of each tile in pixels (default 32x32)
        """
        self.tile_size = tile_size
        self.tilesets = []
        self.tiles = {}  # Dictionary mapping tile ID to surface
        
        # Load all tilesets
        tile_id = 1  # Start from 1 since 0 = empty tile
        for path in tileset_paths:
            if os.path.exists(path):
                tileset = pygame.image.load(path).convert_alpha()
                self.tilesets.append(tileset)
                
                # Extract tiles from this tileset
                ts_width = tileset.get_width() // tile_size
                ts_height = tileset.get_height() // tile_size
                
                for row in range(ts_height):
                    for col in range(ts_width):
                        tile_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                        tile_surf.blit(tileset, (0, 0), 
                                     (col * tile_size, row * tile_size, tile_size, tile_size))
                        self.tiles[tile_id] = tile_surf
                        tile_id += 1
    
    def load_layer_from_js(self, js_file_path):
        """Load a layer from a JavaScript file containing a 2D array.
        
        Returns a 2D list of tile IDs.
        """
        with open(js_file_path, 'r') as f:
            content = f.read()
        
        # Extract the array from JavaScript const declaration
        # Match pattern: const varname = [[...]];
        match = re.search(r'const\s+\w+\s*=\s*(\[[\s\S]*?\]);', content)
        if not match:
            return []
        
        array_str = match.group(1)
        # Convert JavaScript array to Python list
        array_str = array_str.replace('\n', '').replace(' ', '')
        layer_data = eval(array_str)  # Safe here since we control the file format
        
        return layer_data
    
    def draw_layer(self, surface, layer_data, scale=1.0):
        """Draw a tile layer onto a surface.
        
        Args:
            surface: Pygame surface to draw on
            layer_data: 2D list of tile IDs
            scale: Scale factor for rendering (to fit different screen sizes)
        """
        scaled_tile_size = int(self.tile_size * scale)
        
        for row_idx, row in enumerate(layer_data):
            for col_idx, tile_id in enumerate(row):
                if tile_id == 0:  # 0 = empty tile
                    continue
                
                if tile_id in self.tiles:
                    tile_surf = self.tiles[tile_id]
                    if scale != 1.0:
                        tile_surf = pygame.transform.scale(tile_surf, 
                                                          (scaled_tile_size, scaled_tile_size))
                    
                    x = col_idx * scaled_tile_size
                    y = row_idx * scaled_tile_size
                    surface.blit(tile_surf, (x, y))


def load_collision_map(js_file_path, tile_size=16, scale=1.0):
    """Load collision data and return list of collision rectangles.
    
    Args:
        js_file_path: Path to collisions.js file
        tile_size: Base tile size in pixels (before scaling)
        scale: Scale factor applied to the tilemap
    
    Returns:
        List of pygame.Rect objects for collision tiles
    """
    with open(js_file_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'const\s+\w+\s*=\s*(\[[\s\S]*?\]);', content)
    if not match:
        return []
    
    array_str = match.group(1)
    array_str = array_str.replace('\n', '').replace(' ', '')
    collision_data = eval(array_str)
    
    # Create collision rectangles
    collision_rects = []
    scaled_tile_size = int(tile_size * scale)
    
    for row_idx, row in enumerate(collision_data):
        for col_idx, value in enumerate(row):
            if value == 1:  # 1 = collision
                rect = pygame.Rect(
                    col_idx * scaled_tile_size,
                    row_idx * scaled_tile_size,
                    scaled_tile_size,
                    scaled_tile_size
                )
                collision_rects.append(rect)
    
    return collision_rects
    
    def draw_layer(self, surface, layer_data, scale=1.0):
        """Draw a tile layer onto a surface.
        
        Args:
            surface: Pygame surface to draw on
            layer_data: 2D list of tile IDs
            scale: Scale factor for rendering (to fit different screen sizes)
        """
        scaled_tile_size = int(self.tile_size * scale)
        
        for row_idx, row in enumerate(layer_data):
            for col_idx, tile_id in enumerate(row):
                if tile_id == 0:  # 0 = empty tile
                    continue
                
                if tile_id in self.tiles:
                    tile_surf = self.tiles[tile_id]
                    if scale != 1.0:
                        tile_surf = pygame.transform.scale(tile_surf, 
                                                          (scaled_tile_size, scaled_tile_size))
                    
                    x = col_idx * scaled_tile_size
                    y = row_idx * scaled_tile_size
                    surface.blit(tile_surf, (x, y))


def load_dinner_tilemap(dinner_folder_path):
    """Helper function to load the dinner scene tilemap.
    
    Args:
        dinner_folder_path: Path to art/backgrounds/dinner folder
    
    Returns:
        List of tuples: (TileMap instance, layer data array) for each layer
    """
    images_path = os.path.join(dinner_folder_path, 'images')
    data_path = os.path.join(dinner_folder_path, 'data')
    
    # Map each layer to its specific tileset (from index.js)
    layer_config = [
        ('l_New_Layer_1.js', '36f64d67-ac65-466e-b273-f6a716e5a400.png'),
        ('l_New_Layer_2.js', '36f64d67-ac65-466e-b273-f6a716e5a400.png'),
        ('l_New_Layer_4.js', '4de8c995-53d6-47f6-f675-8739b10a4b00.png'),
        ('l_New_Layer_4_1.js', 'e2966820-83b3-472f-1255-76c6a3585f00.png'),
        ('l_New_Layer_5.js', 'e2966820-83b3-472f-1255-76c6a3585f00.png'),
        ('l_New_Layer_6.js', '36f64d67-ac65-466e-b273-f6a716e5a400.png'),  # Assuming same as layer 1
        ('l_New_Layer_7.js', '36f64d67-ac65-466e-b273-f6a716e5a400.png'),  # Assuming same as layer 1
        ('l_New_Layer_8.js', 'a43e70e4-a509-44ca-6b81-9016e4b50300.png'),
    ]
    
    layers = []
    for layer_file, tileset_file in layer_config:
        layer_path = os.path.join(data_path, layer_file)
        tileset_path = os.path.join(images_path, tileset_file)
        
        if os.path.exists(layer_path) and os.path.exists(tileset_path):
            # Create a separate tilemap for this layer with its specific tileset
            tilemap = TileMap([tileset_path], tile_size=16)
            layer_data = tilemap.load_layer_from_js(layer_path)
            layers.append((tilemap, layer_data))
    
    return layers


def load_apartment_tilemap(apartment_folder_path):
    """Helper function to load the apartment scene tilemap from TMJ file.
    
    Args:
        apartment_folder_path: Path to art/backgrounds/apartment folder
    
    Returns:
        List of tuples: (TileMap instance, layer data array) for each layer
    """
    tmj_path = os.path.join(apartment_folder_path, 'apartment.tmj')
    tileset_path = os.path.join(apartment_folder_path, 'untitled.png')
    
    if not os.path.exists(tmj_path) or not os.path.exists(tileset_path):
        return []
    
    # Load the TMJ JSON file
    with open(tmj_path, 'r') as f:
        map_data = json.load(f)
    
    # Create tilemap with the single tileset
    # The TMJ file has multiple tilesets, but we'll use the main one
    tilemap = TileMap([tileset_path], tile_size=16)
    
    layers = []
    for layer in map_data.get('layers', []):
        if layer.get('type') == 'tilelayer' and layer.get('visible', True):
            # Convert flat data array to 2D array
            width = layer.get('width', 16)
            height = layer.get('height', 16)
            flat_data = layer.get('data', [])
            
            layer_data = []
            for row in range(height):
                row_data = flat_data[row * width:(row + 1) * width]
                layer_data.append(row_data)
            
            layers.append((tilemap, layer_data))
    
    return layers


def load_apartment_collision_map(apartment_folder_path, tile_size=16, scale=1.0):
    """Load collision data from apartment TMJ file and return list of collision rectangles.
    
    Args:
        apartment_folder_path: Path to art/backgrounds/apartment folder
        tile_size: Base tile size in pixels (before scaling)
        scale: Scale factor applied to the tilemap
    
    Returns:
        List of pygame.Rect objects for collision polygons
    """
    tmj_path = os.path.join(apartment_folder_path, 'apartment.tmj')
    
    if not os.path.exists(tmj_path):
        return []
    
    with open(tmj_path, 'r') as f:
        map_data = json.load(f)
    
    collision_rects = []
    
    # Process object layers with collision polygons
    for layer in map_data.get('layers', []):
        if layer.get('type') == 'objectgroup':
            layer_name = layer.get('name', '').lower()
                
            for obj in layer.get('objects', []):
                if 'polygon' not in obj:
                    continue
                    
                obj_x = obj.get('x', 0)
                obj_y = obj.get('y', 0)
                
                # Filter furniture layer: skip chairs (y > 185), keep table
                if 'funiture' in layer_name and obj_y > 185:
                    continue
                
                # Convert polygon to bounding rect
                polygon = obj.get('polygon', [])
                if not polygon:
                    continue
                    
                min_x = min(p['x'] for p in polygon)
                max_x = max(p['x'] for p in polygon)
                min_y = min(p['y'] for p in polygon)
                max_y = max(p['y'] for p in polygon)
                
                # Apply position adjustments
                y_offset = 0
                if 'wall' in layer_name and 130 <= obj_y <= 132:
                    y_offset = -50  # TV stand wall
                elif 'funiture' in layer_name and 149 <= obj_y <= 151:
                    y_offset = -50  # Center furniture
                
                rect = pygame.Rect(
                    (obj_x + min_x) * scale,
                    (obj_y + min_y) * scale + y_offset,
                    (max_x - min_x) * scale,
                    (max_y - min_y) * scale
                )
                collision_rects.append(rect)
    
    return collision_rects


def load_apartment_object_rects(apartment_folder_path, tile_size=16, scale=1.0):
    """Load object collision boxes from apartment TMJ file's Object Layer 1.
    
    Args:
        apartment_folder_path: Path to art/backgrounds/apartment folder
        tile_size: Base tile size in pixels (before scaling)
        scale: Scale factor applied to the tilemap
    
    Returns:
        List of pygame.Rect objects for the table objects (wine bottle, glasses, box)
    """
    tmj_path = os.path.join(apartment_folder_path, 'apartment.tmj')
    
    if not os.path.exists(tmj_path):
        return []
    
    with open(tmj_path, 'r') as f:
        map_data = json.load(f)
    
    object_rects = []
    
    # Process Object Layer 1 which contains wine bottle, glasses, and box
    for layer in map_data.get('layers', []):
        if layer.get('type') == 'objectgroup' and layer.get('name') == 'Object Layer 1':
            for obj in layer.get('objects', []):
                if 'polygon' not in obj:
                    continue
                    
                obj_x = obj.get('x', 0)
                obj_y = obj.get('y', 0)
                
                # Convert polygon to bounding rect
                polygon = obj.get('polygon', [])
                if not polygon:
                    continue
                    
                min_x = min(p['x'] for p in polygon)
                max_x = max(p['x'] for p in polygon)
                min_y = min(p['y'] for p in polygon)
                max_y = max(p['y'] for p in polygon)
                
                rect = pygame.Rect(
                    (obj_x + min_x) * scale,
                    (obj_y + min_y) * scale,
                    (max_x - min_x) * scale,
                    (max_y - min_y) * scale
                )
                object_rects.append(rect)
    
    return object_rects

