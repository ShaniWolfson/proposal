import pygame
import sys
import os
from typing import List, Dict, Tuple

# --- CONSTANTS ---
FRAME_WIDTH = 64
FRAME_HEIGHT = 64

IDLE_FRAMES = 4
WALK_FRAMES = 8
SIT_FRAMES = 4

IDLE_SPEED = 200
WALK_SPEED = 100
SIT_SPEED = 400

IDLE_PATH = 'idle.png'
WALK_PATH = 'walk.png'
SIT_PATH = 'sit.png'

WINDOW_W = 800
WINDOW_H = 600

# --- SPRITESHEET HELPER ---
class SpriteSheet:
    def __init__(self, path: str):
        self.path = path
        self.sheet = pygame.image.load(path).convert_alpha()

    def image_at(self, rect: Tuple[int,int,int,int]) -> pygame.Surface:
        x,y,w,h = rect
        surf = pygame.Surface((w,h), pygame.SRCALPHA, 32)
        surf.blit(self.sheet, (0,0), (x,y,w,h))
        return surf

    def load_strip(self, rect: Tuple[int,int,int,int], frame_count: int) -> List[pygame.Surface]:
        x,y,w,h = rect
        frames = []
        for i in range(frame_count):
            frames.append(self.image_at((x + i*w, y, w, h)))
        return frames

# --- ANIMATION ---
class Animation:
    def __init__(self, frames: List[pygame.Surface], speed_ms: int = 100, loop: bool = True):
        self.frames = frames
        self.speed = speed_ms
        self.loop = loop
        self.time = 0
        self.index = 0
        # compute last visible frame index (skip fully-transparent frames)
        self.visible_last_index = 0
        # last visible frame seen while the animation is playing
        self.last_visible_index = None

        try:
            for i in range(len(frames)-1, -1, -1):
                f = frames[i]
                try:
                    m = pygame.mask.from_surface(f)
                    if m.count() > 0:
                        self.visible_last_index = i
                        break
                except Exception:
                    # fallback: assume frame visible
                    self.visible_last_index = i
                    break
        except Exception:
            self.visible_last_index = max(0, len(frames)-1)

    def reset(self):
        self.time = 0
        self.index = 0
        # recompute last_visible_index from visible_last_index
        if hasattr(self, 'visible_last_index'):
            self.last_visible_index = self.visible_last_index
        else:
            self.last_visible_index = None

    def update(self, dt_ms: int):
        if len(self.frames) <= 1:
            return
        self.time += dt_ms
        while self.time >= self.speed:
            self.time -= self.speed
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
        # update last_visible_index as we progress
        try:
            f = self.frames[self.index]
            m = pygame.mask.from_surface(f)
            if m.count() > 0:
                self.last_visible_index = self.index
        except Exception:
            # if mask fails, be conservative and set last_visible_index
            self.last_visible_index = self.index

    def get_frame(self) -> pygame.Surface:
        if not self.frames:
            return None
        # Prefer the current index. If that frame is fully transparent, fall back
        # to the most recently seen visible frame (cached in last_visible_index),
        # then to visible_last_index, then scan backward as a final fallback.
        frame = self.frames[self.index]
        try:
            m = pygame.mask.from_surface(frame)
            if m.count() > 0:
                return frame
        except Exception:
            return frame
        # If we have a cached recently visible frame, use it
        idx = getattr(self, 'last_visible_index', None)
        if idx is not None and 0 <= idx < len(self.frames):
            return self.frames[idx]

        # fallback to scanning backwards for a visible frame
        for i in range(self.index - 1, -1, -1):
            f = self.frames[i]
            try:
                m = pygame.mask.from_surface(f)
                if m.count() > 0:
                    return f
            except Exception:
                return f

        # as a last resort, try visible_last_index if set
        idx = getattr(self, 'visible_last_index', None)
        if idx is not None and 0 <= idx < len(self.frames):
            return self.frames[idx]

        return frame

# --- ANIMATION MANAGER ---
class AnimationManager:
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current: str = None

    def add(self, name: str, anim: Animation):
        self.animations[name] = anim

    def play(self, name: str):
        if name == self.current:
            return
        if name not in self.animations:
            return
        self.current = name
        self.animations[name].reset()

    def hold_last(self, name: str):
        """Switch to the animation and set it to its final frame (hold)."""
        if name == self.current:
            return
        if name not in self.animations:
            return
        anim = self.animations[name]
        self.current = name
        anim.loop = False
        # set to last visible frame to avoid holding a blank/transparent frame
        idx = getattr(anim, 'visible_last_index', None)
        if idx is None:
            idx = len(anim.frames) - 1

        # verify that chosen idx is actually visible; if not, scan backwards
        chosen = None
        for i in range(idx, -1, -1):
            try:
                m = pygame.mask.from_surface(anim.frames[i])
                if m.count() > 0:
                    chosen = i
                    break
            except Exception:
                chosen = i
                break

        if chosen is None:
            chosen = max(0, len(anim.frames) - 1)

        anim.index = chosen
        anim.time = 0

    def update(self, dt_ms: int):
        if self.current and self.current in self.animations:
            self.animations[self.current].update(dt_ms)

    def draw(self, surface: pygame.Surface, x:int, y:int, scale:float=1.0):
        if not self.current:
            return
        frame = self.animations[self.current].get_frame()
        if frame:
            if scale != 1.0:
                new_width = int(frame.get_width() * scale)
                new_height = int(frame.get_height() * scale)
                frame = pygame.transform.scale(frame, (new_width, new_height))
            surface.blit(frame, (x, y))

# --- PLAYER ---
class Player:
    def __init__(self, x: int, y: int, assets_dir: str):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 180
        self.direction = 'down'  # down, left, right, up
        self.sitting = False
        # True while movement keys are currently held
        self.moving_flag = False

        self.anim_mgr = AnimationManager()
        self.assets_dir = assets_dir
        self.load_animations()
        self.anim_mgr.play('idle_down')

    def load_animations(self):
        # expected files in assets_dir: idle.png, walk.png, sit.png
        def load_grid(path, frames_per_row):
            full = os.path.join(self.assets_dir, path)
            if not os.path.exists(full):
                return {}
            ss = SpriteSheet(full)
            w,h = ss.sheet.get_size()
            rows = h // FRAME_HEIGHT
            cols = frames_per_row
            # user's sheet order: row0=up, row1=left, row2=down, row3=right
            dir_names = ['up','left','down','right']
            out = {}
            for r in range(min(rows,4)):
                frames = ss.load_strip((0, r*FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT), cols)
                out[dir_names[r]] = frames
            return out

        idle_map = load_grid(IDLE_PATH, IDLE_FRAMES)
        walk_map = load_grid(WALK_PATH, WALK_FRAMES)
        sit_map = load_grid(SIT_PATH, SIT_FRAMES)

        # build Animation objects
        for d in ['down','left','right','up']:
            if d in idle_map:
                # idle should play once and hold last frame
                self.anim_mgr.add(f'idle_{d}', Animation(idle_map[d], speed_ms=IDLE_SPEED, loop=False))
            if d in walk_map:
                self.anim_mgr.add(f'walk_{d}', Animation(walk_map[d], speed_ms=WALK_SPEED, loop=True))
            if d in sit_map:
                self.anim_mgr.add(f'sit_{d}', Animation(sit_map[d], speed_ms=SIT_SPEED, loop=False))

    def handle_input(self, keys):
        if self.sitting:
            self.vx = 0
            self.vy = 0
            self.moving_flag = False
            return
        self.vx = 0
        self.vy = 0
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.direction = 'left'
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.direction = 'right'
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.speed
            self.direction = 'up'
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.speed
            self.direction = 'down'
            moving = True

        # record whether movement keys are currently pressed
        self.moving_flag = moving

    def update(self, dt_ms:int):
        # apply movement unless sitting
        if not self.sitting:
            self.x += int(self.vx * (dt_ms/1000.0))
            self.y += int(self.vy * (dt_ms/1000.0))

        # choose animation
        if self.sitting:
            key = f'sit_{self.direction}'
            if key in self.anim_mgr.animations:
                self.anim_mgr.play(key)
        else:
            # use movement flag (true only while movement keys are held)
            if self.moving_flag:
                key = f'walk_{self.direction}'
                if key in self.anim_mgr.animations:
                    self.anim_mgr.play(key)
            else:
                key = f'idle_{self.direction}'
                if key in self.anim_mgr.animations:
                    # hold the last frame of idle so it doesn't blink out
                    self.anim_mgr.hold_last(key)

        self.anim_mgr.update(dt_ms)

    def draw(self, surface: pygame.Surface):
        self.anim_mgr.draw(surface, self.x, self.y)

# --- MAIN GAME ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    assets_dir = os.path.join('art', 'characters', 'maria')
    player = Player(WINDOW_W//2, WINDOW_H//2, assets_dir)

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    player.sitting = not player.sitting

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(dt)

        screen.fill((60,60,80))
        player.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
