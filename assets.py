import os
import pygame
from typing import Dict, Tuple

ROOT = os.path.dirname(__file__)
ART_DIR = os.path.join(ROOT, 'art')

# containers
SURFACES: Dict[str, pygame.Surface] = {}
ANIMATIONS: Dict[tuple, Dict[str, list]] = {}


def _load_folder(folder: str):
    path = os.path.join(ART_DIR, folder)
    if not os.path.isdir(path):
        return
    for fn in os.listdir(path):
        if not fn.lower().endswith('.png'):
            continue
        key = f"{folder}/{fn}"
        full = os.path.join(path, fn)
        try:
            # pygame requires a video mode to be set before calling convert()/convert_alpha()
            # To stay safe during headless or early-load contexts, load without converting
            # and only convert when blitting if needed.
            surf = pygame.image.load(full)
            # store the raw surface; callers can call convert_alpha() after display is set
            SURFACES[key] = surf
        except Exception as e:
            print('Failed to load', full, e)


def load_assets():
    """Load all PNGs under art/ and subfolders into SURFACES.

    Keys are returned as 'characters/maria_player.png' etc.
    """
    pygame.init()
    for folder in ('characters', 'objects', 'backgrounds'):
        _load_folder(folder)


def get(key: str) -> pygame.Surface:
    """Return a surface by key, or None if missing."""
    s = SURFACES.get(key)
    # lazy convert if display set
    if s is not None and hasattr(pygame, 'display') and pygame.display.get_init():
        try:
            # convert_alpha may fail if surface already converted; ignore
            return s.convert_alpha()
        except Exception:
            return s
    return s


def get_scaled(key: str, size: Tuple[int, int]) -> pygame.Surface:
    s = get(key)
    if s is None:
        return None
    return pygame.transform.smoothscale(s, size)


def _slice_horizontal_strip(surf: pygame.Surface, frame_size: Tuple[int, int] = None) -> list:
    """If the surface is a horizontal strip of same-size frames, return list of frames.

    If frame_size is provided (w,h), slice the strip into frames of that size.
    Otherwise fall back to the square-frame heuristic (width divisible by height).
    """
    w, h = surf.get_size()
    frames = []

    # If caller provided the expected frame size, use it when it matches the sheet layout
    if frame_size is not None:
        fw, fh = frame_size
        if fw > 0 and fh > 0:
            # If the sheet is a single row matching the requested height
            if h == fh and w > fw and (w % fw) == 0:
                count = w // fw
                for i in range(count):
                    rect = pygame.Rect(i * fw, 0, fw, fh)
                    frame = surf.subsurface(rect).copy()
                    frames.append(frame)
                return frames
            # If the sheet contains multiple rows/columns of the requested frame size,
            # slice into row-major frames (rows x cols).
            if (h % fh) == 0 and (w % fw) == 0 and h >= fh and w >= fw:
                rows = h // fh
                cols = w // fw
                for r in range(rows):
                    for c in range(cols):
                        rect = pygame.Rect(c * fw, r * fh, fw, fh)
                        frame = surf.subsurface(rect).copy()
                        frames.append(frame)
                return frames

    # fallback: square-frame heuristic (legacy behavior)
    if h > 0 and w > h and (w % h) == 0:
        count = w // h
        for i in range(count):
            rect = pygame.Rect(i * h, 0, h, h)
            frame = surf.subsurface(rect).copy()
            frames.append(frame)
    # If we still didn't find frames and a frame_size was provided, try some
    # common LPC frame sizes as a fallback (64x64, 48x64, 32x32).
    if not frames and frame_size is not None:
        common = [(64, 64), (48, 64), (32, 32)]
        for cw, ch in common:
            if cw > 0 and ch > 0 and (w % cw) == 0 and (h % ch) == 0:
                cols = w // cw
                rows = h // ch
                for r in range(rows):
                    for c in range(cols):
                        rect = pygame.Rect(c * cw, r * ch, cw, ch)
                        frames.append(surf.subsurface(rect).copy())
                if frames:
                    return frames
    return frames


def get_animations(character_name: str, size: Tuple[int, int] = None) -> Dict[str, list]:
    """Return a dict of animations for character folders under art/characters/<name>/.

    Behavior:
    - If a file named <anim>.png exists and is a horizontal strip, slice it into frames.
    - Else, collect files like <anim>_0.png, <anim>_1.png, ... sorted numerically.
    Results cached in ANIMATIONS.
    """
    cache_key = (character_name, size)
    if cache_key in ANIMATIONS:
        return ANIMATIONS[cache_key]

    animations: Dict[str, list] = {}
    folder = os.path.join(ART_DIR, 'characters', character_name)
    if not os.path.isdir(folder):
        ANIMATIONS[character_name] = animations
        return animations

    # list png files
    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    # map base names
    by_base = {}
    for fn in files:
        name = os.path.splitext(fn)[0]
        by_base.setdefault(name, []).append(fn)

    for base, fns in by_base.items():
        # try direct strip file first (single file with that base)
        if len(fns) == 1:
            full = os.path.join(folder, fns[0])
            try:
                surf = pygame.image.load(full)
                # strip-slicing heuristic - pass requested frame size (if any)
                frames = _slice_horizontal_strip(surf, frame_size=size)
                if frames:
                    # Determine actual frame size from extracted frames (some sheets
                    # may not match the requested `size`). Use that to compute rows/cols
                    # and create per-row direction animations (up,left,down,right).
                    try:
                        sw, sh = surf.get_size()
                        fw_actual = frames[0].get_width()
                        fh_actual = frames[0].get_height()
                        if fw_actual > 0 and fh_actual > 0 and (sw % fw_actual) == 0 and (sh % fh_actual) == 0:
                            cols = sw // fw_actual
                            rows = sh // fh_actual
                            if rows >= 1 and cols > 0:
                                dir_names = ['up', 'left', 'down', 'right']
                                for r in range(min(rows, 4)):
                                    start = r * cols
                                    row_frames = frames[start:start+cols]
                                    animations[f"{base}_{dir_names[r]}"] = row_frames
                                # keep the flattened frames as the base key too
                                animations[base] = frames
                                SURFACES[f'characters/{character_name}/{fns[0]}'] = surf
                                continue
                    except Exception:
                        pass
                    # default: store flat frames under base
                    animations[base] = frames
                    # also register raw surface under SURFACES for backwards compatibility
                    SURFACES[f'characters/{character_name}/{fns[0]}'] = surf
                    continue
                else:
                    # single-frame image
                    animations[base] = [surf]
                    SURFACES[f'characters/{character_name}/{fns[0]}'] = surf
                    continue
            except Exception as e:
                print('Failed to load animation', full, e)

        # otherwise try numbered frames like walk_0, walk_1
        # sort by suffix if present
            numbered = []
        for fn in fns:
            full = os.path.join(folder, fn)
            try:
                surf = pygame.image.load(full)
                numbered.append((fn, surf))
                SURFACES[f'characters/{character_name}/{fn}'] = surf
            except Exception:
                pass
        if numbered:
            # sort by filename (attempt numeric suffix sort)
            def sort_key(t):
                fn = t[0]
                parts = fn.rsplit('_', 1)
                if len(parts) == 2 and parts[1].split('.')[0].isdigit():
                    return int(parts[1].split('.')[0])
                return fn

            numbered.sort(key=sort_key)
            frames = [t[1] for t in numbered]
            animations[base] = frames

    # if size requested, scale frames
    if size is not None:
        scaled: Dict[str, list] = {}
        for k, frames in animations.items():
            scaled[k] = [pygame.transform.smoothscale(f, size) for f in frames]
        ANIMATIONS[cache_key] = scaled
        return scaled

    ANIMATIONS[cache_key] = animations
    return animations
