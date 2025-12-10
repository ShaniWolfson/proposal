# Project Reorganization Summary

## Changes Made (December 9, 2025)

### 1. Art Asset Reorganization

Created scene-specific folders under `art/scenes/` to organize assets by their usage:

#### New Folder Structure:
```
art/scenes/
├── bumble/
│   ├── Bumble_home.jpg (splash screen)
│   ├── bumble_logo.png
│   ├── red_heart.png (match animation)
│   └── heart.png (shared with other scenes)
├── drive/
│   └── date_drive/
│       ├── nightroad.png
│       ├── dayroad.png
│       └── '90s vehicles.png
├── apartment/
│   └── apartment/
│       ├── untitled.png
│       ├── apartment.tmj
│       └── [collision data files]
├── disney/
│   ├── castle.png
│   └── castle_background.png
├── dinner/
│   └── dinner/
│       ├── index.html
│       ├── images/
│       ├── data/
│       └── classes/
└── moving/
    (reserved for future assets)
```

### 2. Code Updates

Updated file paths in the following scene files:
- **bumble_scene.py**: Updated heart image path to `art/scenes/bumble/red_heart.png`
- **bumble_splash_scene.py**: Updated splash image to `art/scenes/bumble/Bumble_home.jpg`
- **disney_scene.py**: 
  - Castle image: `art/scenes/disney/castle.png`
  - Heart image: `art/scenes/bumble/heart.png` (shared resource)
- **drive_scene.py**: Updated all paths to `art/scenes/drive/date_drive/`
- **apartment_scene.py**: Updated folder path to `art/scenes/apartment/apartment/`

### 3. Removed Unused Files

Moved unused/test scripts to `unused_scripts/` folder:
- **climbing_scene.py** - Unused climbing gym scene (no reference in game flow)
- **disney_scene_old.py** - Old version of Disney scene
- **main.py** - Old entry point (replaced by proposal_game.py)
- **lpc_demo.py** - Demo/test file

Deleted unused assets:
- **climbing_gym_bg.png** - Asset for unused climbing scene
- **download.jpg** - Reference image for UI design (no longer needed)

### 4. Active Game Scenes

The following scenes are currently used in the game flow:
1. **BumbleSplashScene** → Splash screen with Bumble logo
2. **BumbleScene** → Dating app swipe interface
3. **TransitionScene** → Text transitions between scenes
4. **DriveScene** → Driving to the city
5. **ApartmentScene** → First date at Shani's apartment
6. **DisneyScene** → Disney World castle scene with fireworks
7. **MovingScene** → Moving day scene
8. **DinnerScene** → Dinner proposal scene
9. **MenuScene** → Navigation menu (accessible with M key)

### 5. Benefits

- **Improved Organization**: Assets are now grouped by scene, making it easier to find related files
- **Cleaner Codebase**: Removed unused scripts that were cluttering the project root
- **Better Maintainability**: Clear separation between active and unused code
- **Easier Asset Management**: Each scene's assets are self-contained in their own folder

### 6. Testing

✅ Game tested and confirmed working after reorganization
✅ All asset paths updated correctly
✅ No runtime errors

### Notes

- The `heart.png` in `art/scenes/bumble/` is shared between bumble and disney scenes
- Character sprites remain in `art/characters/` as they're used across multiple scenes
- The `art/objects/` folder is preserved for game objects used across scenes
