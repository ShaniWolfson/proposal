import pygame
from typing import Optional


class Scene:
    """Base class for game scenes.

    Subclass this to implement specific scenes. Methods:
    - start(): called when the scene becomes active
    - end(): called when the scene is replaced/removed
    - handle_event(event): called for each pygame event
    - update(dt): called each frame with delta seconds
    - draw(surface): render the scene to the given surface
    """

    def __init__(self, manager: Optional[object] = None):
        self.manager = manager

    def start(self):
        pass

    def end(self):
        pass

    def handle_event(self, event: pygame.event.EventType):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        pass


class SceneManager:
    """Simple scene manager to switch active scenes."""

    def __init__(self):
        self.scene: Optional[Scene] = None

    def go_to(self, scene: Scene):
        if self.scene is not None:
            try:
                self.scene.end()
            except Exception:
                pass
        self.scene = scene
        self.scene.manager = self
        try:
            self.scene.start()
        except Exception:
            pass

    def handle_event(self, event: pygame.event.EventType):
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt: float):
        if self.scene:
            self.scene.update(dt)

    def draw(self, surface: pygame.Surface):
        if self.scene:
            self.scene.draw(surface)
