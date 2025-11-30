"""Generate placeholder PNG sprites for the project using pygame.

Run from the project root after creating / activating a Python environment with pygame installed:

    py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    py scripts\generate_placeholders.py

This will populate `art/characters`, `art/objects`, `art/backgrounds` with simple colored PNGs and text labels so you can preview scenes before final art is ready.
"""
import os
import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
ART_DIR = os.path.join(PROJECT_ROOT, 'art')
CHAR_DIR = os.path.join(ART_DIR, 'characters')
OBJ_DIR = os.path.join(ART_DIR, 'objects')
BG_DIR = os.path.join(ART_DIR, 'backgrounds')

os.makedirs(CHAR_DIR, exist_ok=True)
os.makedirs(OBJ_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)

pygame.init()
# font for labels
try:
    FONT = pygame.font.SysFont(None, 20)
except Exception:
    pygame.font.init()
    FONT = pygame.font.SysFont(None, 20)

# helper to create and save a surface with label

def make_image(path, size, color, label=None):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    if label:
        # draw a semi-transparent box for the label
        label_surf = FONT.render(label, True, (255, 255, 255))
        # drop a small shadow
        surf.blit(FONT.render(label, True, (0, 0, 0)), (6, 6))
        surf.blit(label_surf, (4, 4))
    pygame.image.save(surf, path)
    print('Wrote', path)

# Characters
chars = [
    ('maria_player.png', (48, 48), (200, 120, 180), 'Maria'),
    ('shani_player.png', (48, 48), (120, 160, 220), 'Shani'),
    ('lexa_dog.png', (32, 24), (180, 140, 100), 'Lexa'),
    ('friend_loriana.png', (48, 48), (220, 160, 180), 'Loriana'),
    ('friend_oresti.png', (48, 48), (160, 200, 160), 'Oresti'),
    ('friend_marissa.png', (48, 48), (200, 200, 140), 'Marissa'),
    ('brother_gio.png', (48, 48), (180, 160, 220), 'Gio'),
    ('mom.png', (48, 48), (220, 180, 160), 'Mom'),
    ('dad.png', (48, 48), (160, 180, 220), 'Dad'),
]
for name, size, color, label in chars:
    make_image(os.path.join(CHAR_DIR, name), size, color, label)

# Objects
objects = [
    ('phone_bumble.png', (240, 400), (30, 30, 40), 'Phone'),
    ('profile_bad_1.png', (200, 280), (80, 60, 80), 'Bad1'),
    ('profile_bad_2.png', (200, 280), (80, 60, 100), 'Bad2'),
    ('profile_shani.png', (200, 280), (120, 160, 220), 'Shani'),
    ('wine_bottle.png', (32, 64), (90, 20, 120), 'Wine'),
    ('wnrs_cards.png', (48, 28), (220, 220, 220), 'Cards'),
    ('couch.png', (128, 64), (120, 80, 90), 'Couch'),
    ('tv.png', (64, 48), (30, 30, 30), 'TV'),
    ('box_shani.png', (64, 64), (200, 180, 140), "Shani's Box"),
    ('box_maria.png', (64, 64), (200, 140, 180), "Maria's Box"),
    ('box_lexa.png', (64, 64), (160, 120, 100), "Lexa's Box"),
    ('cake.png', (64, 48), (240, 200, 180), 'Cake'),
    ('car_blue.png', (96, 48), (60, 140, 220), 'Car'),
    ('uhaul_truck.png', (120, 60), (240, 140, 60), 'UHaul'),
    ('pothole.png', (32, 16), (60, 50, 40), 'Pothole'),
    ('jaywalker.png', (32, 48), (200, 160, 120), 'Jaywalker'),
]
for name, size, color, label in objects:
    make_image(os.path.join(OBJ_DIR, name), size, color, label)

# Backgrounds
bg = [
    ('apt_background.png', (1280, 720), (90, 70, 80), 'Apt'),
    ('castle_background.png', (1280, 720), (18, 24, 80), 'Castle'),
    ('climbing_gym_bg.png', (1280, 720), (40, 60, 80), 'Climb Gym'),
    ('moving_street_bg.png', (1280, 720), (120, 180, 240), 'Moving Street'),
    ('dinner_room_bg.png', (1280, 720), (80, 40, 30), 'Dinner'),
]
for name, size, color, label in bg:
    make_image(os.path.join(BG_DIR, name), size, color, label)

print('Placeholder generation complete.')
pygame.quit()
