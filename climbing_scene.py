import pygame
from scene import Scene


class ClimbingScene(Scene):
    """Button-mash climbing scene. Mash SPACE or UP to climb to the top."""

    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.progress = 0.0
        self.goal = 100.0
        self.cheer = False

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.progress = 0.0
        self.cheer = False

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP):
            self.progress += 3.0

    def update(self, dt: float):
        # small natural decay
        self.progress = max(0.0, self.progress - dt * 4.0)
        if self.progress >= self.goal and not self.cheer:
            self.cheer = True

    def draw(self, surface: pygame.Surface):
        surface.fill((40, 60, 80))
        w, h = surface.get_size()
        # draw wall
        pygame.draw.rect(surface, (140, 120, 110), (w//2 - 120, 80, 240, h - 160))
        # progress bar
        bar_w = 300
        pygame.draw.rect(surface, (80, 80, 80), (w//2 - bar_w//2, 40, bar_w, 20))
        frac = min(1.0, self.progress / self.goal)
        pygame.draw.rect(surface, (120, 220, 120), (w//2 - bar_w//2, 40, int(bar_w * frac), 20))

        label = self.font.render("Mash SPACE/UP to climb — Shani cheers you on!", True, (240, 240, 240))
        surface.blit(label, (w//2 - label.get_width()//2, 10))

        if self.cheer:
            t = self.font.render("You reached the top! Shani: 'You can do it! Flag your right foot!'", True, (255, 230, 200))
            surface.blit(t, (w//2 - t.get_width()//2, h - 80))
