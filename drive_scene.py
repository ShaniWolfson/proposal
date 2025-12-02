import pygame
import random
import importlib
import os
from scene import Scene


class DriveScene(Scene):
    """Driving scene with scrolling background and traffic cars.

    Args:
        vehicle: 'car' or 'uhaul' (currently unused)
        duration: seconds to auto-complete (default 35)
        time_of_day: 'night' or 'day' (default 'night')
        manager: Scene manager for transitions
    """

    def __init__(self, vehicle='car', duration=35.0, time_of_day='night', manager=None):
        super().__init__(manager)
        self.vehicle = vehicle
        self.duration = duration
        self.time_of_day = time_of_day
        self.timer = duration
        self.font = None
        
        # Constants
        self.PLAYER_CAR_SCALE = 2
        self.TRAFFIC_CAR_SCALE = 2
        self.ROAD_SCALE = 3.0
        self.DRIFT_BACK_SPEED = 40
        self.SCROLL_SPEED_BOOST = 1.2
        self.FRICTION = 5.0
        self.EXCLUDED_CARS = {9}  # Car #9 is empty space
        
        # Road and scrolling
        self.road_bg = None
        self.road_x = 0
        self.scroll_speed = 70
        self.road_top = 350  # Moved down from 360
        self.road_bottom = 730  # Moved down from 880
        self.road_left = 0
        self.road_right = 1000
        
        # Player car
        self.blue_car = None
        self.car_x = 200
        self.car_y = 720 // 2
        self.car_speed = 300  # Up/down
        self.car_speed_x = 200  # Left/right
        self.crashed = False
        self.crash_timer = 0.0
        self.bump_velocity_x = 0
        self.bump_velocity_y = 0
        
        # Traffic cars
        self.traffic_cars = []  # List of {x, y, sprite, speed}
        self.traffic_spawn_timer = 0.0
        self.traffic_spawn_interval = 3.0  # Spawn a car every 3 seconds
        self.next_car_index = 0  # Track which car to spawn next for cycling
        
        # Dialogue messages for collisions
        self.collision_messages = [
            "Hey watch where you are going!",
            "Hey speedy slow down!",
            "Watch it!",
            "Learn to drive!",
            "Everyone's always in a rush!",
            "Stay in your lane!",
            "What you got a hot date or something?"
        ]
        self.current_message = None
        self.message_timer = 0.0
        self.message_duration = 2.0  # Show message for 2 seconds
        self.message_cooldown = 0.0  # Cooldown before next message can appear
        self.message_cooldown_duration = 1.0  # Wait 1 second after message disappears
        
        # Fade out effect
        self.fade_out = False
        self.fade_alpha = 0

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.timer = self.duration
        self.crashed = False
        self.road_x = 0
        self.current_message = None
        self.message_timer = 0.0
        self.message_cooldown = 0.0
        
        # Load the road background based on time of day
        if self.time_of_day == 'day':
            road_path = os.path.join('art', 'backgrounds', 'date_drive', 'dayroad.png')
        else:
            road_path = os.path.join('art', 'backgrounds', 'date_drive', 'nightroad.png')
        self.road_bg = pygame.image.load(road_path).convert_alpha()
        
        # Load car sprites using the car_sprites loader
        from car_sprites import load_car_sprites
        vehicles_path = os.path.join('art', 'backgrounds', 'date_drive', "'90s vehicles.png")
        
        # Load all car sprites
        self.all_cars = load_car_sprites(vehicles_path, expected_cols=4, 
                                        directions=["left", "right", "front", "back"],
                                        split_first_col=True)
        
        # Choose and scale player car based on time of day
        car_index = self._get_player_car_index()
        car_sprite = self.all_cars[car_index]["right"]
        self.blue_car = pygame.transform.scale(
            car_sprite,
            (car_sprite.get_width() * self.PLAYER_CAR_SCALE, 
             car_sprite.get_height() * self.PLAYER_CAR_SCALE)
        )
        
        # Position car vertically centered in the drivable area
        self.car_y = self.road_top + (self.road_bottom - self.road_top - self.blue_car.get_height()) // 2
        
        # Initialize traffic
        self.traffic_cars = []
        self.traffic_spawn_timer = self.traffic_spawn_interval
        self.next_car_index = 0

    def _get_player_car_index(self):
        """Get player car index based on time of day."""
        return 12 if self.time_of_day == 'day' else 3
    
    def _get_available_car_indices(self):
        """Get list of car indices available for traffic (excludes player car and empty slots)."""
        player_car = self._get_player_car_index()
        return [i for i in range(len(self.all_cars)) 
                if i != player_car and i not in self.EXCLUDED_CARS]

    def handle_event(self, event: pygame.event.EventType):
        pass
    
    def spawn_traffic_car(self):
        """Spawn a traffic car on the road, cycling through available cars."""
        available_cars = self._get_available_car_indices()
        
        # Cycle through cars
        car_index = available_cars[self.next_car_index % len(available_cars)]
        self.next_car_index += 1
        
        car_sprite = self.all_cars[car_index]["right"]
        scaled_sprite = pygame.transform.scale(
            car_sprite,
            (car_sprite.get_width() * self.TRAFFIC_CAR_SCALE, 
             car_sprite.get_height() * self.TRAFFIC_CAR_SCALE)
        )
        
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
                current_scroll_speed = self.scroll_speed * self.SCROLL_SPEED_BOOST
            
            # Scroll the road to the right (simulating forward movement)
            self.road_x += current_scroll_speed * dt
            
            # Loop the road when it scrolls past the image width
            if self.road_bg:
                road_width = self.road_bg.get_width()
                if self.road_x >= road_width:
                    self.road_x -= road_width
            
            # Natural pull back - car drifts backward if not pressing right
            if not (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                self.car_x -= self.DRIFT_BACK_SPEED * dt
            
            # Apply bump velocity with friction
            if self.bump_velocity_x != 0 or self.bump_velocity_y != 0:
                self.car_x += self.bump_velocity_x * dt
                self.car_y += self.bump_velocity_y * dt
                # Apply friction to slow down bump
                self.bump_velocity_x *= (1.0 - self.FRICTION * dt)
                self.bump_velocity_y *= (1.0 - self.FRICTION * dt)
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
                            # Show random collision message (only if cooldown expired)
                            if self.message_cooldown <= 0:
                                self.current_message = random.choice(self.collision_messages)
                                self.message_timer = self.message_duration
                        
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
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.current_message = None
                # Start cooldown after message disappears
                self.message_cooldown = self.message_cooldown_duration
        
        # Update message cooldown
        if self.message_cooldown > 0:
            self.message_cooldown -= dt
        
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
        surface.fill((0, 0, 0))
        
        # Draw the scrolling road
        if self.road_bg:
            tile_scaled = int(16 * self.ROAD_SCALE)
            
            # Calculate scroll offset
            scroll_offset_pixels = int(self.road_x)
            scroll_offset_tiles = scroll_offset_pixels / 16
            
            # Scale road once
            scaled_width = int(self.road_bg.get_width() * self.ROAD_SCALE)
            scaled_height = int(self.road_bg.get_height() * self.ROAD_SCALE)
            scaled_road = pygame.transform.scale(self.road_bg, (scaled_width, scaled_height))
            
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
        
        # Draw collision message popup
        if self.current_message:
            # Create dialog box centered on screen
            box_width = 500
            box_height = 100
            box_x = (1280 - box_width) // 2
            box_y = 150
            
            # Draw semi-transparent background
            dialog_bg = pygame.Surface((box_width, box_height))
            dialog_bg.fill((40, 40, 50))
            dialog_bg.set_alpha(220)
            surface.blit(dialog_bg, (box_x, box_y))
            
            # Draw border
            pygame.draw.rect(surface, (200, 200, 220), (box_x, box_y, box_width, box_height), 3)
            
            # Draw message text (centered)
            message_font = pygame.font.SysFont(None, 36)
            text_surf = message_font.render(self.current_message, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
            surface.blit(text_surf, text_rect)
        
        # Draw fade out overlay
        if self.fade_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surface, (0, 0))
        hint = "Use WASD or Arrow Keys to move" if not self.crashed else "Crashed! Recovering..."
        hsurf = self.font.render(hint, True, (255, 255, 255))
        surface.blit(hsurf, (20, 50))
