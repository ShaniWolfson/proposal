import pygame
from scene import Scene


class DisneyScene(Scene):
    """Quick Disney World scene: walk up together and kiss at castle with fireworks."""

    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.timer = 3.0
        self.kissed = False

    def start(self):
        self.font = pygame.font.SysFont(None, 36)
        self.timer = 3.0
        self.kissed = False

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.kissed = True

    def update(self, dt: float):
        if self.kissed:
            self.timer -= dt
            if self.timer <= 0:
                # go back to main flow (placeholder: go to next scene if exists)
                pass

    def draw(self, surface: pygame.Surface):
        surface.fill((18, 24, 80))
        w, h = surface.get_size()
        # castle simple
        pygame.draw.polygon(surface, (220, 220, 240), [(w//2-80, h//2+40), (w//2-40, h//2-40), (w//2, h//2+40)])
        title = self.font.render("Disney World — A Kiss at the Castle", True, (255, 255, 255))
        surface.blit(title, (20, 20))

        if not self.kissed:
            hint = self.font.render("Press SPACE to kiss", True, (240, 200, 200))
            surface.blit(hint, ((w - hint.get_width())//2, h - 120))
        else:
            # simple fireworks
            for i in range(8):
                pygame.draw.circle(surface, (255, 200, 50), (100 + i*120, 120), 8 + (i%3)*4)
            text = self.font.render("You kiss under the fireworks.", True, (255, 240, 240))
            surface.blit(text, ((w - text.get_width())//2, h - 120))
