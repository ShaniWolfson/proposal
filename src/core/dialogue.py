import pygame
from typing import List, Optional


class DialogueBox:
    """Simple dialogue box that shows lines of text and optional choices.

    Usage:
      box = DialogueBox(font, width, height)
      box.set_lines(["Hello", "World"])  # pages
      box.update(dt); box.draw(surface)
    """

    def __init__(self, font: pygame.font.Font, width: int, height: int):
        self.font = font
        self.width = width
        self.height = height
        self.lines: List[str] = []
        self.index = 0
        self.visible = False
        self.choices: Optional[List[str]] = None
        self.selected = 0

    def set_lines(self, lines: List[str], choices: Optional[List[str]] = None):
        self.lines = lines
        self.index = 0
        self.visible = True
        self.choices = choices
        self.selected = 0

    def next(self):
        if not self.visible:
            return
        if self.index < len(self.lines) - 1:
            self.index += 1
        else:
            # end of dialogue
            self.visible = False

    def prev(self):
        if self.index > 0:
            self.index -= 1

    def handle_event(self, event: pygame.event.EventType):
        if not self.visible:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.next()
            elif event.key == pygame.K_LEFT and self.choices:
                self.selected = max(0, self.selected - 1)
            elif event.key == pygame.K_RIGHT and self.choices:
                self.selected = min(len(self.choices) - 1, self.selected + 1)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface, x: int, y: int):
        if not self.visible:
            return
        box = pygame.Surface((self.width, self.height))
        box.fill((15, 15, 20))
        pygame.draw.rect(box, (220, 220, 220), box.get_rect(), 2)

        text = self.lines[self.index]
        wrapped = self._wrap_text(text, self.font, self.width - 16)
        yy = 8
        for line in wrapped:
            surf = self.font.render(line, True, (240, 240, 240))
            box.blit(surf, (8, yy))
            yy += surf.get_height() + 2

        if self.choices:
            # draw choices centered
            choices_text = "  ".join(self.choices)
            surf = self.font.render(choices_text, True, (200, 200, 200))
            bx = (self.width - surf.get_width()) // 2
            box.blit(surf, (bx, self.height - 28))

        surface.blit(box, (x, y))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int):
        words = text.split(" ")
        lines = []
        cur = []
        for w in words:
            test = " ".join(cur + [w])
            if font.size(test)[0] <= max_width:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        return lines
