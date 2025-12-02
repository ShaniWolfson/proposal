import pygame
import random
import importlib
import os
from scene import Scene


class DriveScene(Scene):
    """Night road driving scene with scrolling background.

    vehicle: 'car' or 'uhaul'
    duration: seconds to auto-complete (default 60)
    """

    def __init__(self, vehicle='car', duration=60.0, manager=None):
        super().__init__(manager)
        self.vehicle = vehicle
        self.duration = duration
        self.timer = duration
        self.font = None
        
        # Load night road background
        self.night_road = None
        self.road_x = 0
        
        # Load blue car sprite
        self.blue_car = None
        self.car_x = 200  # Starting X position
        self.car_y = 720 // 2  # Center vertically
        self.car_speed = 300  # Up/down movement speed
        self.car_speed_x = 200  # Left/right movement speed
        
        self.obstacles = []
        self.spawn_timer = 0.0
        self.scroll_speed = 100  # Road scrolling speed (slowed down)
        self.crashed = False
        self.crash_timer = 0.0
        
        # Road boundaries (y coordinates with offset applied)
        self.road_top = 150 + 100  # y_offset + some margin for top of road
        self.road_bottom = 150 + 720 - 100  # y_offset + scaled_height - margin for bottom

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.timer = self.duration
        self.obstacles = []
        self.spawn_timer = 0.5
        self.crashed = False
        self.road_x = 0
        
        # Set road boundaries based on the actual road rendering
        # Road is scaled to 720px tall and offset by 150px down
        # The actual drivable area is roughly in the middle third of the road
        self.road_top = 150 + 200  # Start of drivable area (offset + margin)
        self.road_bottom = 150 + 720 - 150  # End of drivable area (offset + height - margin)
        
        # Load the night road background
        road_path = os.path.join('art', 'backgrounds', 'date_drive', 'nightroad.png')
        self.night_road = pygame.image.load(road_path).convert_alpha()
        
        # Load car sprites using the car_sprites loader
        from car_sprites import load_car_sprites
        vehicles_path = os.path.join('art', 'backgrounds', 'date_drive', "'90s vehicles.png")
        
        # Load all car sprites
        self.all_cars = load_car_sprites(vehicles_path, expected_cols=4, 
                                        directions=["left", "right", "front", "back"],
                                        split_first_col=True)
        
        # Use car #3 (yellow car) facing right
        car_index = 3
        car_sprite = self.all_cars[car_index]["right"]
        
        # Scale up 2x for visibility
        self.blue_car = pygame.transform.scale(car_sprite, 
                                              (car_sprite.get_width() * 2, 
                                               car_sprite.get_height() * 2))
        
        # Position car on left side and vertically centered on the road
        self.car_x = 200
        self.car_y = (720 - self.blue_car.get_height()) // 2

    def handle_event(self, event: pygame.event.EventType):
        pass

    def update(self, dt: float):
        if self.crashed:
            self.crash_timer -= dt
            if self.crash_timer <= 0:
                self.crashed = False
        else:
            # Scroll the road to the right (simulating forward movement)
            self.road_x += self.scroll_speed * dt
            
            # Loop the road when it scrolls past the image width
            if self.night_road:
                road_width = self.night_road.get_width()
                if self.road_x >= road_width:
                    self.road_x -= road_width
            
            # Handle up/down/left/right movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.car_y -= int(self.car_speed * dt)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.car_y += int(self.car_speed * dt)
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.car_x -= int(self.car_speed_x * dt)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.car_x += int(self.car_speed_x * dt)

            # Clamp car position to road boundaries
            if self.blue_car:
                car_height = self.blue_car.get_height()
                car_width = self.blue_car.get_width()
                # Clamp to road boundaries (top and bottom edges)
                self.car_y = max(self.road_top, min(self.car_y, self.road_bottom - car_height))
                # Clamp to screen bounds (left and right)
                self.car_x = max(0, min(self.car_x, 1280 - car_width))

            self.timer -= dt
            if self.timer <= 0:
                # transition to apartment scene module to avoid import cycles
                try:
                    mod = importlib.import_module('apartment_scene')
                    cls = getattr(mod, 'ApartmentScene')
                    if self.manager:
                        self.manager.go_to(cls(self.manager))
                except Exception:
                    # fallback: do nothing
                    pass

    def draw(self, surface: pygame.Surface):
        # Fill black background
        surface.fill((0, 0, 0))
        
        # Draw the scrolling night road
        if self.night_road:
            # The tilemap is 300 tiles wide x 16 tiles tall (4800px x 256px at 16px per tile)
            # Screen is 1280x720, we want to show tiles at proper scale
            
            # Scale factor to make the road fill the screen vertically and look bigger
            # Road height is 256px, screen is 720px: scale = 720/256 = 2.8125
            # Increase to 4x for bigger appearance
            scale_factor = 3.5
            tile_scaled = int(16 * scale_factor)  # Each tile becomes ~64 pixels
            
            # Calculate visible tiles
            visible_tiles_x = int(1280 / tile_scaled) + 2  # +2 for partial tiles
            
            # Scroll position in tiles
            scroll_offset_pixels = int(self.road_x)
            scroll_offset_tiles = scroll_offset_pixels / 16  # Convert to tile units
            
            # Scale the road once for efficiency
            scaled_width = int(self.night_road.get_width() * scale_factor)
            scaled_height = int(self.night_road.get_height() * scale_factor)
            scaled_road = pygame.transform.scale(self.night_road, (scaled_width, scaled_height))
            
            # Draw seamlessly scrolling road (shifted down)
            offset_x = int(scroll_offset_tiles * tile_scaled) % scaled_width
            y_offset = 0  # Move the road down 200 pixels
            
            # Blit two copies for seamless loop
            surface.blit(scaled_road, (-offset_x, y_offset))
            surface.blit(scaled_road, (scaled_width - offset_x, y_offset))
        
        # Draw the blue car
        if self.blue_car:
            surface.blit(self.blue_car, (int(self.car_x), int(self.car_y)))

        # UI
        t = self.font.render(f"Time: {int(self.timer)}s", True, (255, 255, 255))
        surface.blit(t, (20, 20))
        hint = "Use WASD or Arrow Keys to move" if not self.crashed else "Crashed! Recovering..."
        hsurf = self.font.render(hint, True, (255, 255, 255))
        surface.blit(hsurf, (20, 50))
