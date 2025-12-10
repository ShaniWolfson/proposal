import pygame
import sys
sys.path.insert(0, 'src')
from src.core.scene import SceneManager, Scene
from src.core.player import Player
from src.scenes.menu_scene import MenuScene
from src.core import assets


# Screen dimensions - reduced height to prevent cutoff
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


# Keep GameScene available as a simple test, but start at the MenuScene for quick navigation
class GameScene(Scene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.player = None
        self.sprites = pygame.sprite.Group()
        self.obstacles = []

    def start(self):
        # place player roughly center
        self.player = Player(SCREEN_WIDTH // 2 - 16, SCREEN_HEIGHT // 2 - 24)
        self.sprites.add(self.player)

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.interact()

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.sprites.update(dt, obstacles=self.obstacles)

    def draw(self, surface: pygame.Surface):
        surface.fill((30, 30, 40))
        # simple HUD
        font = pygame.font.SysFont(None, 24)
        info = font.render("Move: WASD/Arrows — Interact: SPACE — Quit: ESC", True, (220, 220, 220))
        surface.blit(info, (12, 12))
        self.sprites.draw(surface)


def main():
    pygame.init()
    # load art assets (if any) so scenes can query them
    try:
        assets.load_assets()
    except Exception:
        pass
    
    # Center the window on screen
    import os
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Our Adventure — Prototype")
    clock = pygame.time.Clock()
    
    # Initialize audio mixer for music support
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Warning: Could not initialize audio mixer: {e}")

    manager = SceneManager()
    # Start with Bumble splash screen instead of menu
    from src.scenes.bumble_splash_scene import BumbleSplashScene
    manager.go_to(BumbleSplashScene(manager))

    # Scene shortcuts (label, module, class)
    scene_shortcuts = [
        ("bumble_scene", "BumbleScene"),
        ("drive_scene", "DriveScene"),
        ("apartment_scene", "ApartmentScene"),
        ("disney_scene", "DisneyScene"),
        ("moving_scene", "MovingScene"),
        ("dinner_scene", "DinnerScene"),
    ]
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Press M to open menu
                manager.go_to(MenuScene(manager))
            elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                # Global scene shortcuts - pressing 1-8 at any time jumps to that scene
                idx = event.key - pygame.K_1
                if 0 <= idx < len(scene_shortcuts):
                    module_name, class_name = scene_shortcuts[idx]
                    try:
                        import importlib
                        mod = importlib.import_module(f"src.scenes.{module_name}")
                        cls = getattr(mod, class_name)
                        manager.go_to(cls(manager))
                    except Exception as e:
                        print(f"Failed to load {module_name}.{class_name}: {e}")
            else:
                manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error running game:", e)
        pygame.quit()
        sys.exit(1)
