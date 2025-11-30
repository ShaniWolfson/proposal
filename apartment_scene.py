import pygame
import importlib
from scene import Scene
from dialogue import DialogueBox


class ApartmentScene(Scene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.dialog = None
        # simple interactable rects
        self.wine_rect = pygame.Rect(540, 320, 40, 80)
        self.cards_rect = pygame.Rect(620, 360, 48, 28)
        self.couch_rect = pygame.Rect(440, 380, 200, 80)

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.dialog = DialogueBox(self.font, 800, 120)
        self.dialog.set_lines(["You remember the red wine... Wow who knew kosher wine could taste this good?"])

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # interact by proximity — for prototype just cycle dialogs
                if self.dialog.visible:
                    self.dialog.next()
                else:
                    # open wine dialog as default
                    self.dialog.set_lines(["Wow who knew kosher wine could taste this good?"])

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill((50, 40, 55))
        w, h = surface.get_size()
        # simple room floor
        pygame.draw.rect(surface, (80, 60, 70), (200, 200, 880, 420), border_radius=6)

        # draw couch
        pygame.draw.rect(surface, (120, 80, 90), self.couch_rect)
        # wine bottle
        pygame.draw.rect(surface, (90, 20, 120), self.wine_rect)
        # cards
        pygame.draw.rect(surface, (200, 200, 200), self.cards_rect)

        title = self.font.render("First Date — Your UWS Apartment", True, (240, 240, 240))
        surface.blit(title, (20, 20))

        # hint
        hint = self.font.render("Press SPACE to interact with the room objects", True, (200, 200, 200))
        surface.blit(hint, (20, 60))

        # dialog
        if self.dialog:
            self.dialog.draw(surface, 240, 520)
