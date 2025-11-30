import pygame
from scene import Scene
from drive_scene import DriveScene


class BumbleScene(Scene):
    """Simple swipe-style scene: Maria swipes through profiles until she finds Shani."""

    def __init__(self, manager=None):
        super().__init__(manager)
        # three cringe profiles then Shani
        self.profiles = [
            {"name": "Profile 1", "bio": "If you can't handle me at my worst...", "match": False},
            {"name": "Profile 2", "bio": "I am not really single...", "match": False},
            {"name": "Profile 3", "bio": "successful software engineer, has a cute dog and super cute", "match": False},
            {"name": "Shani", "bio": "THIS ONE IS CUTE ✓", "match": True},
        ]
        self.index = 0
        self.font = None
        self.transition_timer = 0.0
        self.matched = False

    def start(self):
        self.font = pygame.font.SysFont(None, 36)
        self.index = 0
        self.matched = False

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_x, pygame.K_LEFT, pygame.K_a):
                # reject
                self._reject()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_c, pygame.K_RIGHT, pygame.K_d):
                # accept if match or simulate swipe right
                self._accept()

    def _reject(self):
        if self.index < len(self.profiles) - 1:
            self.index += 1

    def _accept(self):
        cur = self.profiles[self.index]
        if cur.get("match"):
            # matched Shani
            self.matched = True
            self.transition_timer = 1.2
        else:
            # still reject non-matching accept acts like pass
            self._reject()

    def update(self, dt: float):
        if self.matched:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                # go to the car driving minigame
                if self.manager:
                    self.manager.go_to(DriveScene(vehicle='car', duration=10.0, manager=self.manager))

    def draw(self, surface: pygame.Surface):
        surface.fill((40, 30, 60))
        w, h = surface.get_size()
        box_w, box_h = 700, 300
        box = pygame.Rect((w - box_w) // 2, (h - box_h) // 2, box_w, box_h)
        pygame.draw.rect(surface, (230, 230, 240), box, border_radius=8)

        # profile text
        cur = self.profiles[self.index]
        name_surf = self.font.render(cur["name"], True, (10, 10, 10))
        bio_font = pygame.font.SysFont(None, 28)
        bio_surf = bio_font.render(cur["bio"], True, (30, 30, 30))
        surface.blit(name_surf, (box.x + 20, box.y + 20))
        surface.blit(bio_surf, (box.x + 20, box.y + 70))

        hint = "Press X or Left to reject — Press SPACE/Enter to accept"
        hint_surf = bio_font.render(hint, True, (200, 200, 200))
        surface.blit(hint_surf, (box.x + 20, box.y + box_h - 44))

        if self.matched:
            m = pygame.font.SysFont(None, 48).render("It's a match!", True, (255, 50, 120))
            surface.blit(m, ((w - m.get_width()) // 2, box.y - 64))


