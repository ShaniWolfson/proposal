import pygame
import random
import importlib
import os
from scene import Scene


class DriveScene(Scene):
    """Night road driving scene with scrolling background and traffic cars.

    Args:
        vehicle: 'car' or 'uhaul' (currently unused)
        duration: seconds to auto-complete (default 35)
        manager: Scene manager for transitions
    """

    def __init__(self, vehicle='car', duration=35.0, manager=None):
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
        self.scroll_speed = 100  # Road scrolling speed
        self.crashed = False
        self.crash_timer = 0.0
        self.bump_velocity_x = 0  # Smooth bump knockback velocity
        self.bump_velocity_y = 0
        
        # Traffic cars
        self.traffic_cars = []  # List of {x, y, sprite, speed}
        self.traffic_spawn_timer = 0.0
        self.traffic_spawn_interval = 3.0  # Spawn a car every 3 seconds
        self.next_car_index = 0  # Track which car to spawn next for cycling
        
        # Fade out effect
        self.fade_out = False
        self.fade_alpha = 0
        
        # Road boundaries (y coordinates with offset applied)
        self.road_top = 150 + 100  # y_offset + some margin for top of road
        self.road_bottom = 150 + 720 - 100  # y_offset + scaled_height - margin for bottom

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.timer = self.duration
        self.crashed = False
        self.road_x = 0
        
        # Set road boundaries (drivable area)
        self.road_top = 360  # Start of drivable area
        self.road_bottom = 880  # End of drivable area
        self.road_left = 0  # Left edge
        self.road_right = 1000  # Right edge
        
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
        
        # Initialize traffic cars list
        self.traffic_cars = []
        self.traffic_spawn_timer = self.traffic_spawn_interval
        self.next_car_index = 0  # Start cycling from first car

    def handle_event(self, event: pygame.event.EventType):
        pass
    
    def spawn_traffic_car(self):
        """Spawn a traffic car on the road, cycling through available cars."""
        # Get list of available cars (exclude car 3 which is the player)
        available_cars = [i for i in range(len(self.all_cars)) if i != 3]
        
        # Cycle through cars instead of random
        car_index = available_cars[self.next_car_index % len(available_cars)]
        self.next_car_index += 1
        
        # All traffic cars face right
        direction = "right"
        car_sprite = self.all_cars[car_index][direction]
        
        # Scale up 2x like player car
        scaled_sprite = pygame.transform.scale(car_sprite, 
                                              (car_sprite.get_width() * 2, 
                                               car_sprite.get_height() * 2))
        
        # Spawn on right side of screen, random Y within road bounds
        spawn_x = 1280  # Start just off screen to the right
        spawn_y = random.randint(self.road_top, self.road_bottom - scaled_sprite.get_height())
        
        # Check if this position overlaps with existing traffic cars
        spawn_rect = pygame.Rect(spawn_x, spawn_y, scaled_sprite.get_width(), scaled_sprite.get_height())
        for existing_car in self.traffic_cars:
            existing_rect = pygame.Rect(existing_car['x'], existing_car['y'],
                                       existing_car['sprite'].get_width(),
                                       existing_car['sprite'].get_height())
            if spawn_rect.colliderect(existing_rect):
                # Don't spawn if it would overlap
                return
        
        # Speed: negative to move left (slower than scroll speed so it appears to move back)
        speed = random.randint(-150, -80)
        
        self.traffic_cars.append({
            'x': spawn_x,
            'y': spawn_y,
            'sprite': scaled_sprite,
            'speed': speed
        })

    def update(self, dt: float):
        if self.crashed:
            self.crash_timer -= dt
            if self.crash_timer <= 0:
                self.crashed = False
        else:
            # Handle up/down/left/right movement
            keys = pygame.key.get_pressed()
            
            # Dynamic scroll speed - speed up when moving right
            current_scroll_speed = self.scroll_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                current_scroll_speed = self.scroll_speed * 1.2  # 20% faster when moving right (reduced for smoother feel)
            
            # Scroll the road to the right (simulating forward movement)
            self.road_x += current_scroll_speed * dt
            
            # Loop the road when it scrolls past the image width
            if self.night_road:
                road_width = self.night_road.get_width()
                if self.road_x >= road_width:
                    self.road_x -= road_width
            
            # Natural pull back - car drifts backward if not pressing right
            drift_back_speed = 40  # Pixels per second
            if not (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                # Drift backward naturally
                self.car_x -= drift_back_speed * dt
            
            # Apply bump velocity with friction
            if self.bump_velocity_x != 0 or self.bump_velocity_y != 0:
                self.car_x += self.bump_velocity_x * dt
                self.car_y += self.bump_velocity_y * dt
                # Apply friction to slow down bump
                friction = 5.0
                self.bump_velocity_x *= (1.0 - friction * dt)
                self.bump_velocity_y *= (1.0 - friction * dt)
                # Stop if very slow
                if abs(self.bump_velocity_x) < 1:
                    self.bump_velocity_x = 0
                if abs(self.bump_velocity_y) < 1:
                    self.bump_velocity_y = 0
            
            # Handle movement input
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
                # Clamp to road boundaries (all edges)
                self.car_y = max(self.road_top, min(self.car_y, self.road_bottom - car_height))
                self.car_x = max(self.road_left, min(self.car_x, self.road_right - car_width))
            
            # Update traffic cars
            self.traffic_spawn_timer -= dt
            if self.traffic_spawn_timer <= 0:
                self.spawn_traffic_car()
                self.traffic_spawn_timer = self.traffic_spawn_interval
            
            # Move traffic cars and remove off-screen ones
            for car in self.traffic_cars[:]:
                car['x'] += car['speed'] * dt
                # Remove if off screen to the left
                if car['x'] + car['sprite'].get_width() < 0:
                    self.traffic_cars.remove(car)
            
            # Check collision with traffic cars - proper blocking collision
            if self.blue_car:
                player_rect = pygame.Rect(self.car_x, self.car_y, car_width, car_height)
                for traffic_car in self.traffic_cars:
                    traffic_rect = pygame.Rect(traffic_car['x'], traffic_car['y'], 
                                              traffic_car['sprite'].get_width(), 
                                              traffic_car['sprite'].get_height())
                    if player_rect.colliderect(traffic_rect):
                        # Calculate overlap to push player back properly
                        overlap_left = (player_rect.right - traffic_rect.left)
                        overlap_right = (traffic_rect.right - player_rect.left)
                        overlap_top = (player_rect.bottom - traffic_rect.top)
                        overlap_bottom = (traffic_rect.bottom - player_rect.top)
                        
                        # Find smallest overlap to resolve collision
                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                        
                        if not self.crashed:
                            # Brief bump effect only on first collision
                            self.crashed = True
                            self.crash_timer = 0.2
                            self.bump_velocity_x = -150
                            self.bump_velocity_y = random.randint(-50, 50)
                        
                        # Push player out of collision based on smallest overlap
                        if min_overlap == overlap_left:
                            self.car_x = traffic_rect.left - car_width - 2
                        elif min_overlap == overlap_right:
                            self.car_x = traffic_rect.right + 2
                        elif min_overlap == overlap_top:
                            self.car_y = traffic_rect.top - car_height - 2
                        elif min_overlap == overlap_bottom:
                            self.car_y = traffic_rect.bottom + 2

            self.timer -= dt
            if self.timer <= 0 and not self.fade_out:
                self.fade_out = True
        
        # Handle fade out
        if self.fade_out:
            self.fade_alpha += dt * 150  # Fade over ~1.7 seconds
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # Transition to apartment scene
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
            # Scale road to 3.5x for better visibility
            scale_factor = 3.5
            tile_scaled = int(16 * scale_factor)
            
            # Calculate scroll offset
            scroll_offset_pixels = int(self.road_x)
            scroll_offset_tiles = scroll_offset_pixels / 16
            
            # Scale road once
            scaled_width = int(self.night_road.get_width() * scale_factor)
            scaled_height = int(self.night_road.get_height() * scale_factor)
            scaled_road = pygame.transform.scale(self.night_road, (scaled_width, scaled_height))
            
            # Draw two copies for seamless scrolling loop
            offset_x = int(scroll_offset_tiles * tile_scaled) % scaled_width
            surface.blit(scaled_road, (-offset_x, 0))
            surface.blit(scaled_road, (scaled_width - offset_x, 0))
        
        # Draw traffic cars
        for traffic_car in self.traffic_cars:
            surface.blit(traffic_car['sprite'], (int(traffic_car['x']), int(traffic_car['y'])))
        
        # Draw the blue car
        if self.blue_car:
            surface.blit(self.blue_car, (int(self.car_x), int(self.car_y)))

        # UI
        t = self.font.render(f"Time: {int(self.timer)}s", True, (255, 255, 255))
        surface.blit(t, (10, 10))
        
        # Draw fade out overlay
        if self.fade_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surface, (0, 0))
        hint = "Use WASD or Arrow Keys to move" if not self.crashed else "Crashed! Recovering..."
        hsurf = self.font.render(hint, True, (255, 255, 255))
        surface.blit(hsurf, (20, 50))
