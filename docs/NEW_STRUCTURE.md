# Project Structure Reorganization

## New Structure

```
our_adventure/
├── game.py                 # Main entry point (NEW - cleaner implementation)
├── proposal_game.py        # Legacy entry point (kept for compatibility)
├── requirements.txt
├── README.md
│
├── src/                    # Source code (NEW)
│   ├── __init__.py
│   ├── core/              # Core game systems
│   │   ├── __init__.py
│   │   ├── scene.py       # Base Scene and SceneManager
│   │   ├── player.py      # Player character
│   │   ├── assets.py      # Asset loading
│   │   └── dialogue.py    # Dialogue system
│   │
│   ├── scenes/            # All game scenes
│   │   ├── __init__.py
│   │   ├── bumble_scene.py
│   │   ├── bumble_splash_scene.py
│   │   ├── drive_scene.py
│   │   ├── apartment_scene.py
│   │   ├── disney_scene.py
│   │   ├── moving_scene.py
│   │   ├── dinner_scene.py
│   │   ├── menu_scene.py
│   │   └── transition_scene.py
│   │
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── tilemap.py     # Tilemap loading
│       ├── car_sprites.py # Car sprite utilities
│       └── lpc_demo.py    # Animation system
│
├── art/                   # Game assets
│   ├── music/            # Background music
│   ├── scenes/           # Scene-specific assets
│   │   ├── bumble/
│   │   ├── drive/
│   │   ├── apartment/
│   │   ├── disney/
│   │   ├── dinner/
│   │   └── moving/
│   ├── characters/       # Character sprites
│   └── objects/          # Game objects
│
├── docs/                 # Documentation
│   ├── MUSIC_GUIDE.md
│   └── REORGANIZATION_SUMMARY.md
│
└── scripts/             # Utility scripts
    ├── generate_placeholders.py
    └── generate_maria_placeholders.py
```

## Key Improvements

### 1. **Organized Source Code**
- All Python code now in `src/` directory
- Clear separation: `core/`, `scenes/`, `utils/`
- Proper Python package structure with `__init__.py` files

### 2. **New Main Entry Point**
- `game.py` - Clean, modern implementation
- Better organized with `Game` and `GameConfig` classes
- Improved error handling and logging
- `proposal_game.py` kept for backward compatibility

### 3. **Better Import System**
```python
# Old way (scattered imports):
from scene import Scene
from player import Player
from bumble_scene import BumbleScene

# New way (organized imports):
from src.core import Scene, Player
from src.scenes import BumbleScene
from src.utils import load_tilemap
```

### 4. **Documentation Organization**
- All docs moved to `docs/` folder
- Easier to find guides and references

### 5. **Scene Management**
- Centralized scene shortcuts in GameConfig
- Easy to add/modify scenes
- Better keyboard shortcut handling

## Running the Game

### New Entry Point (Recommended):
```bash
python game.py
```

### Legacy Entry Point (Still works):
```bash
python proposal_game.py
```

## Keyboard Shortcuts

- **ESC** - Quit game
- **M** - Open menu
- **1** - Jump to Bumble scene
- **2** - Jump to Drive scene
- **3** - Jump to Apartment scene
- **4** - Jump to Disney scene
- **5** - Jump to Moving scene
- **6** - Jump to Dinner scene

## Benefits

### For Development:
- **Easier navigation** - Know exactly where to find files
- **Better imports** - Clear module dependencies
- **Scalability** - Easy to add new scenes/systems
- **Maintenance** - Organized code is easier to debug

### For Performance:
- **Modular loading** - Only load what you need
- **Clear dependencies** - Easier to optimize
- **Better separation** - Reduces coupling

### For Collaboration:
- **Standard structure** - Familiar to Python developers
- **Clear organization** - New contributors can navigate easily
- **Documentation** - All docs in one place

## Migration Notes

### Import Updates Needed:
All scene files need import updates. Pattern:
```python
# Before:
from scene import Scene
from dialogue import DialogueBox
from tilemap import load_tilemap

# After:
from src.core.scene import Scene
from src.core.dialogue import DialogueBox
from src.utils.tilemap import load_tilemap
```

### Asset Paths:
Asset paths remain unchanged:
- `art/scenes/bumble/...`
- `art/characters/...`
- `art/music/...`

## Next Steps

1. ✅ Created new folder structure
2. ✅ Moved files to organized locations
3. ✅ Created __init__.py for packages
4. ✅ Created new game.py entry point
5. ⏳ Update imports in all scene files
6. ⏳ Test all scenes work correctly
7. ⏳ Update README with new structure

## File Checklist

### Core Files:
- [x] src/core/scene.py
- [x] src/core/player.py
- [x] src/core/assets.py
- [x] src/core/dialogue.py

### Scene Files:
- [x] src/scenes/bumble_scene.py
- [x] src/scenes/bumble_splash_scene.py
- [x] src/scenes/drive_scene.py
- [x] src/scenes/apartment_scene.py
- [x] src/scenes/disney_scene.py
- [x] src/scenes/moving_scene.py
- [x] src/scenes/dinner_scene.py
- [x] src/scenes/menu_scene.py
- [x] src/scenes/transition_scene.py

### Utility Files:
- [x] src/utils/tilemap.py
- [x] src/utils/car_sprites.py
- [x] src/utils/lpc_demo.py

### Documentation:
- [x] docs/MUSIC_GUIDE.md
- [x] docs/REORGANIZATION_SUMMARY.md
