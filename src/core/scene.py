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
    
    Music support:
    - Set music_file attribute to enable background music
    - Music will automatically play when scene starts and stop when it ends
    """

    def __init__(self, manager: Optional[object] = None):
        self.manager = manager
        self.music_file = None  # Override in subclass to set music

    def start(self):
        # Play scene music if specified
        if self.music_file:
            self._play_music(self.music_file)

    def end(self):
        # Stop music when scene ends
        if self.music_file:
            pygame.mixer.music.stop()
    
    def _play_music(self, music_path: str, volume: float = 0.5, loops: int = -1):
        """Play background music for this scene.
        
        Args:
            music_path: Path to music file (mp3, ogg, etc.)
            volume: Volume level (0.0 to 1.0)
            loops: Number of times to loop (-1 for infinite)
        """
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"Failed to load music {music_path}: {e}")

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
