import pygame
import importlib
from scene import Scene
from drive_scene import DriveScene


class UHaulDriveScene(DriveScene):
    def __init__(self, duration=10.0, manager=None):
        super().__init__(vehicle='uhaul', duration=duration, manager=manager)

    def update(self, dt: float):
        super().update(dt)
        # when finished, transition to unpack scene
        if self.timer <= 0:
            try:
                mod = importlib.import_module('moving_scene')
                cls = getattr(mod, 'UnpackScene')
                if self.manager:
                    self.manager.go_to(cls(self.manager))
            except Exception:
                pass


class UnpackScene(Scene):
    """Scene where Maria opens three boxes: Shani's, Maria's, Lexa's."""

    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.boxes = [False, False, False]

    def start(self):
        self.font = pygame.font.SysFont(None, 28)

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.boxes[0] = True
            elif event.key == pygame.K_2:
                self.boxes[1] = True
            elif event.key == pygame.K_3:
                self.boxes[2] = True

    def update(self, dt: float):
        # if all opened, wait a moment and move to dinner placeholder
        if all(self.boxes):
            try:
                mod = importlib.import_module('dinner_scene')
                cls = getattr(mod, 'DinnerScene')
                if self.manager:
                    self.manager.go_to(cls(self.manager))
            except Exception:
                # if dinner_scene not available, stay
                pass

    def draw(self, surface: pygame.Surface):
        surface.fill((70, 70, 80))
        w, h = surface.get_size()
        title = self.font.render("Moving In — Open the boxes: 1=Shani, 2=Maria, 3=Lexa", True, (240, 240, 240))
        surface.blit(title, (20, 20))
        labels = ["Shani's stuff...", "Maria's colorful sweaters...", "Lexa's toys and treats..."]
        for i in range(3):
            x = 220 + i * 260
            rect = pygame.Rect(x, h//2 - 60, 180, 120)
            pygame.draw.rect(surface, (180, 160, 140), rect)
            if self.boxes[i]:
                txt = self.font.render(labels[i], True, (20, 20, 20))
                surface.blit(txt, (rect.x + 8, rect.y + 8))
            else:
                txt = self.font.render("Box %d (press %d)" % (i+1, i+1), True, (20, 20, 20))
                surface.blit(txt, (rect.x + 8, rect.y + 8))
