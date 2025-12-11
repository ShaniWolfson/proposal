import pygame
import random
import math
from ..core.scene import Scene


class DisneyScene(Scene):
    """Disney World scene: characters kiss at castle with fireworks."""

    # Constants
    TIMER_DURATION = 30.0
    HEART_DELAY = 5.0
    HEART_GROW_SPEED = 0.8
    HEART_BASE_SIZE = 350
    KISS_ANIMATION_SPEED = 0.3
    HINT_FADE_SPEED = 200
    FIREWORK_SPAWN_INTERVAL = 0.3
    FIREWORK_PARTICLES = 20
    STAR_COUNT = 105
    
    # Character positions
    MARIA_START_X_OFFSET = -102
    MARIA_END_X_OFFSET = -80
    SHANI_START_X_OFFSET = -26
    SHANI_END_X_OFFSET = -48
    CHAR_Y_OFFSET = 230
    CHAR_SCALE = 128
    
    # Colors
    SKY_COLOR = (30, 50, 120)
    GROUND_COLOR = (60, 80, 60)
    STAR_COLOR = (255, 255, 200)
    HINT_COLOR = (240, 200, 200)
    TITLE_COLOR = (255, 255, 255)
    
    FIREWORK_COLORS = [
        (255, 100, 100),  # Red
        (100, 255, 100),  # Green
        (100, 100, 255),  # Blue
        (255, 255, 100),  # Yellow
        (255, 100, 255),  # Magenta
        (100, 255, 255),  # Cyan
    ]
    
    STAR_POSITIONS = [
        (80, 40), (250, 90), (450, 30), (680, 70), (890, 45), (950, 110),
        (150, 200), (380, 250), (620, 280), (820, 185), (1000, 240),
        (40, 350), (320, 420), (540, 380), (750, 340), (920, 450),
        (190, 165), (410, 315), (580, 145), (780, 420), (870, 260),
        (110, 455), (290, 225), (500, 365), (710, 155), (960, 395),
        (60, 330), (350, 180), (640, 460), (800, 235), (1010, 160),
        (200, 400), (470, 490), (730, 270), (900, 520), (560, 510),
        (130, 75), (340, 120), (520, 85), (670, 135), (850, 95), (980, 145),
        (220, 310), (440, 275), (590, 395), (770, 325), (930, 365),
        (95, 480), (280, 440), (485, 505), (655, 470), (845, 515),
        (165, 220), (395, 190), (545, 240), (715, 210), (885, 180),
        (45, 410), (305, 385), (510, 425), (695, 395), (905, 475),
        (175, 130), (365, 95), (535, 160), (725, 115), (895, 125),
        (85, 290), (270, 340), (465, 320), (625, 355), (815, 305),
        (120, 510), (330, 485), (555, 455), (740, 525), (940, 490),
        (210, 65), (420, 50), (610, 105), (790, 75), (970, 85),
        (140, 370), (360, 410), (575, 430), (765, 380), (925, 415),
        (70, 195), (295, 155), (490, 210), (685, 175), (880, 230),
        (155, 445), (385, 525), (520, 495), (720, 460), (915, 505),
        (100, 115), (315, 140), (505, 120), (690, 150), (910, 165),
        (50, 260), (260, 290), (455, 270), (635, 310), (825, 285)
    ]

    def __init__(self, manager=None):
        super().__init__(manager)
        self.music_file = "art/music/apartment/first_date.mp3"  # Continue apartment music
        self.font = None
        self.timer = self.TIMER_DURATION
        self.kissed = False
        
        # Sprites and images
        self.maria_sprite = None
        self.shani_sprite = None
        self.castle_image = None
        self.heart_image = None
        
        # Animation state
        self.fireworks = []
        self.firework_timer = 0
        self.heart_scale = 0
        self.heart_delay_timer = 0
        self.hint_alpha = 0
        self.hint_fade_direction = 1
        self.star_alphas = {}
        self.kiss_animation_progress = 0
        
        # Photo montage (after heart animation)
        self.photos = []
        self.photo_positions = []  # List of (x, y) positions for each photo
        self.montage_active = False
        self.current_photo_index = 0
        self.photo_display_time = 0.15  # Time each photo stays on screen
        self.photo_fade_time = 0.15  # Fade in/out duration
        self.photo_timer = 0.0
        self.displayed_photos = []  # List of (photo, position, alpha) for photos on screen

    def start(self):
        """Initialize scene resources and state."""
        super().start()  # Call parent to handle music
        self.font = pygame.font.SysFont(None, 36)
        self._reset_state()
        self._initialize_stars()
        self._load_assets()
        self._load_photos()

    def _reset_state(self):
        """Reset all animation state variables."""
        self.timer = self.TIMER_DURATION
        self.kissed = False
        self.fireworks = []
        self.firework_timer = 0
        self.heart_scale = 0
        self.heart_delay_timer = 0
        self.hint_alpha = 0
        self.hint_fade_direction = 1
        self.kiss_animation_progress = 0

    def _initialize_stars(self):
        """Initialize star twinkling data."""
        self.star_alphas = {}
        for i in range(self.STAR_COUNT):
            self.star_alphas[i] = {
                'alpha': random.randint(80, 255),
                'speed': random.uniform(150, 300),
                'direction': random.choice([-1, 1])
            }

    def _load_assets(self):
        """Load all image assets."""
        try:
            self.castle_image = pygame.image.load("art/scenes/disney/castle.png").convert_alpha()
        except Exception as e:
            print(f"Failed to load castle image: {e}")
        
        try:
            self.heart_image = pygame.image.load("art/scenes/bumble/heart.png").convert_alpha()
        except Exception as e:
            print(f"Failed to load heart image: {e}")
        
        # Load character sprites
        self._load_character_sprite("maria", 3, lambda s: setattr(self, 'maria_sprite', s))
        self._load_character_sprite("shani", 1, lambda s: setattr(self, 'shani_sprite', s))

    def _load_character_sprite(self, name, row, setter):
        """Helper to load a character sprite from spritesheet."""
        try:
            sheet = pygame.image.load(f"art/characters/{name}/idle.png").convert_alpha()
            sprite = sheet.subsurface(pygame.Rect(0, row * 64, 64, 64))
            setter(sprite)
        except Exception as e:
            print(f"Failed to load {name} sprite: {e}")
    
    def _load_photos(self):
        """Load real photos for floating around castle."""
        import os
        photo_folder = os.path.join('art', 'photos')
        
        # Try to load real photos first
        loaded_photos = False
        try:
            if os.path.isdir(photo_folder):
                photo_files = [f for f in os.listdir(photo_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for photo_file in photo_files:
                    try:
                        photo_path = os.path.join(photo_folder, photo_file)
                        photo = pygame.image.load(photo_path).convert_alpha()
                        # Resize to reasonable size (max 150px on longest side)
                        w, h = photo.get_size()
                        scale_factor = min(150 / w, 150 / h)
                        new_w = int(w * scale_factor)
                        new_h = int(h * scale_factor)
                        photo = pygame.transform.scale(photo, (new_w, new_h))
                        self.photos.append(photo)
                        loaded_photos = True
                    except Exception as e:
                        print(f"Could not load photo {photo_file}: {e}")
        except Exception as e:
            print(f"Could not load photos: {e}")
        
        # If no photos found, create sample placeholder rectangles
        if not loaded_photos:
            print("No photos found, using placeholder rectangles")
            import random
            for i in range(50):
                # Generate random pastel colors
                color = (
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(150, 255)
                )
                photo = pygame.Surface((180, 180))
                photo.fill(color)
                pygame.draw.rect(photo, (100, 100, 100), (0, 0, 180, 180), 3)
                font = pygame.font.Font(None, 24)
                text = font.render(f"#{i+1}", True, (50, 50, 50))
                text_rect = text.get_rect(center=(90, 90))
                photo.blit(text, text_rect)
                self.photos.append(photo)

    def handle_event(self, event: pygame.event.EventType):
        """Handle keyboard input."""
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.kissed = True

    def update(self, dt: float):
        """Update scene state."""
        self._update_stars(dt)
        self._update_hint_fade(dt)
        self._update_photos(dt)
        
        if self.kissed:
            self._update_kiss_sequence(dt)
    
    def _update_photos(self, dt):
        """Update photo montage - add photos one by one to fill screen."""
        if not self.montage_active or not self.photos:
            return
        
        self.photo_timer += dt
        total_cycle = self.photo_fade_time * 2 + self.photo_display_time
        
        # Check if it's time to add a new photo
        if self.photo_timer >= total_cycle:
            # Add the current photo to the displayed list with a random position
            if self.current_photo_index < len(self.photos):
                import random
                # Screen dimensions
                screen_w, screen_h = 1024, 768
                
                # Try to find a position that doesn't overlap too much with existing photos
                min_distance = 140  # Minimum distance between photo centers
                max_attempts = 50
                best_x, best_y = None, None
                best_min_dist = 0
                
                for attempt in range(max_attempts):
                    x = random.randint(90, screen_w - 90)
                    y = random.randint(90, screen_h - 90)
                    
                    # Calculate minimum distance to any existing photo
                    if self.displayed_photos:
                        min_dist = min(
                            ((x - p['x'])**2 + (y - p['y'])**2)**0.5
                            for p in self.displayed_photos
                        )
                    else:
                        min_dist = float('inf')
                    
                    # If we found a good spot with enough distance, use it
                    if min_dist >= min_distance:
                        best_x, best_y = x, y
                        break
                    
                    # Otherwise, keep track of the best position so far
                    if min_dist > best_min_dist:
                        best_min_dist = min_dist
                        best_x, best_y = x, y
                
                x, y = best_x, best_y
                
                self.displayed_photos.append({
                    'photo': self.photos[self.current_photo_index],
                    'x': x,
                    'y': y,
                    'alpha': 0,
                    'timer': 0
                })
                
                self.current_photo_index += 1
                if self.current_photo_index >= len(self.photos):
                    self.current_photo_index = 0  # Loop back
            
            self.photo_timer = 0.0
        
        # Update alpha for all displayed photos
        for photo_data in self.displayed_photos:
            photo_data['timer'] += dt
            if photo_data['timer'] < self.photo_fade_time:
                # Fade in
                photo_data['alpha'] = int(255 * (photo_data['timer'] / self.photo_fade_time))
            else:
                # Stay at full alpha
                photo_data['alpha'] = 255

    def _update_stars(self, dt):
        """Update star twinkling animation."""
        for star_data in self.star_alphas.values():
            star_data['alpha'] += star_data['direction'] * star_data['speed'] * dt
            if star_data['alpha'] >= 255:
                star_data['alpha'] = 255
                star_data['direction'] = -1
            elif star_data['alpha'] <= 80:
                star_data['alpha'] = 80
                star_data['direction'] = 1

    def _update_hint_fade(self, dt):
        """Update hint text fade animation."""
        if not self.kissed:
            self.hint_alpha += self.hint_fade_direction * dt * self.HINT_FADE_SPEED
            if self.hint_alpha >= 255:
                self.hint_alpha = 255
                self.hint_fade_direction = -1
            elif self.hint_alpha <= 0:
                self.hint_alpha = 0
                self.hint_fade_direction = 1

    def _update_kiss_sequence(self, dt):
        """Update all kiss-related animations."""
        self.timer -= dt
        
        # Animate characters moving together
        if self.kiss_animation_progress < 1.0:
            self.kiss_animation_progress = min(1.0, self.kiss_animation_progress + dt * self.KISS_ANIMATION_SPEED)
        
        # Update heart growth
        self.heart_delay_timer += dt
        if self.heart_delay_timer >= self.HEART_DELAY and self.heart_scale < 1.0:
            self.heart_scale = min(1.0, self.heart_scale + dt * self.HEART_GROW_SPEED)
            # Start photo montage when heart reaches full size
            if self.heart_scale >= 1.0:
                self.montage_active = True
        
        # Spawn and update fireworks
        self._update_fireworks(dt)
        
        # Transition to next scene
        if self.timer <= 0:
            self._transition_to_moving_scene()

    def _update_fireworks(self, dt):
        """Spawn and update firework particles."""
        self.firework_timer += dt
        if self.firework_timer >= self.FIREWORK_SPAWN_INTERVAL:
            self.firework_timer = 0
            self._spawn_firework_burst()
        
        # Update existing particles
        for f in self.fireworks[:]:
            f['t'] += dt
            f['x'] += f['vx'] * dt
            f['y'] += f['vy'] * dt
            f['vy'] += 100 * dt  # Gravity
            if f['t'] >= f['max_t']:
                self.fireworks.remove(f)

    def _spawn_firework_burst(self):
        """Create a burst of firework particles."""
        center_x = random.randint(100, 900)
        center_y = random.randint(80, 200)
        color = random.choice(self.FIREWORK_COLORS)
        
        for _ in range(self.FIREWORK_PARTICLES):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.fireworks.append({
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                't': 0,
                'max_t': random.uniform(1.0, 2.0)
            })

    def _transition_to_moving_scene(self):
        """Transition to the moving in together scene."""
        from .transition_scene import TransitionScene
        from .moving_scene import MovingScene
        next_scene = TransitionScene(
            "And then we decided to move in together!\nTime to get the UHaul!",
            MovingScene,
            self.manager,
            duration=7.0
        )
        self.manager.go_to(next_scene)

    def draw(self, surface: pygame.Surface):
        """Render the scene."""
        w, h = surface.get_size()
        
        # Draw background
        surface.fill(self.SKY_COLOR)
        self._draw_stars(surface)
        self._draw_ground(surface, w, h)
        self._draw_castle(surface, w, h)
        
        # Draw characters
        char_y = h - self.CHAR_Y_OFFSET
        self._draw_characters(surface, w, char_y)
        
        # Draw UI (heart and fireworks)
        self._draw_hint_or_effects(surface, w, h, char_y)
        
        # Draw photo montage (last, so it overlays everything including the heart)
        if self.montage_active:
            self._draw_photos(surface)
    
    def _draw_photos(self, surface):
        """Draw all displayed photos filling the screen."""
        if not self.displayed_photos:
            return
        
        # Draw each photo at its position with its current alpha
        for photo_data in self.displayed_photos:
            if photo_data['alpha'] <= 0:
                continue
            
            photo = photo_data['photo']
            
            # Create a copy with alpha applied
            photo_with_alpha = photo.copy()
            photo_with_alpha.set_alpha(int(photo_data['alpha']))
            
            # Position the photo
            photo_rect = photo_with_alpha.get_rect(center=(int(photo_data['x']), int(photo_data['y'])))
            
            # Draw subtle shadow
            shadow = pygame.Surface(photo_with_alpha.get_size(), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            shadow_rect = shadow.get_rect(center=(int(photo_data['x'] + 3), int(photo_data['y'] + 3)))
            surface.blit(shadow, shadow_rect)
            
            # Draw photo
            surface.blit(photo_with_alpha, photo_rect)

    def _draw_stars(self, surface):
        """Draw twinkling stars."""
        for i, (x, y) in enumerate(self.STAR_POSITIONS):
            alpha = int(self.star_alphas.get(i, {}).get('alpha', 255))
            star_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, (*self.STAR_COLOR, alpha), (3, 3), 2)
            surface.blit(star_surface, (x - 3, y - 3))

    def _draw_ground(self, surface, w, h):
        """Draw the ground."""
        pygame.draw.rect(surface, self.GROUND_COLOR, (0, h - 150, w, 150))

    def _draw_castle(self, surface, w, h):
        """Draw the castle background."""
        if not self.castle_image:
            return
        
        castle_width = int(w * 1.2)
        castle_height = int(self.castle_image.get_height() * (castle_width / self.castle_image.get_width()))
        scaled_castle = pygame.transform.scale(self.castle_image, (castle_width, castle_height))
        castle_x = (w - castle_width) // 2 - 3
        castle_y = h - 150 - castle_height + 320
        surface.blit(scaled_castle, (castle_x, castle_y))

    def _draw_characters(self, surface, w, char_y):
        """Draw Maria and Shani with interpolated positions."""
        # Calculate positions
        maria_x = w // 2 + self.MARIA_START_X_OFFSET + \
                  (self.MARIA_END_X_OFFSET - self.MARIA_START_X_OFFSET) * self.kiss_animation_progress
        shani_x = w // 2 + self.SHANI_START_X_OFFSET + \
                  (self.SHANI_END_X_OFFSET - self.SHANI_START_X_OFFSET) * self.kiss_animation_progress
        
        # Draw sprites
        if self.maria_sprite:
            maria_scaled = pygame.transform.scale(self.maria_sprite, (self.CHAR_SCALE, self.CHAR_SCALE))
            surface.blit(maria_scaled, (maria_x, char_y))
        
        if self.shani_sprite:
            shani_scaled = pygame.transform.scale(self.shani_sprite, (self.CHAR_SCALE, self.CHAR_SCALE))
            surface.blit(shani_scaled, (shani_x, char_y))

    def _draw_title(self, surface):
        """Draw the scene title."""
        title = self.font.render("Disney World — A Kiss at the Castle", True, self.TITLE_COLOR)
        surface.blit(title, (20, 20))

    def _draw_hint_or_effects(self, surface, w, h, char_y):
        """Draw either the hint text or kiss effects."""
        if not self.kissed:
            self._draw_hint(surface, w, h)
        else:
            self._draw_fireworks(surface)
            self._draw_heart(surface, w, char_y)

    def _draw_hint(self, surface, w, h):
        """Draw the 'Press SPACE to kiss' hint."""
        hint = self.font.render("Press SPACE to kiss", True, self.HINT_COLOR)
        hint.set_alpha(int(self.hint_alpha))
        surface.blit(hint, ((w - hint.get_width()) // 2, h - 70))

    def _draw_fireworks(self, surface):
        """Draw firework particles."""
        for f in self.fireworks:
            alpha = int(255 * (1 - f['t'] / f['max_t']))
            if alpha > 0:
                particle_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, f['color'], (6, 6), 6)
                surface.blit(particle_surface, (int(f['x']) - 6, int(f['y']) - 6))

    def _draw_heart(self, surface, w, char_y):
        """Draw the growing heart."""
        if not self.heart_image or self.heart_scale <= 0:
            return
        
        # Calculate heart position (centered between characters)
        maria_center = (w // 2 + self.MARIA_END_X_OFFSET) + 64
        shani_center = (w // 2 + self.SHANI_END_X_OFFSET) + 64
        heart_center_x = (maria_center + shani_center) // 2
        heart_center_y = char_y + 64
        
        # Scale and draw heart
        current_size = int(self.HEART_BASE_SIZE * self.heart_scale)
        if current_size > 1:
            scaled_heart = pygame.transform.scale(self.heart_image, (current_size, current_size))
            heart_x = heart_center_x - current_size // 2
            heart_y = heart_center_y - current_size // 2
            surface.blit(scaled_heart, (heart_x, heart_y))
