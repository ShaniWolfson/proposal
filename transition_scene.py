import pygame
from scene import Scene


class TransitionScene(Scene):
    """Simple transition scene that displays a message before moving to the next scene."""

    def __init__(self, message, next_scene_class, manager=None, duration=4.0):
        super().__init__(manager)
        self.message = message
        self.next_scene_class = next_scene_class
        self.duration = duration
        self.timer = 0
        self.font = None
        self.fade_in_alpha = 255
        self.fade_out_alpha = 0
        self.fade_in_duration = 1.0
        self.fade_out_duration = 1.0
        self.displayed_message = ""
        self.char_index = 0
        self.type_speed = 15  # characters per second
        
    def start(self):
        self.font = pygame.font.SysFont(None, 42)
        self.timer = 0
        self.fade_in_alpha = 255
        self.fade_out_alpha = 0
        self.displayed_message = ""
        self.char_index = 0

    def handle_event(self, event: pygame.event.EventType):
        pass

    def update(self, dt: float):
        self.timer += dt
        
        # Typewriter effect - add characters over time
        if self.char_index < len(self.message):
            self.char_index += dt * self.type_speed
            if self.char_index > len(self.message):
                self.char_index = len(self.message)
            self.displayed_message = self.message[:int(self.char_index)]
        
        # Fade in from black
        if self.timer < self.fade_in_duration:
            self.fade_in_alpha = 255 * (1 - self.timer / self.fade_in_duration)
        else:
            self.fade_in_alpha = 0
        
        # Start fade out before transition
        time_remaining = self.duration - self.timer
        if time_remaining <= self.fade_out_duration:
            self.fade_out_alpha = 255 * (1 - time_remaining / self.fade_out_duration)
        
        # Transition to next scene
        if self.timer >= self.duration:
            if self.manager and self.next_scene_class:
                self.manager.go_to(self.next_scene_class(self.manager))

    def draw(self, surface: pygame.Surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        
        # Draw message centered (with typewriter effect)
        text = self.font.render(self.displayed_message, True, (255, 240, 230))
        text_rect = text.get_rect(center=(w // 2, h // 2))
        surface.blit(text, text_rect)
        
        # Draw fade in overlay
        if self.fade_in_alpha > 0:
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_in_alpha))
            surface.blit(fade_surface, (0, 0))
        
        # Draw fade out overlay
        if self.fade_out_alpha > 0:
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_out_alpha))
            surface.blit(fade_surface, (0, 0))
