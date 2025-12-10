# Music Integration Guide

## Overview
Each scene can now have its own background music that automatically plays when the scene starts and stops when it ends.

## Folder Structure
```
art/music/
├── bumble/         # Dating app scene music
├── drive/          # Driving scene music
├── apartment/      # First date apartment music
├── disney/         # Disney World castle music
├── moving/         # U-Haul moving day music
└── dinner/         # Family dinner/proposal music
```

## How to Add Music to a Scene

### Step 1: Add your music file
Place your music file (mp3, ogg, wav) in the appropriate folder under `art/music/`

Example:
- `art/music/bumble/upbeat_dating.mp3`
- `art/music/drive/city_night_drive.mp3`
- `art/music/disney/romantic_castle.mp3`

### Step 2: Set the music_file in your scene's __init__
In your scene's `__init__` method, set the `self.music_file` attribute:

```python
class BumbleScene(Scene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.music_file = "art/music/bumble/upbeat_dating.mp3"
        # ... rest of init code
```

### Step 3: (Optional) Customize volume or loop behavior
If you want different volume or loop settings, override the start() method:

```python
def start(self):
    # Custom music settings
    if self.music_file:
        self._play_music(self.music_file, volume=0.3, loops=-1)
    
    # ... rest of start code
```

## Recommended Music for Each Scene

### 1. Bumble Scene
- **Mood**: Upbeat, modern, playful
- **Examples**: Pop instrumentals, electronic upbeat tracks
- **Duration**: ~30 seconds (loops)

### 2. Drive Scene (First Date)
- **Mood**: Romantic, anticipatory, smooth
- **Examples**: Jazz, smooth R&B, lo-fi hip hop
- **Duration**: ~15 seconds (loops)

### 3. Apartment Scene
- **Mood**: Intimate, warm, cozy
- **Examples**: Soft acoustic, indie folk, ambient
- **Duration**: 1-2 minutes (loops)

### 4. Disney Scene
- **Mood**: Magical, romantic, orchestral
- **Examples**: Disney-inspired instrumentals, fairy tale music
- **Duration**: ~45 seconds (loops)

### 5. Moving Scene (U-Haul Drive)
- **Mood**: Optimistic, energetic, forward-looking
- **Examples**: Upbeat indie, feel-good pop
- **Duration**: ~15 seconds (loops)

### 6. Dinner Scene
- **Mood**: Nervous excitement, emotional, building to romantic
- **Examples**: Italian restaurant ambiance, classical strings, emotional piano
- **Duration**: 2-3 minutes (loops)

## Free Music Resources

### Royalty-Free Music Sites:
1. **FreePD.com** - Public domain music
2. **Incompetech.com** - Kevin MacLeod's music (CC BY)
3. **Purple Planet Music** - Free music for games
4. **Bensound.com** - Royalty-free tracks
5. **YouTube Audio Library** - Free music and sound effects

### Sound Effects (Optional):
- **Freesound.org** - User-uploaded sounds
- **Zapsplat.com** - Free sound effects

## Technical Notes

- **Supported Formats**: MP3, OGG, WAV (OGG recommended for best compatibility)
- **File Size**: Keep files under 5MB for smooth loading
- **Volume**: Default is 0.5 (50%). Adjust in `_play_music()` call
- **Loops**: Default is -1 (infinite). Set to 0 for one-time play

## Example Implementation

```python
# bumble_scene.py
class BumbleScene(Scene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.music_file = "art/music/bumble/dating_vibes.mp3"
        # ... rest of init

# drive_scene.py
class DriveScene(Scene):
    def __init__(self, vehicle='car', duration=35.0, time_of_day='night', manager=None):
        super().__init__(manager)
        if time_of_day == 'night':
            self.music_file = "art/music/drive/night_drive.mp3"
        else:
            self.music_file = "art/music/drive/day_drive.mp3"
        # ... rest of init
```

## Current Scene Music Status

- [ ] Bumble Scene - Not yet added
- [ ] Drive Scene (Night) - Not yet added
- [ ] Apartment Scene - Not yet added
- [ ] Disney Scene - Not yet added
- [ ] Moving Scene (Day) - Not yet added
- [ ] Dinner Scene - Not yet added

## Next Steps

1. Find or create appropriate music tracks for each scene
2. Add music files to `art/music/[scene_name]/` folders
3. Update each scene's `__init__` to set `self.music_file`
4. Test volume levels and adjust as needed
5. Consider adding fade-in/fade-out transitions for smoother scene changes
