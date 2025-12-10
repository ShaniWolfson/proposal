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
        # Play scene music if specified and not already playing
        if self.music_file:
            # Check if this music is already playing (via scene manager)
            if hasattr(self.manager, 'current_music_file') and self.manager.current_music_file == self.music_file:
                # Music is already playing, don't restart it
                pass
            else:
                self._play_music(self.music_file)

    def end(self):
        # Fade out music when scene ends
        if self.music_file and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
    
    def _play_music(self, music_path: str, volume: float = 0.5, loops: int = -1, fade_ms: int = 1000):
        """Play background music for this scene.
        
        Args:
            music_path: Path to music file (mp3, ogg, etc.)
            volume: Volume level (0.0 to 1.0)
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade in duration in milliseconds (default 1000ms = 1 second)
        """
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
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
        self.current_music_file: Optional[str] = None

    def go_to(self, scene: Scene):
        # Check if new scene has same music as currently playing
        next_music = getattr(scene, 'music_file', None)
        same_music = (self.current_music_file is not None and 
                     next_music is not None and
                     self.current_music_file == next_music)
        
        if self.scene is not None:
            try:
                # Only end (fade out) if next scene has different music
                if not same_music:
                    self.scene.end()
                    self.current_music_file = None
            except Exception:
                pass
        
        self.scene = scene
        self.scene.manager = self
        try:
            # Always call start() for scene initialization
            self.scene.start()
            # Track current music file
            if next_music:
                self.current_music_file = next_music
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
