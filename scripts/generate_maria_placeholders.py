"""Generate placeholder horizontal-strip PNGs for Maria animations.
Creates files under art/characters/maria: idle.png, walk.png, slash.png, cast.png, die.png
Each file is a horizontal strip where each frame is 64x64.
"""
import os
import pygame

FRAME_W = 64
FRAME_H = 64
OUT_DIR = os.path.join('art', 'characters', 'maria')
ANIMS = {
    'idle': 4,
    'walk': 8,
    'slash': 6,
    'cast': 6,
    'die': 6,
}

os.makedirs(OUT_DIR, exist_ok=True)

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 28)

for name, count in ANIMS.items():
    surf = pygame.Surface((FRAME_W * count, FRAME_H), pygame.SRCALPHA, 32)
    for i in range(count):
        x = i * FRAME_W
        # color per animation for visual distinction
        if name == 'idle':
            color = (200, 200, 255)
        elif name == 'walk':
            color = (200, 255, 200)
        elif name == 'slash':
            color = (255, 200, 200)
        elif name == 'cast':
            color = (255, 230, 180)
        elif name == 'die':
            color = (150, 150, 150)
        else:
            color = (180, 180, 180)
        pygame.draw.rect(surf, color, (x + 2, 2, FRAME_W - 4, FRAME_H - 4))
        # draw frame index
        txt = font.render(str(i), True, (10, 10, 10))
        surf.blit(txt, (x + 8, 8))
    out_path = os.path.join(OUT_DIR, f"{name}.png")
    pygame.image.save(surf, out_path)
    print('Wrote', out_path)

print('Done generating placeholders')
pygame.quit()
