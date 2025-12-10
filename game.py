"""Our Adventure - A Proposal Game

Main game entry point with scene management and keyboard shortcuts.
"""

import pygame
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import Scene, SceneManager, Player, load_assets
from src.scenes import (
    BumbleSplashScene, BumbleScene, DriveScene,
    ApartmentScene, DisneyScene, MovingScene,
    DinnerScene, MenuScene
)

# Configuration
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Our Adventure"


class GameConfig:
    """Game configuration and settings."""
    def __init__(self):
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.fps = FPS
        self.title = GAME_TITLE
        
        # Scene shortcuts: Key number -> (Scene class, Display name)
        self.scene_shortcuts = {
            pygame.K_1: (BumbleScene, "Bumble"),
            pygame.K_2: (DriveScene, "Drive"),
            pygame.K_3: (ApartmentScene, "Apartment"),
            pygame.K_4: (DisneyScene, "Disney"),
            pygame.K_5: (MovingScene, "Moving"),
            pygame.K_6: (DinnerScene, "Dinner"),
        }


class Game:
    """Main game class handling initialization and game loop."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.screen = None
        self.clock = None
        self.manager = None
        self.running = False
        
    def initialize(self):
        """Initialize Pygame and game systems."""
        pygame.init()
        
        # Initialize mixer for music support
        pygame.mixer.init()
        
        # Load assets
        try:
            load_assets()
        except Exception as e:
            print(f"Warning: Failed to load some assets: {e}")
        
        # Center window on screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # Create window
        self.screen = pygame.display.set_mode(
            (self.config.screen_width, self.config.screen_height)
        )
        pygame.display.set_caption(self.config.title)
        
        # Create clock and scene manager
        self.clock = pygame.time.Clock()
        self.manager = SceneManager()
        
        # Start with splash screen
        self.manager.go_to(BumbleSplashScene(self.manager))
        
    def handle_input(self, event):
        """Handle global input events."""
        if event.type == pygame.QUIT:
            self.running = False
            
        elif event.type == pygame.KEYDOWN:
            # ESC to quit
            if event.key == pygame.K_ESCAPE:
                self.running = False
                
            # M for menu
            elif event.key == pygame.K_M:
                self.manager.go_to(MenuScene(self.manager))
                
            # Number keys for scene shortcuts
            elif event.key in self.config.scene_shortcuts:
                scene_class, name = self.config.scene_shortcuts[event.key]
                try:
                    self.manager.go_to(scene_class(self.manager))
                    print(f"Jumped to {name} scene")
                except Exception as e:
                    print(f"Failed to load {name} scene: {e}")
            
            # Pass event to current scene
            else:
                self.manager.handle_event(event)
        else:
            self.manager.handle_event(event)
    
    def update(self, dt: float):
        """Update game state."""
        self.manager.update(dt)
    
    def draw(self):
        """Render the current frame."""
        self.manager.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        self.running = True
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.config.fps) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                self.handle_input(event)
            
            # Update and draw
            self.update(dt)
            self.draw()
    
    def shutdown(self):
        """Clean up and exit."""
        pygame.quit()


def main():
    """Main entry point."""
    config = GameConfig()
    game = Game(config)
    
    try:
        game.initialize()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        game.shutdown()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
