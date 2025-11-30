import pygame
import sys
from typing import List, Dict, Tuple

# --- CONFIG / CONSTANTS ---
FRAME_WIDTH = 64
FRAME_HEIGHT = 64
WALK_FRAMES = 8
ANIMATION_SPEED = 100  # ms per frame

SPRITE_SHEET_PATH = "assets/lpc_character.png"  # replace with your sheet
# If you have per-animation files for a character, point to the directory, e.g.:
SPRITE_SHEET_DIR = "art/characters/maria"

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# --- SPRITESHEET HELPER ---
class SpriteSheet:
    """Simple sprite sheet helper for LPC-style horizontal strips.

    Usage:
        sheet = SpriteSheet(path)
        frame = sheet.image_at((x, y, w, h))
        frames = sheet.load_strip((x, y, w, h), count)
    """
    def __init__(self, filename: str):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def image_at(self, rect: Tuple[int,int,int,int]) -> pygame.Surface:
        """Return a Surface for a single frame at rect=(x,y,w,h)."""
        x, y, w, h = rect
        image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        image.blit(self.sheet, (0, 0), (x, y, w, h))
        return image

    def load_strip(self, rect: Tuple[int,int,int,int], count: int) -> List[pygame.Surface]:
        """Load a horizontal strip of `count` frames starting at rect=(x,y,w,h)."""
        x, y, w, h = rect
        frames = []
        for i in range(count):
            frames.append(self.image_at((x + i * w, y, w, h)))
        return frames

# --- ANIMATION CLASS ---
class Animation:
    def __init__(self, frames: List[pygame.Surface], speed_ms: int = ANIMATION_SPEED, loop: bool = True):
        self.frames = frames
        self.speed = speed_ms
        self.loop = loop
        self.time_acc = 0
        self.index = 0
        self.finished = False

    def reset(self):
        self.time_acc = 0
        self.index = 0
        self.finished = False

    def update(self, dt_ms: int):
        if self.finished or len(self.frames) == 0:
            return
        self.time_acc += dt_ms
        while self.time_acc >= self.speed:
            self.time_acc -= self.speed
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True

    def get_current(self) -> pygame.Surface:
        if not self.frames:
            return None
        return self.frames[self.index]

    def is_finished(self) -> bool:
        return self.finished

# --- PLAYER CLASS ---
class Player:
    def __init__(self, x: int, y: int, spritesheet_or_frames):
        self.x = x
        self.y = y
        self.speed = 200  # px/sec
        self.vx = 0
        self.vy = 0
        self.facing_left = False

        # load animations from the sheet according to LPC layout
        # spritesheet_or_frames can be either a SpriteSheet or a dict of pre-sliced frames
        self.anims: Dict[str, Animation] = {}
        frames_map = {}
        if isinstance(spritesheet_or_frames, dict):
            frames_map = spritesheet_or_frames
        else:
            # single sheet with assumed rows
            ss = spritesheet_or_frames
            try:
                frames_map['idle'] = ss.load_strip((0, 0, FRAME_WIDTH, FRAME_HEIGHT), 4)
                frames_map['walk'] = ss.load_strip((0, FRAME_HEIGHT * 1, FRAME_WIDTH, FRAME_HEIGHT), 8)
                frames_map['slash'] = ss.load_strip((0, FRAME_HEIGHT * 2, FRAME_WIDTH, FRAME_HEIGHT), 6)
                frames_map['cast'] = ss.load_strip((0, FRAME_HEIGHT * 3, FRAME_WIDTH, FRAME_HEIGHT), 6)
                frames_map['die'] = ss.load_strip((0, FRAME_HEIGHT * 4, FRAME_WIDTH, FRAME_HEIGHT), 6)
            except Exception as e:
                print('Warning: failed to slice single-sheet animations:', e)

        # create Animation objects for any frames we have
        if 'idle' in frames_map and frames_map['idle']:
            self.anims['idle'] = Animation(frames_map['idle'], speed_ms=200, loop=True)
        if 'walk' in frames_map and frames_map['walk']:
            self.anims['walk'] = Animation(frames_map['walk'], speed_ms=ANIMATION_SPEED, loop=True)
        if 'slash' in frames_map and frames_map['slash']:
            self.anims['slash'] = Animation(frames_map['slash'], speed_ms=80, loop=False)
        if 'cast' in frames_map and frames_map['cast']:
            self.anims['cast'] = Animation(frames_map['cast'], speed_ms=120, loop=False)
        if 'die' in frames_map and frames_map['die']:
            self.anims['die'] = Animation(frames_map['die'], speed_ms=150, loop=False)

        self.current = 'idle'
        self.anim = self.anims.get(self.current)

    def set_animation(self, name: str, reset: bool = True):
        if name == self.current:
            return
        if name not in self.anims:
            return
        self.current = name
        self.anim = self.anims[name]
        if reset:
            self.anim.reset()

    def update(self, dt_ms: int, keys):
        # movement
        self.vx = 0
        self.vy = 0
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_left = True
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_left = False
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.speed
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.speed
            moving = True

        # apply movement (dt in ms -> convert to seconds)
        self.x += int(self.vx * (dt_ms / 1000.0))
        self.y += int(self.vy * (dt_ms / 1000.0))

        # determine direction suffix for animations
        dir_suffix = ''
        if moving:
            if self.vx < 0:
                dir_suffix = '_left'
            elif self.vx > 0:
                dir_suffix = '_right'
            elif self.vy < 0:
                dir_suffix = '_up'
            elif self.vy > 0:
                dir_suffix = '_down'

        # actions override movement
        if keys[pygame.K_SPACE]:
            # slash
            target = 'slash'
            if dir_suffix and (target + dir_suffix) in self.anims:
                target = target + dir_suffix
            if self.current != target or self.anim.is_finished():
                self.set_animation(target)
        elif keys[pygame.K_f]:
            target = 'cast'
            if dir_suffix and (target + dir_suffix) in self.anims:
                target = target + dir_suffix
            if self.current != target or self.anim.is_finished():
                self.set_animation(target)
        elif keys[pygame.K_k]:
            if self.current != 'die':
                self.set_animation('die')
        else:
            # if currently in a non-looping action and it's not finished, keep it
            if self.current in ('slash', 'cast') and not self.anim.is_finished():
                pass
            elif self.current == 'die':
                # dead — freeze
                pass
            else:
                # movement determines idle/walk
                if moving:
                    target = 'walk' + dir_suffix if dir_suffix and ('walk' + dir_suffix) in self.anims else 'walk'
                    # avoid resetting if already playing the same animation
                    if self.current != target:
                        self.set_animation(target)
                else:
                    target = 'idle' + dir_suffix if dir_suffix and ('idle' + dir_suffix) in self.anims else 'idle'
                    if self.current != target:
                        self.set_animation(target)

        # update current animation
        if self.anim:
            self.anim.update(dt_ms)

    def draw(self, surface: pygame.Surface):
        frame = self.anim.get_current() if self.anim else None
        if frame is None:
            # draw placeholder
            pygame.draw.rect(surface, (200, 120, 120), (self.x, self.y, FRAME_WIDTH, FRAME_HEIGHT))
            return
        img = frame
        if self.facing_left:
            img = pygame.transform.flip(frame, True, False)
        surface.blit(img, (self.x, self.y))

# --- MAIN GAME ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('LPC Animation Demo')
    clock = pygame.time.Clock()

    # load spritesheet
    # prefer per-animation files under SPRITE_SHEET_DIR if available
    frames_map = {}
    loaded_frames = False
    import os, json
    anim_names = ['idle', 'walk', 'slash', 'cast', 'die']
    # if there's a character.json in the directory, use it to discover animation names
    cj_path = os.path.join(SPRITE_SHEET_DIR, 'character.json')
    if os.path.exists(cj_path):
        try:
            with open(cj_path, 'r', encoding='utf-8') as f:
                cj = json.load(f)
            # prefer enabledAnimations keys that are present
            enabled = cj.get('enabledAnimations') or {}
            # gather names where value is True or keys present in supported list
            from_json = [k for k, v in enabled.items() if isinstance(v, bool) and v]
            if from_json:
                anim_names = from_json + [n for n in anim_names if n not in from_json]
        except Exception as e:
            print('Warning: failed to parse character.json:', e)

    if os.path.isdir(SPRITE_SHEET_DIR):
        # try each animation name discovered
        for name in anim_names:
            path = os.path.join(SPRITE_SHEET_DIR, f"{name}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # auto-slice horizontally by FRAME_WIDTH; support multiple rows (directions)
                    w, h = img.get_size()
                    cols = w // FRAME_WIDTH if FRAME_WIDTH else 0
                    rows = h // FRAME_HEIGHT if FRAME_HEIGHT else 0
                    # user's sheet order: row0=up, row1=left, row2=down, row3=right
                    dirs = ['up', 'left', 'down', 'right']
                    # collect per-row frames
                    for r in range(max(1, rows)):
                        frames = []
                        for i in range(cols):
                            surf = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA, 32)
                            surf.blit(img, (0, 0), (i*FRAME_WIDTH, r*FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
                            frames.append(surf)
                        if frames:
                            if rows > 1 and r < len(dirs):
                                frames_map[f"{name}_{dirs[r]}"] = frames
                            else:
                                # fallback to name without suffix (use first row)
                                frames_map.setdefault(name, frames)
                            loaded_frames = True
                except Exception as e:
                    print('Warning loading', path, e)

    if loaded_frames:
        player = Player((WINDOW_WIDTH - FRAME_WIDTH)//2, (WINDOW_HEIGHT - FRAME_HEIGHT)//2, frames_map)
    else:
        # fallback to a single big sheet path
        try:
            sheet = SpriteSheet(SPRITE_SHEET_PATH)
        except Exception as e:
            print('Failed to load sprite sheet:', e)
            print('Make sure SPRITE_SHEET_PATH points to a valid PNG file, or provide per-animation files in', SPRITE_SHEET_DIR)
            pygame.quit()
            sys.exit(1)
        player = Player((WINDOW_WIDTH - FRAME_WIDTH)//2, (WINDOW_HEIGHT - FRAME_HEIGHT)//2, sheet)

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        keys = pygame.key.get_pressed()
        player.update(dt, keys)

        screen.fill((40, 40, 50))
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
