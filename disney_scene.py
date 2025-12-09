import pygame
from scene import Scene


class DisneyScene(Scene):
    """Quick Disney World scene: walk up together and kiss at castle with fireworks."""

    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.timer = 10.0
        self.kissed = False
        self.maria_sprite = None
        self.shani_sprite = None
        self.castle_image = None
        self.heart_image = None
        self.fireworks = []
        self.firework_timer = 0
        self.heart_scale = 0
        self.heart_grow_speed = 0.8
        self.heart_delay = 5.0
        self.heart_delay_timer = 0
        self.hint_alpha = 0
        self.hint_fade_direction = 1
        self.star_alphas = {}  # Track alpha for each star
        self.kiss_animation_progress = 0  # 0 = apart, 1 = together

    def start(self):
        self.font = pygame.font.SysFont(None, 36)
        self.timer = 10.0
        self.kissed = False
        self.fireworks = []
        self.firework_timer = 0
        self.heart_scale = 0
        self.heart_grow_speed = 0.8
        self.heart_delay = 5.0
        self.heart_delay_timer = 0
        self.hint_alpha = 0
        self.hint_fade_direction = 1
        self.kiss_animation_progress = 0
        
        # Initialize star twinkling
        import random
        self.star_alphas = {}
        for i in range(105):  # Number of stars
            self.star_alphas[i] = {
                'alpha': random.randint(80, 255),
                'speed': random.uniform(150, 300),
                'direction': random.choice([-1, 1])
            }
        
        # Load castle image
        try:
            self.castle_image = pygame.image.load("art/backgrounds/castle.png").convert_alpha()
        except Exception as e:
            print(f"Failed to load castle image: {e}")
        
        # Load heart image
        try:
            self.heart_image = pygame.image.load("art/backgrounds/heart.png").convert_alpha()
        except Exception as e:
            print(f"Failed to load heart image: {e}")
        
        # Load Maria sprite - facing right for kissing
        # Use idle.png row facing right (row 3, column 0 for standing/idle right)
        try:
            maria_sheet = pygame.image.load("art/characters/maria/idle.png").convert_alpha()
            # Each sprite is 64x64, row 3 (facing right), column 0
            maria_x = 0 * 64
            maria_y = 3 * 64
            self.maria_sprite = maria_sheet.subsurface(pygame.Rect(maria_x, maria_y, 64, 64))
        except Exception as e:
            print(f"Failed to load Maria sprite: {e}")
        
        # Load Shani sprite - facing left for kissing
        # Use idle.png row facing left (row 1, column 0)
        try:
            shani_sheet = pygame.image.load("art/characters/shani/idle.png").convert_alpha()
            # Each sprite is 64x64, row 1 (facing left), column 0
            shani_x = 0 * 64
            shani_y = 1 * 64
            self.shani_sprite = shani_sheet.subsurface(pygame.Rect(shani_x, shani_y, 64, 64))
        except Exception as e:
            print(f"Failed to load Shani sprite: {e}")

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.kissed = True

    def update(self, dt: float):
        # Update star twinkling
        for star_id, star_data in self.star_alphas.items():
            star_data['alpha'] += star_data['direction'] * star_data['speed'] * dt
            if star_data['alpha'] >= 255:
                star_data['alpha'] = 255
                star_data['direction'] = -1
            elif star_data['alpha'] <= 80:
                star_data['alpha'] = 80
                star_data['direction'] = 1
        
        # Update hint fade in/out animation
        if not self.kissed:
            self.hint_alpha += self.hint_fade_direction * dt * 200
            if self.hint_alpha >= 255:
                self.hint_alpha = 255
                self.hint_fade_direction = -1
            elif self.hint_alpha <= 0:
                self.hint_alpha = 0
                self.hint_fade_direction = 1
        
        if self.kissed:
            self.timer -= dt
            
            # Animate characters moving together
            if self.kiss_animation_progress < 1.0:
                self.kiss_animation_progress += dt * 0.3  # 0.3 = slower animation speed
                if self.kiss_animation_progress > 1.0:
                    self.kiss_animation_progress = 1.0
            
            # Increment delay timer
            self.heart_delay_timer += dt
            
            # Grow the heart after delay
            if self.heart_delay_timer >= self.heart_delay:
                if self.heart_scale < 1.0:
                    self.heart_scale += dt * self.heart_grow_speed
                    if self.heart_scale > 1.0:
                        self.heart_scale = 1.0
            
            # Spawn fireworks periodically
            self.firework_timer += dt
            if self.firework_timer >= 0.3:  # Spawn every 0.3 seconds
                self.firework_timer = 0
                import random
                import math
                # Spawn a burst of firework particles
                center_x = random.randint(100, 900)
                center_y = random.randint(80, 200)
                color = random.choice([
                    (255, 100, 100),  # Red
                    (100, 255, 100),  # Green
                    (100, 100, 255),  # Blue
                    (255, 255, 100),  # Yellow
                    (255, 100, 255),  # Magenta
                    (100, 255, 255),  # Cyan
                ])
                # Create burst pattern
                for _ in range(20):
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
            
            # Update firework particles
            for f in self.fireworks[:]:
                f['t'] += dt
                f['x'] += f['vx'] * dt
                f['y'] += f['vy'] * dt
                f['vy'] += 100 * dt  # Gravity
                if f['t'] >= f['max_t']:
                    self.fireworks.remove(f)
            
            if self.timer <= 0:
                # Transition to moving in together scene
                from transition_scene import TransitionScene
                from moving_scene import MovingScene
                next_scene = TransitionScene(
                    "And then we decided to move in together! Time to get the UHaul!",
                    MovingScene,
                    self.manager,
                    duration=10.0
                )
                self.manager.go_to(next_scene)

    def draw(self, surface: pygame.Surface):
        w, h = surface.get_size()
        
        # Sky background - twilight blue
        surface.fill((30, 50, 120))
        
        # Draw stars - spread across the entire sky
        star_positions = [
            (80, 40), (250, 90), (450, 30), (680, 70), (890, 45), (950, 110),
            (150, 200), (380, 250), (620, 280), (820, 185), (1000, 240),
            (40, 350), (320, 420), (540, 380), (750, 340), (920, 450),
            (190, 165), (410, 315), (580, 145), (780, 420), (870, 260),
            (110, 455), (290, 225), (500, 365), (710, 155), (960, 395),
            (60, 330), (350, 180), (640, 460), (800, 235), (1010, 160),
            (200, 400), (470, 490), (730, 270), (900, 520), (560, 510),
            # Additional stars
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
        for i, (x, y) in enumerate(star_positions):
            alpha = int(self.star_alphas[i]['alpha']) if i in self.star_alphas else 255
            star_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            color_with_alpha = (255, 255, 200, alpha)
            pygame.draw.circle(star_surface, color_with_alpha, (3, 3), 2)
            surface.blit(star_surface, (x - 3, y - 3))
        
        # Ground
        pygame.draw.rect(surface, (60, 80, 60), (0, h - 150, w, 150))
        
        # Draw castle image if loaded
        if self.castle_image:
            # Scale castle to fit nicely in the scene
            castle_width = int(w *1.2)  # 80% of screen width
            castle_height = int(self.castle_image.get_height() * (castle_width / self.castle_image.get_width()))
            scaled_castle = pygame.transform.scale(self.castle_image, (castle_width, castle_height))
            # Center the castle horizontally and position it so bottom is at grass line (moved down 200 pixels)
            castle_x = (w - castle_width) // 2
            castle_y = h - 150 - castle_height + 320  # Position so bottom sits on grass, moved down 200 pixels
            surface.blit(scaled_castle, (castle_x, castle_y))
        
        # Draw characters in front of castle
        char_y = h - 230  # Position them in front of the castle
        
        # Interpolate character positions based on kiss_animation_progress
        # Start positions (apart)
        maria_start_x = w // 2 - 102
        shani_start_x = w // 2 - 26
        # End positions (together)
        maria_end_x = w // 2 - 80
        shani_end_x = w // 2 - 48
        
        # Calculate current positions using linear interpolation
        maria_x = maria_start_x + (maria_end_x - maria_start_x) * self.kiss_animation_progress
        shani_x = shani_start_x + (shani_end_x - shani_start_x) * self.kiss_animation_progress
        
        # Draw Maria (facing right toward Shani)
        if self.maria_sprite:
            maria_scaled = pygame.transform.scale(self.maria_sprite, (128, 128))
            surface.blit(maria_scaled, (maria_x, char_y))
        
        # Draw Shani (facing left toward Maria)
        if self.shani_sprite:
            shani_scaled = pygame.transform.scale(self.shani_sprite, (128, 128))
            surface.blit(shani_scaled, (shani_x, char_y))
        
        # Draw title
        title = self.font.render("Disney World — A Kiss at the Castle", True, (255, 255, 255))
        surface.blit(title, (20, 20))

        if not self.kissed:
            hint = self.font.render("Press SPACE to kiss", True, (240, 200, 200))
            hint.set_alpha(int(self.hint_alpha))
            surface.blit(hint, ((w - hint.get_width())//2, h - 70))
        else:
            # Draw firework particles
            for f in self.fireworks:
                import math
                # Calculate alpha based on remaining life
                alpha = int(255 * (1 - f['t'] / f['max_t']))
                if alpha > 0:
                    # Draw particle as a circle
                    particle_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                    particle_surface.set_alpha(alpha)
                    pygame.draw.circle(particle_surface, f['color'], (6, 6), 6)
                    surface.blit(particle_surface, (int(f['x']) - 6, int(f['y']) - 6))
            
            # Draw a growing heart that covers them (drawn last so it's on top)
            if self.heart_image and self.heart_scale > 0:
                # Heart center position (center between Maria and Shani)
                # Maria is at (w // 2 - 80), Shani is at (w // 2 - 48)
                # Center between them: average of their positions plus half character width (64)
                maria_center = (w // 2 - 80) + 64
                shani_center = (w // 2 - 48) + 64
                heart_center_x = (maria_center + shani_center) // 2
                heart_center_y = char_y + 64  # Middle of characters vertically
                
                # Calculate heart size based on scale (grows to cover characters)
                # Target size: about 350 pixels to cover both characters
                base_size = 350
                current_size = int(base_size * self.heart_scale)
                
                if current_size > 1:
                    # Scale the heart image
                    scaled_heart = pygame.transform.scale(self.heart_image, (current_size, current_size))
                    # Center it between the characters
                    heart_x = heart_center_x - current_size // 2
                    heart_y = heart_center_y - current_size // 2
                    surface.blit(scaled_heart, (heart_x, heart_y))
