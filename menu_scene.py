import pygame
import importlib
from scene import Scene


class MenuScene(Scene):
    """Simple debug menu to jump to any scene by number or click.

    Shows a list of available scenes and imports them on demand to avoid circular imports.
    """

    def __init__(self, manager=None):
        super().__init__(manager)
        # (label, module, class)
        self.options = [
            ("1 Bumble (swipe)", "bumble_scene", "BumbleScene"),
            ("2 Drive (car)", "drive_scene", "DriveScene"),
            ("3 Apartment (first date)", "apartment_scene", "ApartmentScene"),
            ("4 Disney (kiss)", "disney_scene", "DisneyScene"),
            ("5 Climbing (mash)", "climbing_scene", "ClimbingScene"),
            ("6 U-Haul Drive", "moving_scene", "UHaulDriveScene"),
            ("7 Unpack Boxes", "moving_scene", "UnpackScene"),
            ("8 Dinner (family)", "dinner_scene", "DinnerScene"),
        ]
        self.font = None

    def start(self):
        self.font = pygame.font.SysFont(None, 34)

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.options):
                    self._goto(idx)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            w, h = pygame.display.get_surface().get_size()
            start_y = 120
            for i, opt in enumerate(self.options):
                rect = pygame.Rect(120, start_y + i * 56, w - 240, 48)
                if rect.collidepoint(mx, my):
                    self._goto(i)

    def _goto(self, idx: int):
        label, module_name, class_name = self.options[idx]
        try:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            if self.manager:
                self.manager.go_to(cls(self.manager))
        except Exception as e:
            print("Failed to load", module_name, e)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill((18, 22, 30))
        w, h = surface.get_size()
        title = self.font.render("Our Adventure — Scene Menu", True, (240, 240, 240))
        surface.blit(title, ((w - title.get_width()) // 2, 40))

        start_y = 120
        for i, (label, _, _) in enumerate(self.options):
            txt = self.font.render(label, True, (200, 200, 220))
            surface.blit(txt, (120, start_y + i * 56))

        hint = self.font.render("Press 1-8 or click an item to jump to a scene", True, (160, 160, 180))
        surface.blit(hint, (120, h - 80))
