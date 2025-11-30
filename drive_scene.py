import pygame
import random
import importlib
from scene import Scene


class DriveScene(Scene):
    """Side-scrolling driving minigame.

    vehicle: 'car' or 'uhaul'
    duration: seconds to auto-complete (default 10)
    """

    def __init__(self, vehicle='car', duration=10.0, manager=None):
        super().__init__(manager)
        self.vehicle = vehicle
        self.duration = duration
        self.timer = duration
        self.font = None
        self.player_rect = pygame.Rect(120, 300, 56, 28)
        self.obstacles = []
        self.spawn_timer = 0.0
        self.scroll_speed = 220 if vehicle == 'car' else 180
        self.avoid_color = (240, 100, 80)
        self.bg_offset = 0
        self.crashed = False
        self.crash_timer = 0.0

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.timer = self.duration
        self.obstacles = []
        self.spawn_timer = 0.5
        self.crashed = False

    def handle_event(self, event: pygame.event.EventType):
        pass

    def update(self, dt: float):
        if self.crashed:
            self.crash_timer -= dt
            if self.crash_timer <= 0:
                self.crashed = False
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player_rect.y -= int(300 * dt)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player_rect.y += int(300 * dt)

            # clamp
            self.player_rect.y = max(40, min(self.player_rect.y, 720 - 40 - self.player_rect.height))

            # spawn obstacles
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = random.uniform(0.6, 1.2)
                oy = random.randint(80, 720 - 80)
                ow = 40 if random.random() < 0.6 else 24
                oh = 24
                rect = pygame.Rect(1280 + 10, oy, ow, oh)
                ob_type = 'pothole'
                if random.random() < 0.25:
                    ob_type = 'jaywalker'
                # store obstacle as a dict to avoid attaching attributes to Rect
                self.obstacles.append({'rect': rect, 'type': ob_type})

            # move obstacles
            for o in list(self.obstacles):
                o['rect'].x -= int(self.scroll_speed * dt)
                if o['rect'].right < -50:
                    self.obstacles.remove(o)

            # collisions
            for o in list(self.obstacles):
                if self.player_rect.colliderect(o['rect']):
                    # crash
                    self.crashed = True
                    self.crash_timer = 0.8
                    try:
                        self.obstacles.remove(o)
                    except ValueError:
                        pass

            self.timer -= dt
            if self.timer <= 0:
                # transition to apartment scene module to avoid import cycles
                try:
                    mod = importlib.import_module('apartment_scene')
                    cls = getattr(mod, 'ApartmentScene')
                    if self.manager:
                        self.manager.go_to(cls(self.manager))
                except Exception:
                    # fallback: do nothing
                    pass

    def draw(self, surface: pygame.Surface):
        # sky
        surface.fill((120, 180, 240))
        # simple scrolling buildings
        w, h = surface.get_size()
        self.bg_offset = (self.bg_offset + int(self.scroll_speed * 0.02)) % 400
        for i in range(-2, 6):
            bx = (i * 200) - (self.bg_offset % 200)
            pygame.draw.rect(surface, (200 - (i % 3) * 20, 180, 160), (bx, h - 220, 140, 180))

        # road
        pygame.draw.rect(surface, (40, 40, 40), (0, h - 120, w, 120))
        # lane lines
        for x in range(0, w, 80):
            pygame.draw.rect(surface, (220, 220, 80), (x + ((int(self.bg_offset) // 10) % 80), h - 60, 40, 6))

        # draw obstacles
        for o in self.obstacles:
            color = (100, 80, 60) if o.get('type') == 'pothole' else (220, 180, 60)
            pygame.draw.rect(surface, color, o['rect'])

        # draw player vehicle
        car_color = (60, 140, 220) if self.vehicle == 'car' else (240, 140, 60)
        pygame.draw.rect(surface, car_color, self.player_rect)

        # UI
        t = self.font.render(f"Time: {int(self.timer)}s", True, (255, 255, 255))
        surface.blit(t, (20, 20))
        hint = "Use W/S or Up/Down to steer" if not self.crashed else "Crashed! Recovering..."
        hsurf = self.font.render(hint, True, (255, 255, 255))
        surface.blit(hsurf, (20, 50))
