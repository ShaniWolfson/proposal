import pygame
from ..core.scene import Scene
from .bumble_scene import BumbleScene


class BumbleSplashScene(Scene):
    """Splash screen showing Bumble_home.jpeg before fading to the Bumble scene."""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.image = None
        self.timer = 0.0
        self.duration = 3.0  # Show splash for 3 seconds
        self.fade_alpha = 0
        self.fade_in_duration = 1.0
        self.fade_out_duration = 1.0
        self.fading_out = False
        
    def start(self):
        try:
            # Load without convert to preserve quality
            self.image = pygame.image.load("art/scenes/bumble/Bumble_home.jpg")
        except Exception as e:
            print(f"Failed to load Bumble_home.jpg: {e}")
            # If image fails to load, skip to Bumble scene immediately
            if self.manager:
                self.manager.go_to(BumbleScene(self.manager))
    
    def handle_event(self, event: pygame.event.EventType):
        # Allow skipping splash with space or enter
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._transition_to_bumble()
    
    def update(self, dt: float):
        self.timer += dt
        
        # Fade in
        if self.timer < self.fade_in_duration:
            self.fade_alpha = int((self.timer / self.fade_in_duration) * 255)
        # Hold
        elif self.timer < self.duration - self.fade_out_duration:
            self.fade_alpha = 255
        # Fade out and transition
        elif not self.fading_out:
            self.fading_out = True
        
        if self.fading_out:
            fade_progress = (self.timer - (self.duration - self.fade_out_duration)) / self.fade_out_duration
            if fade_progress >= 1.0:
                self._transition_to_bumble()
            else:
                self.fade_alpha = int((1.0 - fade_progress) * 255)
    
    def _transition_to_bumble(self):
        if self.manager:
            self.manager.go_to(BumbleScene(self.manager))
    
    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))
        
        if self.image:
            w, h = surface.get_size()
            img_w, img_h = self.image.get_size()
            
            # If image is already close to screen size, just center it without scaling
            if abs(img_w - w) < 100 and abs(img_h - h) < 100:
                x = (w - img_w) // 2
                y = (h - img_h) // 2
                temp_surface = self.image.copy()
                temp_surface.set_alpha(self.fade_alpha)
                surface.blit(temp_surface, (x, y))
            else:
                # Calculate aspect ratio scaling to fit within screen
                scale_w = w / img_w
                scale_h = h / img_h
                scale = min(scale_w, scale_h)  # Use min to fit inside screen
                
                # Scale image maintaining aspect ratio
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                
                # Only scale if needed
                if new_w != img_w or new_h != img_h:
                    scaled_image = pygame.transform.smoothscale(self.image, (new_w, new_h))
                else:
                    scaled_image = self.image
                
                # Center the scaled image
                x = (w - new_w) // 2
                y = (h - new_h) // 2
                
                # Create a copy with alpha applied
                temp_surface = scaled_image.copy()
                temp_surface.set_alpha(self.fade_alpha)
                surface.blit(temp_surface, (x, y))
