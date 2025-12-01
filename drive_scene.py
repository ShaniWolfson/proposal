import pygame
import random
import importlib
import os
from scene import Scene


class DriveScene(Scene):
    """Night road driving scene with scrolling background.

    vehicle: 'car' or 'uhaul'
    duration: seconds to auto-complete (default 10)
    """

    def __init__(self, vehicle='car', duration=10.0, manager=None):
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
        self.car_x = 200  # Fixed position on left side
        self.car_y = 720 // 2  # Center vertically
        self.car_speed = 300  # Up/down movement speed
        
        self.obstacles = []
        self.spawn_timer = 0.0
        self.scroll_speed = 100  # Road scrolling speed (slowed down)
        self.crashed = False
        self.crash_timer = 0.0

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.timer = self.duration
        self.obstacles = []
        self.spawn_timer = 0.5
        self.crashed = False
        self.road_x = 0
        
        # Load the night road background
        road_path = os.path.join('art', 'backgrounds', 'date_drive', 'nightroad.png')
        self.night_road = pygame.image.load(road_path).convert_alpha()
        
        # Load car sprites using the loader
        vehicles_path = os.path.join('art', 'backgrounds', 'date_drive')
        veh_files = os.listdir(vehicles_path)
        veh_file = [f for f in veh_files if 'vehicles' in f.lower()][0]
        vehicles_sheet = pygame.image.load(os.path.join(vehicles_path, veh_file)).convert_alpha()
        
        # Sheet is 224x960 with 2 columns (left, right facing)
        sheet_w, sheet_h = vehicles_sheet.get_size()
        cols = 2
        sprite_w = sheet_w // cols  # 112 pixels per column
        
        # Detect number of rows - each car has variable height
        # We'll use the detected car positions
        car_positions = [
            (7, 57),    # Car 0
            (71, 57),   # Car 1
            (135, 57),  # Car 2
            (199, 57),  # Car 3 (yellow car)
            (265, 55),  # Car 4
            (331, 53),  # Car 5
            (395, 53),  # Car 6
            (459, 53),  # Car 7
            (528, 48),  # Car 8
            (587, 53),  # Car 9
            (649, 55),  # Car 10
            (713, 55),  # Car 11
            (775, 57),  # Car 12
            (840, 56),  # Car 13
            (907, 53),  # Car 14
        ]
        
        # Extract Car #3 (yellow, 4th car, 0-indexed as 3)
        car_index = 3
        car_start_y, car_height = car_positions[car_index]
        
        # Get right-facing version (column 1)
        car_rect = pygame.Rect(sprite_w, car_start_y, sprite_w, car_height)
        car_sprite = vehicles_sheet.subsurface(car_rect).copy()
        
        # Scale up 2x for visibility
        self.blue_car = pygame.transform.scale(car_sprite, (sprite_w * 2, car_height * 2))
        
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
            
            # Handle up/down movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.car_y -= int(self.car_speed * dt)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.car_y += int(self.car_speed * dt)

            # Clamp car position to screen bounds
            if self.blue_car:
                car_height = self.blue_car.get_height()
                self.car_y = max(0, min(self.car_y, 720 - car_height))

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
            # Map is 300 tiles wide x 16 tiles tall (4800px wide x 256px tall at 16px per tile)
            # Show 16x16 tiles at a time, scaled to 1280x720
            # Each tile is 16x16 pixels (4800 / 300 = 16px per tile)
            tile_size = 16  # Each tile is 16x16 pixels
            
            # We want to show 16x16 tiles (same as apartment/dinner scenes)
            view_width = tile_size * 16
            view_height = tile_size * 16
            
            # Calculate which section to show based on scroll position
            offset_x = int(self.road_x) % self.night_road.get_width()
            
            # Extract the 16x16 tile section from the background
            # Since background is only 256px tall, we'll need to handle it differently
            # Let's just show a 1280x720 section and scroll it
            section_width = min(1280, self.night_road.get_width())
            section_height = self.night_road.get_height()
            
            # Create a view surface showing the scrolling section
            view = pygame.Surface((1280, 720))
            view.fill((0, 0, 0))
            
            # Scale the road section to fit screen
            offset = int(self.road_x % self.night_road.get_width())
            
            # Blit two copies for seamless scrolling at native resolution
            # Road is 256px tall, we need to show 16 tiles (256px) centered in 720px screen
            # Scale up to fill screen better: 720/256 = 2.8125x
            scale = 720 / self.night_road.get_height()
            scaled_width = int(self.night_road.get_width() * scale)
            scaled_height = 720
            scaled_road = pygame.transform.scale(self.night_road, (scaled_width, scaled_height))
            
            for i in range(2):
                x_pos = -int(offset * scale) + (i * scaled_width)
                view.blit(scaled_road, (x_pos, 0))
            
            surface.blit(view, (0, 0))
        
        # Draw the blue car
        if self.blue_car:
            surface.blit(self.blue_car, (int(self.car_x), int(self.car_y)))

        # UI
        t = self.font.render(f"Time: {int(self.timer)}s", True, (255, 255, 255))
        surface.blit(t, (20, 20))
        hint = "Use W/S or Up/Down to steer" if not self.crashed else "Crashed! Recovering..."
        hsurf = self.font.render(hint, True, (255, 255, 255))
        surface.blit(hsurf, (20, 50))
