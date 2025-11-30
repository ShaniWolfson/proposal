import pygame
import assets


class Player(pygame.sprite.Sprite):
    """Simple player sprite for top-down movement.

    Controls will be arrow keys or WASD. This class handles movement,
    collision rect and a simple draw placeholder. Replace the surface
    with an actual sprite image later.
    """

    def __init__(self, x: int, y: int, color=(255, 100, 180)):
        super().__init__()
        # try to load character animations (scaled to canonical size); fallback to placeholder surface
        CANON_SIZE = (32, 48)
        try:
            self.animations = assets.get_animations('maria', size=CANON_SIZE) or {}
        except Exception:
            self.animations = {}

        self.current_anim = 'idle'
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_delay = 0.12

        if self.animations and 'idle' in self.animations and len(self.animations['idle']) > 0:
            self.image = self.animations['idle'][0]
        else:
            self.image = pygame.Surface(CANON_SIZE, pygame.SRCALPHA)
            # simple body
            pygame.draw.rect(self.image, color, pygame.Rect(8, 8, 16, 32))
            # simple hair (top)
            pygame.draw.rect(self.image, (120, 70, 20), pygame.Rect(8, 0, 16, 12))

        self.rect = self.image.get_rect(topleft=(x, y))

        # movement
        self.speed = 180  # pixels per second
        self.vx = 0
        self.vy = 0

    def handle_input(self, keys):
        self.vx = 0
        self.vy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = 1

        # set animation based on input
        if self.vx < 0:
            self.current_anim = 'walk' if 'walk' in self.animations else 'idle'
        elif self.vx > 0:
            self.current_anim = 'walk' if 'walk' in self.animations else 'idle'
        elif self.vy != 0:
            self.current_anim = 'walk' if 'walk' in self.animations else 'idle'
        else:
            self.current_anim = 'idle'

    def update(self, dt, obstacles=None):
        # normalize diagonal speed
        if self.vx != 0 and self.vy != 0:
            mul = 0.7071
        else:
            mul = 1
        dx = int(self.vx * self.speed * mul * dt)
        dy = int(self.vy * self.speed * mul * dt)

        # basic movement without physics; obstacles is a list of rects
        if dx:
            self.rect.x += dx
            if obstacles:
                for o in obstacles:
                    if self.rect.colliderect(o):
                        # simple pushback
                        if dx > 0:
                            self.rect.right = o.left
                        else:
                            self.rect.left = o.right
        if dy:
            self.rect.y += dy
            if obstacles:
                for o in obstacles:
                    if self.rect.colliderect(o):
                        if dy > 0:
                            self.rect.bottom = o.top
                        else:
                            self.rect.top = o.bottom

        # animation update
        frames = self.animations.get(self.current_anim) if self.animations else None
        if frames and len(frames) > 0:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            # keep rect position
            pos = self.rect.topleft
            self.rect = self.image.get_rect(topleft=pos)

    def interact(self):
        """Placeholder for interaction (press SPACE). Return True if interacted."""
        return False
