import pygame
import os
from ..core.scene import Scene
from ..core.assets import get_animations
from ..utils.lpc_demo import AnimationManager, Animation


class IntroScene(Scene):
    """Opening scene with story text and characters walking across screen."""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.story_lines = [
            "The Story of Shani and Maria",
            "",
            "A little over a year ago Shani and Maria met on a dating app.",
            "Neither of them realized that this was the beginning of a wild journey",
            "filled with late-night conversations,",
            "road trips, Disney adventures,",
            "moving in together, and so much more.",
            "",
            "This is their love story.",
        ]
        self.current_line_index = 0
        self.line_timer = 0.0
        self.line_display_time = 2.5  # seconds per line
        self.font_title = None
        self.font_text = None
        
        # Character animation
        self.shani_anim = None
        self.maria_anim = None
        self.shani_x = -100  # Start off-screen left
        self.maria_x = -200
        self.shani_y = 500
        self.maria_y = 520
        self.walk_speed = 80
        self.characters_walking = True
        
        # Photo montage
        self.montage_active = False
        self.montage_timer = 0.0
        self.montage_duration = 8.0  # Total time for montage
        self.photos = []
        self.photo_data = []  # List of (photo, x, y, scale, rotation, velocity)
        
        # Timing
        self.intro_complete = False
        self.fade_timer = 0.0
        self.fade_duration = 1.0
        
    def start(self):
        """Initialize the intro scene."""
        super().start()
        
        # Load fonts
        try:
            self.font_title = pygame.font.Font(None, 72)
            self.font_text = pygame.font.Font(None, 48)
        except Exception:
            self.font_title = pygame.font.SysFont('Arial', 72)
            self.font_text = pygame.font.SysFont('Arial', 48)
        
        # Load character animations
        self._setup_characters()
        
        # Load photos for montage
        self._load_photos()
        
    def _setup_characters(self):
        """Load and setup character animations."""
        # Setup Shani
        try:
            shani_anims = get_animations('shani', size=(64, 64))
            self.shani_anim = AnimationManager()
            for name, frames in shani_anims.items():
                if frames and len(frames) > 0:
                    # Filter out transparent frames for walk animations
                    if 'walk' in name:
                        visible_frames = []
                        for frame in frames:
                            try:
                                mask = pygame.mask.from_surface(frame)
                                if mask.count() > 0:
                                    visible_frames.append(frame)
                            except Exception:
                                visible_frames.append(frame)
                        frames = visible_frames if visible_frames else frames
                    
                    speed = 150 if 'walk' in name else 200
                    self.shani_anim.add(name, Animation(frames, speed_ms=speed, loop=True))
            
            if 'walk_right' in self.shani_anim.animations:
                self.shani_anim.play('walk_right')
            else:
                print(f"Warning: walk_right not found for Shani. Available: {list(self.shani_anim.animations.keys())}")
        except Exception as e:
            print(f"Could not load Shani animations: {e}")
            
        # Setup Maria
        try:
            maria_anims = get_animations('maria', size=(64, 64))
            self.maria_anim = AnimationManager()
            for name, frames in maria_anims.items():
                if frames and len(frames) > 0:
                    # Filter out transparent frames for walk animations
                    if 'walk' in name:
                        visible_frames = []
                        for frame in frames:
                            try:
                                mask = pygame.mask.from_surface(frame)
                                if mask.count() > 0:
                                    visible_frames.append(frame)
                            except Exception:
                                visible_frames.append(frame)
                        frames = visible_frames if visible_frames else frames
                    
                    speed = 150 if 'walk' in name else 200
                    self.maria_anim.add(name, Animation(frames, speed_ms=speed, loop=True))
            
            if 'walk_right' in self.maria_anim.animations:
                self.maria_anim.play('walk_right')
            else:
                print(f"Warning: walk_right not found for Maria. Available: {list(self.maria_anim.animations.keys())}")
        except Exception as e:
            print(f"Could not load Maria animations: {e}")
    
    def _load_photos(self):
        """Load real photos for the montage."""
        import random
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
                        # Resize to reasonable size (max 200px on longest side)
                        w, h = photo.get_size()
                        scale_factor = min(200 / w, 200 / h)
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
            # Create 6 sample photo placeholders with different colors
            colors = [
                (255, 200, 200),  # Light red
                (200, 255, 200),  # Light green
                (200, 200, 255),  # Light blue
                (255, 255, 200),  # Light yellow
                (255, 200, 255),  # Light magenta
                (200, 255, 255),  # Light cyan
            ]
            for i, color in enumerate(colors):
                # Create a colored rectangle as placeholder
                photo = pygame.Surface((150, 150))
                photo.fill(color)
                # Add border
                pygame.draw.rect(photo, (100, 100, 100), (0, 0, 150, 150), 5)
                # Add "PHOTO" text
                font = pygame.font.Font(None, 36)
                text = font.render(f"PHOTO {i+1}", True, (50, 50, 50))
                text_rect = text.get_rect(center=(75, 75))
                photo.blit(text, text_rect)
                self.photos.append(photo)
        
        # Initialize photo positions with random floating motion
        for i, photo in enumerate(self.photos):
            x = random.randint(100, 924)
            y = random.randint(-200, -50)  # Start above screen
            scale = random.uniform(0.8, 1.2)
            rotation = random.uniform(-15, 15)
            vx = random.uniform(-30, 30)
            vy = random.uniform(20, 50)
            self.photo_data.append({
                'x': x, 'y': y, 'scale': scale, 'rotation': rotation,
                'vx': vx, 'vy': vy, 'rotation_speed': random.uniform(-20, 20)
            })
    
    def handle_event(self, event: pygame.event.EventType):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Skip to next scene
                self._transition_to_menu()
    
    def update(self, dt: float):
        """Update intro scene state."""
        # Update line timer (skip if montage is active)
        if not self.montage_active and self.current_line_index < len(self.story_lines):
            self.line_timer += dt
            if self.line_timer >= self.line_display_time:
                self.line_timer = 0.0
                self.current_line_index += 1
        
        # Update character positions and animations
        if self.characters_walking:
            self.shani_x += self.walk_speed * dt
            self.maria_x += self.walk_speed * dt
            
            # Keep walk animation active
            if self.shani_anim and self.shani_anim.current != 'walk_right':
                self.shani_anim.play('walk_right')
            if self.maria_anim and self.maria_anim.current != 'walk_right':
                self.maria_anim.play('walk_right')
            
            # Stop walking when they reach center-right
            if self.shani_x > 1100:
                self.characters_walking = False
                if self.shani_anim:
                    self.shani_anim.play('idle_right')
                if self.maria_anim:
                    self.maria_anim.play('idle_right')
        
        # Always update animations (whether walking or idle)
        if self.shani_anim:
            self.shani_anim.update(dt * 1000)
        if self.maria_anim:
            self.maria_anim.update(dt * 1000)
        
        # Check if text is complete, then start montage
        if self.current_line_index >= len(self.story_lines) and not self.characters_walking and not self.montage_active:
            print(f"Starting montage! Photos loaded: {len(self.photos)}")
            self.montage_active = True
            self.montage_timer = 0.0
        
        # Update photo montage
        if self.montage_active:
            self.montage_timer += dt
            
            # Update each photo position
            for i, data in enumerate(self.photo_data):
                data['x'] += data['vx'] * dt
                data['y'] += data['vy'] * dt
                data['rotation'] += data['rotation_speed'] * dt
                
                # Bounce off walls
                if data['x'] < 0 or data['x'] > 1024:
                    data['vx'] *= -1
                if data['y'] > 768:
                    data['y'] = -200  # Reset to top
                    data['x'] = __import__('random').randint(100, 924)
            
            # End montage after duration
            if self.montage_timer >= self.montage_duration:
                self.fade_timer += dt
                if self.fade_timer >= self.fade_duration:
                    self._transition_to_menu()
    
    def _transition_to_menu(self):
        """Transition to bumble scene."""
        from .bumble_splash_scene import BumbleSplashScene
        self.manager.go_to(BumbleSplashScene(self.manager))
    
    def draw(self, surface: pygame.Surface):
        """Draw the intro scene."""
        # Blue gradient background (dark to light)
        width, height = surface.get_size()
        for y in range(height):
            # Dark blue at top to lighter blue at bottom
            r = int(30 + (y / height) * 70)
            g = int(50 + (y / height) * 120)
            b = int(100 + (y / height) * 155)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        # Draw text
        y_offset = 100
        for i, line in enumerate(self.story_lines):
            if i > self.current_line_index:
                break
                
            # Use title font for first line, regular font for others
            if i == 0:
                font = self.font_title
                color = (255, 220, 150)  # Golden color for title
            else:
                font = self.font_text
                color = (255, 255, 255)
            
            # Fade in effect for current line
            if i == self.current_line_index:
                alpha = min(255, int((self.line_timer / 0.5) * 255))
                color = (color[0], color[1], color[2])
            
            if line:  # Skip empty lines for rendering but count them
                text_surface = font.render(line, True, color)
                text_rect = text_surface.get_rect(center=(width // 2, y_offset))
                surface.blit(text_surface, text_rect)
            
            y_offset += 60 if i == 0 else 50
        
        # Draw characters (unless montage is active)
        if not self.montage_active:
            if self.shani_anim and self.shani_x > -100:
                self.shani_anim.draw(surface, int(self.shani_x), int(self.shani_y), scale=2.5)
            
            if self.maria_anim and self.maria_x > -100:
                self.maria_anim.draw(surface, int(self.maria_x), int(self.maria_y), scale=2.5)
        
        # Draw photo montage
        if self.montage_active:
            # Debug: Draw a large red rectangle to show montage is active
            debug_rect = pygame.Rect(10, 10, 200, 50)
            pygame.draw.rect(surface, (255, 0, 0), debug_rect)
            debug_font = pygame.font.Font(None, 24)
            debug_text = debug_font.render(f"MONTAGE: {len(self.photos)} photos", True, (255, 255, 255))
            surface.blit(debug_text, (15, 20))
            
            for i, (photo, data) in enumerate(zip(self.photos, self.photo_data)):
                # Apply rotation and scale
                scaled_photo = pygame.transform.rotozoom(photo, data['rotation'], data['scale'])
                photo_rect = scaled_photo.get_rect(center=(int(data['x']), int(data['y'])))
                
                # Add subtle shadow
                shadow = pygame.Surface(scaled_photo.get_size(), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 50))
                shadow_rect = shadow.get_rect(center=(int(data['x'] + 5), int(data['y'] + 5)))
                surface.blit(shadow, shadow_rect)
                
                # Draw photo
                surface.blit(scaled_photo, photo_rect)
                
                # Debug: show position
                pos_text = debug_font.render(f"Photo {i}: ({int(data['x'])}, {int(data['y'])})", True, (255, 255, 0))
                surface.blit(pos_text, (10, 70 + i * 20))
        
        # Draw "Press SPACE to continue" hint
        if self.current_line_index >= len(self.story_lines) - 1:
            hint_font = pygame.font.Font(None, 32)
            hint_text = hint_font.render("Press SPACE to continue", True, (200, 200, 200))
            hint_rect = hint_text.get_rect(center=(width // 2, height - 50))
            # Pulse effect
            alpha = int(128 + 127 * abs(pygame.time.get_ticks() % 2000 - 1000) / 1000)
            hint_text.set_alpha(alpha)
            surface.blit(hint_text, hint_rect)
        
        # Fade out effect at the end
        if self.fade_timer > 0:
            fade_alpha = min(255, int((self.fade_timer / self.fade_duration) * 255))
            fade_surface = pygame.Surface((width, height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            surface.blit(fade_surface, (0, 0))
