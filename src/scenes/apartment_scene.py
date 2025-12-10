import pygame
import math
import os
import random
from ..core.scene import Scene
from ..core.dialogue import DialogueBox
from ..core import assets
from ..utils.tilemap import load_apartment_tilemap, load_apartment_collision_map, load_apartment_object_rects
from ..utils.lpc_demo import AnimationManager, IDLE_SPEED, WALK_SPEED, Animation, SIT_SPEED

# Debug flag - set to True to enable debug output and see collision boxes
DEBUG = False


class ApartmentScene(Scene):
    """Shani's apartment scene - first date memory.
    
    Controls:
    - WASD or Arrow keys to move Maria
    - SPACE to interact with objects
    """
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.dialog = None
        
        # Maria character
        self.player_pos = [-100, 624]  # Start off-screen left, will move to door after delay (824 - 200 offset)
        self.player_speed = 200
        self.player_facing = 'right'
        
        # Shani character (standing by the table)
        self.shani_pos = [750, 400]  # Near the table with wine (600 - 200 offset)
        self.shani_facing = 'left'
        
        # Cutscene state
        self.cutscene_active = True
        self.cutscene_step = -1  # Start at -1 for initial delay
        self.cutscene_timer = 0
        self.cutscene_substep = 0  # Track which part of pathfinding we're on
        self.player_can_move = False
        self.space_key_cooldown = 0  # Cooldown for space key presses
        
        # Background image
        self.background = None
        self.background_scale = 4.0  # Scale 256x256 to 1024x1024 to fill screen width
        self.background_offset_y = -200  # Offset upward to cut off top and show more floor
        self.collision_rects = []
        
        # Animation managers
        self.maria_anim = None
        self.shani_anim = None
        self.maria_sitting_sprite = None  # Static sprite for sitting
        self.shani_sitting_sprite = None  # Static sprite for sitting
        
        # Interactable objects on the table (4 objects: wine bottle, 2 wine glasses, box)
        # These will be loaded from TMJ Object Layer 1 to match their collision boxes
        self.box_rect = None
        self.wine_glass1_rect = None
        self.wine_bottle_rect = None
        self.wine_glass2_rect = None
        self.interacting = False
        self.current_interaction = None  # Track which object is being interacted with
        
        # Interaction counters for wine glasses
        self.wine_glass1_interactions = 0
        self.wine_glass2_interactions = 0
        self.box_interactions = 0
        
        # Game interaction state
        self.game_interaction_active = False
        self.shani_sitting = False
        self.shani_target_pos = None
        self.shani_delay_timer = 0
        self.shani_can_move = False
        self.shani_game_substep = 0  # Track pathfinding substeps for game movement
        self.maria_sitting = False
        self.maria_target_pos = None
        
        # Game overlay (questions when both are sitting)
        self.show_game_overlay = False
        self.current_question = 0
        self.celebration_active = False
        self.celebration_timer = 0
        self.fireworks = []
        self.fade_out = False
        self.fade_alpha = 0
        self.questions = [
            {
                'question': "What color are Maria's eyes?",
                'option1': 'Bluish Green',
                'option2': 'Brown'
            },
            {
                'question': 'Is Shani a morning or night person?',
                'option1': 'Morning',
                'option2': 'Night'
            },
            {
                'question': 'Do you want to go on a second date?',
                'option1': 'Yes',
                'option2': 'No'
            }
        ]

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.dialog = DialogueBox(self.font, 760, 120)
        
        apartment_folder = os.path.join('art', 'scenes', 'apartment', 'apartment')
        try:
            # Load and scale background image (256x256 -> 1024x1024 to fill screen width, then offset)
            bg_path = os.path.join(apartment_folder, 'untitled.png')
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1024, 1024))
            
            # Load collision map from TMJ file
            self.collision_rects = load_apartment_collision_map(
                apartment_folder, 
                tile_size=16, 
                scale=self.background_scale
            )
            
            # Apply background offset to collision rects
            for rect in self.collision_rects:
                rect.y += self.background_offset_y
            
            # Load object collision boxes from TMJ Object Layer 1
            object_rects = load_apartment_object_rects(
                apartment_folder,
                tile_size=16,
                scale=self.background_scale
            )
            
            # Apply background offset to object rects
            for rect in object_rects:
                rect.y += self.background_offset_y
            
            # Sort objects by x-position (left to right) and assign to interaction boxes
            if len(object_rects) >= 4:
                sorted_objs = sorted(object_rects, key=lambda r: r.x)
                self.box_rect = sorted_objs[0]          # Leftmost
                self.wine_glass1_rect = sorted_objs[1]  # 2nd from left
                self.wine_bottle_rect = sorted_objs[2]  # 3rd from left
                self.wine_glass2_rect = sorted_objs[3]  # Rightmost
            
            # Add manual table collision (830 * 4.0 scale - 200 offset)
            table_y = int(830 * self.background_scale / 3.0) + self.background_offset_y
            table_x = int(320 * self.background_scale / 3.0)
            table_width = int(300 * self.background_scale / 3.0)
            self.collision_rects.append(pygame.Rect(table_x, table_y, table_width, 70))
            
            # Add boundary walls (account for background offset)
            wall_thickness = 10
            self.collision_rects.extend([
                pygame.Rect(0, self.background_offset_y, 1024, wall_thickness),  # Top
                pygame.Rect(0, 768 - wall_thickness, 1024, wall_thickness),  # Bottom
                pygame.Rect(0, self.background_offset_y, wall_thickness, 1024),  # Left
                pygame.Rect(1024 - wall_thickness, self.background_offset_y, wall_thickness, 1024)  # Right
            ])
            
        except Exception as e:
            print(f"Could not load apartment background: {e}")
            self.background = None
        
        # Setup Maria animations (facing right)
        self.maria_anim = self._setup_character('maria', ['idle_right', 'idle'])
        self.maria_sitting_sprite = self._load_sitting_sprite('maria')
        
        # Setup Shani animations (facing left)
        self.shani_anim = self._setup_character('shani', ['idle_left', 'idle'])
        self.shani_sitting_sprite = self._load_sitting_sprite('shani')
    
    def _setup_character(self, char_name, initial_anim_priority):
        """Load and setup a character's animation manager."""
        try:
            anims = assets.get_animations(char_name, size=(64, 64))
        except Exception as e:
            print(f"Could not load {char_name} animations: {e}")
            return None
        
        mgr = AnimationManager()
        
        # Add animations with appropriate speeds and filtering
        for name, frames in anims.items():
            if not frames:
                continue
            
            # Filter transparent frames from walk animations for smoother movement
            if 'walk' in name:
                visible_frames = []
                for frame in frames:
                    try:
                        mask = pygame.mask.from_surface(frame)
                        if mask.count() > 0:
                            visible_frames.append(frame)
                    except Exception:
                        visible_frames.append(frame)
                frames = visible_frames if visible_frames else frames
            
            # Determine animation speed
            speed = (IDLE_SPEED if 'idle' in name else
                    WALK_SPEED if 'walk' in name or 'run' in name else
                    SIT_SPEED if 'sit' in name else
                    100 if 'emote' in name else 150)
            
            loop = 'sit' not in name
            
            try:
                mgr.add(name, Animation(frames, speed_ms=speed, loop=loop))
            except Exception:
                pass
        
        # Start with first available animation from priority list
        for anim_name in initial_anim_priority:
            if anim_name in mgr.animations:
                mgr.play(anim_name)
                break
        
        return mgr
    
    def _load_sitting_sprite(self, char_name):
        """Load the first frame of the down-facing sitting animation as a static sprite."""
        try:
            sit_path = os.path.join('art', 'characters', char_name, 'sit.png')
            sit_sheet = pygame.image.load(sit_path).convert_alpha()
            # Extract first frame of row 2 (down-facing)
            # sit.png has 4 rows (up, left, down, right) with 4 frames each
            sprite = pygame.Surface((64, 64), pygame.SRCALPHA, 32)
            sprite.blit(sit_sheet, (0, 0), (0, 128, 64, 64))  # Row 2 (y=128) is down-facing
            return sprite
        except Exception as e:
            print(f"Could not load sitting sprite for {char_name}: {e}")
            return None

    def handle_event(self, event: pygame.event.EventType):
        # Handle game overlay clicks
        if event.type == pygame.MOUSEBUTTONDOWN and self.show_game_overlay:
            mx, my = event.pos
            w, h = pygame.display.get_surface().get_size()
            box = pygame.Rect((w - 520)//2, (h - 220)//2, 520, 220)
            option1_rect = pygame.Rect(box.x + 60, box.y + 140, 160, 48)
            option2_rect = pygame.Rect(box.x + 300, box.y + 140, 160, 48)
            
            if DEBUG:
                print(f"Click at ({mx}, {my}), current_question={self.current_question}/{len(self.questions)}")
                print(f"Option1 rect: {option1_rect}, Option2 rect: {option2_rect}")
            
            if option1_rect.collidepoint(mx, my):
                # Correct answer (option 1 is always correct)
                if DEBUG:
                    print(f"Clicked Option 1! Question {self.current_question}: {self.questions[self.current_question]['question']}")
                
                # Check if this is the last question (Do you want to go on a second date?)
                if self.current_question == len(self.questions) - 1:
                    if DEBUG:
                        print("LAST QUESTION! Triggering celebration!")
                    # Trigger celebration here
                    self.celebration_active = True
                    self.celebration_timer = 0
                    
                    # Create fireworks particles (300 particles - 10x more!)
                    for _ in range(300):
                        self.fireworks.append({
                            'x': random.randint(100, 900),
                            'y': random.randint(100, 700),
                            'vx': random.uniform(-200, 200),
                            'vy': random.uniform(-250, -50),
                            'color': random.choice([(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255), (100, 255, 255), (255, 150, 100)]),
                            'life': random.uniform(1.5, 3.0),
                            'max_life': random.uniform(1.5, 3.0)
                        })
                    
                    # Make Shani play emote animation
                    if self.shani_anim:
                        # Try emote animation first
                        if 'emote' in self.shani_anim.animations:
                            self.shani_anim.play('emote')
                        else:
                            # Fall back to idle
                            self.shani_anim.play('idle_left')
                    
                    if DEBUG:
                        print(f"celebration_active set to {self.celebration_active}, created {len(self.fireworks)} fireworks")
                
                self.current_question += 1
                if self.current_question >= len(self.questions):
                    # All questions answered - hide overlay
                    self.show_game_overlay = False
                    if DEBUG:
                        print("All questions answered, hiding overlay")
            elif option2_rect.collidepoint(mx, my):
                # Wrong answer - do nothing (or could show feedback)
                if DEBUG:
                    print(f"Clicked Option 2 (wrong answer)")
                pass
        
        if event.type == pygame.KEYDOWN:
            if DEBUG:
                print(f"KEYDOWN: {pygame.key.name(event.key)}, cutscene_active={self.cutscene_active}")
            if event.key == pygame.K_SPACE and not self.cutscene_active:
                # If dialogue is visible, advance it and don't check for new interactions
                if self.dialog.visible and self.interacting:
                    self.dialog.next()
                    if not self.dialog.visible:
                        self.interacting = False
                        self.current_interaction = None
                        # Start character movement after dialogue finishes
                        if self.game_interaction_active and DEBUG:
                            print(f"Dialogue finished! Starting character movement. maria_target={self.maria_target_pos}, shani_target={self.shani_target_pos}")
                    return
                
                # Don't allow object interactions while the game is active
                if self.show_game_overlay:
                    return
                
                # Check if near any table objects (expand interaction area vertically only)
                # Use inflated rect to check proximity - width 48px (Maria's width), expand vertically 60px
                maria_rect = pygame.Rect(self.player_pos[0] + 40, self.player_pos[1], 48, 128)
                maria_interact_rect = maria_rect.inflate(0, 120)  # No horizontal expansion, 60px vertical on each side
                
                if DEBUG:
                    print(f"Space pressed! Maria at {self.player_pos}, Interact rect: {maria_interact_rect}")
                    print(f"Box rect: {self.box_rect}, collision: {maria_interact_rect.colliderect(self.box_rect)}")
                    print(f"Wine bottle rect: {self.wine_bottle_rect}, collision: {maria_interact_rect.colliderect(self.wine_bottle_rect)}")
                    print(f"Glass1 rect: {self.wine_glass1_rect}, collision: {maria_interact_rect.colliderect(self.wine_glass1_rect)}")
                    print(f"Glass2 rect: {self.wine_glass2_rect}, collision: {maria_interact_rect.colliderect(self.wine_glass2_rect)}")
                
                # Check box FIRST (game on table) - leftmost object
                if maria_interact_rect.colliderect(self.box_rect):
                    # First interaction: just show the title
                    if self.box_interactions == 0:
                        self.box_interactions += 1
                        self.dialog.set_lines([
                            "Card Game: We are not really strangers"
                        ])
                        self.interacting = True
                        self.current_interaction = 'box'
                    # After seeing title, need to drink wine first
                    elif self.wine_glass1_interactions == 0 and self.wine_glass2_interactions == 0:
                        self.dialog.set_lines([
                            "Maybe I should try the wine first..."
                        ])
                        self.interacting = True
                        self.current_interaction = 'box'
                    # After drinking wine, clicking game again starts it
                    else:
                        # Trigger both Maria and Shani to sit at the table
                        if not self.game_interaction_active:
                            self.game_interaction_active = True
                            # Position Shani at specific chair location (right side)
                            # 700 - 200 offset = 500
                            self.shani_target_pos = [480, 500]
                            # Position Maria at her chair location (left side)
                            self.maria_target_pos = [350, 500]
                            if DEBUG:
                                print(f"Game interaction activated! Targets set: Maria={self.maria_target_pos}, Shani={self.shani_target_pos}")
                        
                        self.dialog.set_lines([
                            "Oh, a board game!",
                            "I wonder if Shani would like to play..."
                        ])
                        self.interacting = True
                        self.current_interaction = 'box'
                
                # Check wine bottle
                elif maria_interact_rect.colliderect(self.wine_bottle_rect):
                    if DEBUG:
                        print(f"Wine bottle collision detected! Maria interact rect: {maria_interact_rect}, Wine rect: {self.wine_bottle_rect}")
                    self.dialog.set_lines([
                        "I hope she likes Kosher wine"
                    ])
                    self.interacting = True
                    self.current_interaction = 'wine_bottle'
                
                # Check first wine glass
                elif maria_interact_rect.colliderect(self.wine_glass1_rect):
                    self.wine_glass1_interactions += 1
                    if self.wine_glass1_interactions == 1:
                        self.dialog.set_lines(["This is really good wine!"])
                    elif self.wine_glass1_interactions == 2:
                        self.dialog.set_lines(["Wow she is really pretty..."])
                    else:
                        self.dialog.set_lines(["Ok I should check out the game on the table"])
                    self.interacting = True
                    self.current_interaction = 'glass1'
                
                # Check second wine glass
                elif maria_interact_rect.colliderect(self.wine_glass2_rect):
                    self.wine_glass2_interactions += 1
                    if self.wine_glass2_interactions == 1:
                        self.dialog.set_lines(["This is really good wine!"])
                    elif self.wine_glass2_interactions == 2:
                        self.dialog.set_lines(["Wow she is really pretty..."])
                    else:
                        self.dialog.set_lines(["Ok I should check out the game on the table"])
                    self.interacting = True
                    self.current_interaction = 'glass2'

    def update(self, dt: float):
        # Handle intro cutscene
        if self.cutscene_active:
            if self.cutscene_step == -1:
                # Step -1: Initial 2 second delay (Maria off-screen)
                self.cutscene_timer += dt
                if self.cutscene_timer >= 2.0:
                    # Move Maria to door position
                    self.player_pos[0] = 45
                    self.cutscene_step = 0
            
            elif self.cutscene_step == 0:
                # Step 0: Maria walks right from door on left wall
                target_x = 145
                if self.player_pos[0] < target_x:
                    self.player_pos[0] += self.player_speed * dt
                    self.player_facing = 'right'
                    if self.maria_anim and self.maria_anim.current != 'walk_right':
                        self.maria_anim.play('walk_right')
                else:
                    self.player_pos[0] = target_x
                    self.cutscene_step = 1
                    if self.maria_anim:
                        self.maria_anim.play('idle_right')
            
            elif self.cutscene_step == 1:
                # Step 1: Shani walks towards Maria using substeps
                target_x = 230  # Right side of Maria (150 + 80 for spacing)
                target_y = 624  # 824 - 200 offset
                
                # Substep 0: Move left to target x
                if self.cutscene_substep == 0:
                    if self.shani_pos[0] > target_x:
                        self.shani_pos[0] -= self.player_speed * dt
                        self.shani_facing = 'left'
                        if self.shani_anim and self.shani_anim.current != 'walk_left':
                            self.shani_anim.play('walk_left')
                    else:
                        self.shani_pos[0] = target_x
                        self.cutscene_substep = 1
                
                # Substep 1: Move down to target y
                elif self.cutscene_substep == 1:
                    if abs(self.shani_pos[1] - target_y) > 2:
                        if self.shani_pos[1] < target_y:
                            self.shani_pos[1] += self.player_speed * dt
                            self.shani_facing = 'down'
                            anim_name = 'walk_down'
                        else:
                            self.shani_pos[1] -= self.player_speed * dt
                            self.shani_facing = 'up'
                            anim_name = 'walk_up'
                        if self.shani_anim and self.shani_anim.current != anim_name:
                            self.shani_anim.play(anim_name)
                    else:
                        self.shani_pos[1] = target_y
                        self.cutscene_substep = 2
                
                # Substep 2: Arrived at Maria
                if self.cutscene_substep == 2:
                    if DEBUG:
                        print(f"Shani reached Maria! pos={self.shani_pos[0]:.1f}, target={target_x}, diff={abs(self.shani_pos[0] - target_x):.1f}")
                    # Reached Maria
                    self.shani_pos[0] = target_x
                    self.shani_pos[1] = target_y
                    self.shani_facing = 'left'
                    if self.shani_anim:
                        self.shani_anim.play('idle_left')
                    # Show dialogue
                    self.dialog.set_lines([
                        "Thanks for coming over!",
                        "Wow, your pictures did not do you justice!",
                        "You are gorgeous!",
                        "Feel free to check out my apartment!"
                    ])
                    self.cutscene_step = 2
            
            elif self.cutscene_step == 2:
                # Step 2: Wait for dialogue to finish
                # Update cooldown
                if self.space_key_cooldown > 0:
                    self.space_key_cooldown -= dt
                
                # Check if dialogue is finished (no more lines)
                if not self.dialog.visible:
                    # Dialogue finished, end cutscene and let Maria move
                    if DEBUG:
                        print("Cutscene ending - Maria can now move!")
                    self.cutscene_active = False
                    self.player_can_move = True
                    self.shani_delay_timer = 3.0  # Start 3 second delay for Shani's movement
                    if self.maria_anim:
                        self.maria_anim.play('idle_right')
                
                # Only check space key if cooldown expired and dialogue still visible
                elif self.space_key_cooldown <= 0:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        self.dialog.next()
                        self.space_key_cooldown = 0.3  # 300ms cooldown between advances
        
        # Handle Maria movement (only when cutscene is not active)
        dx = 0
        dy = 0
        
        if self.player_can_move:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1
                self.player_facing = 'left'
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1
                self.player_facing = 'right'
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1
                self.player_facing = 'up'
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1
                self.player_facing = 'down'
        
        # Normalize diagonal movement
        is_moving = (dx != 0 or dy != 0)
        if is_moving:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            
            # Calculate new position
            new_x = self.player_pos[0] + dx * self.player_speed * dt
            new_y = self.player_pos[1] + dy * self.player_speed * dt
            
            # Collision detection using head area (48x40) like dinner scene
            # Character is 64x64 scaled 2x = 128x128, offset to center the 48-wide collision box
            maria_head_rect = pygame.Rect(new_x + 40, new_y, 48, 40)
            # Also check body collision with furniture (48x128)
            maria_body_rect = pygame.Rect(new_x + 40, new_y, 48, 128)
            
            # Check collision with Shani's head area
            shani_head_rect = pygame.Rect(self.shani_pos[0] + 40, self.shani_pos[1], 48, 40)
            
            collision = False
            if maria_body_rect.colliderect(shani_head_rect):
                collision = True
            else:
                for rect in self.collision_rects:
                    if maria_body_rect.colliderect(rect):
                        collision = True
                        break
            
            if not collision:
                self.player_pos[0] = new_x
                self.player_pos[1] = new_y
        
        # Handle delay timer for Shani's movement after intro dialogue
        if self.shani_delay_timer > 0:
            self.shani_delay_timer -= dt
            if self.shani_delay_timer <= 0:
                self.shani_can_move = True
                if DEBUG:
                    print("Shani can now move to game interaction!")
        
        # Handle Shani movement when game interaction is triggered (walk around table)
        if self.game_interaction_active and not self.shani_sitting and self.shani_can_move:
            if self.shani_target_pos:
                target_x, target_y = self.shani_target_pos
                speed = 180
                
                # Substep 0: Move up higher to avoid Maria (to y=350)
                if self.shani_game_substep == 0:
                    intermediate_y = 350
                    if self.shani_pos[1] > intermediate_y + 5:
                        self.shani_pos[1] -= speed * dt
                        facing = 'up'
                        
                        if self.shani_anim:
                            walk_anim = f'walk_{facing}'
                            if self.shani_anim.current != walk_anim:
                                self.shani_anim.play(walk_anim)
                    else:
                        self.shani_pos[1] = intermediate_y
                        self.shani_game_substep = 1
                
                # Substep 1: Move right to target x
                elif self.shani_game_substep == 1:
                    if abs(self.shani_pos[0] - target_x) > 5:
                        self.shani_pos[0] += speed * dt
                        facing = 'right'
                        
                        if self.shani_anim:
                            walk_anim = f'walk_{facing}'
                            if self.shani_anim.current != walk_anim:
                                self.shani_anim.play(walk_anim)
                    else:
                        self.shani_pos[0] = target_x
                        self.shani_game_substep = 2
                
                # Substep 2: Move down to final target y (chair position)
                elif self.shani_game_substep == 2:
                    if abs(self.shani_pos[1] - target_y) > 5:
                        self.shani_pos[1] += speed * dt
                        facing = 'down'
                        
                        if self.shani_anim:
                            walk_anim = f'walk_{facing}'
                            if self.shani_anim.current != walk_anim:
                                self.shani_anim.play(walk_anim)
                    else:
                        # Reached target, sit down
                        self.shani_pos[0] = target_x
                        self.shani_pos[1] = target_y
                        self.shani_sitting = True
                        if DEBUG:
                            print(f"Shani reached sitting position! shani_sitting={self.shani_sitting}, maria_sitting={self.maria_sitting}")
                        if self.shani_anim:
                            # Try to play sit animation, fall back to idle if not available
                            if 'sit_down' in self.shani_anim.animations:
                                self.shani_anim.play('sit_down')
                            elif 'sit' in self.shani_anim.animations:
                                self.shani_anim.play('sit')
                            else:
                                self.shani_anim.play('idle_left')
        
        # Handle Maria movement when game interaction is triggered
        if self.game_interaction_active and not self.maria_sitting and self.maria_target_pos:
            target_x, target_y = self.maria_target_pos
            dx = target_x - self.player_pos[0]
            dy = target_y - self.player_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 5:
                # Move Maria toward target
                nx = dx / distance
                ny = dy / distance
                speed = 180
                self.player_pos[0] += nx * speed * dt
                self.player_pos[1] += ny * speed * dt
                
                # Determine facing direction
                if abs(dx) > abs(dy):
                    self.player_facing = 'left' if dx < 0 else 'right'
                else:
                    self.player_facing = 'up' if dy < 0 else 'down'
                
                # Play walk animation
                if self.maria_anim:
                    walk_anim = f'walk_{self.player_facing}'
                    if self.maria_anim.current != walk_anim:
                        self.maria_anim.play(walk_anim)
            else:
                # Reached target, sit down
                self.player_pos[0] = target_x
                self.player_pos[1] = target_y
                self.maria_sitting = True
                if DEBUG:
                    print(f"Maria reached sitting position! maria_sitting={self.maria_sitting}, shani_sitting={self.shani_sitting}")
                if self.maria_anim:
                    # Try to play sit animation, fall back to idle
                    if 'sit_down' in self.maria_anim.animations:
                        self.maria_anim.play('sit_down')
                    elif 'sit' in self.maria_anim.animations:
                        self.maria_anim.play('sit')
                    else:
                        self.maria_anim.play('idle_right')
                
        
        # Check if both are sitting - show game overlay (outside movement blocks)
        if self.game_interaction_active and self.shani_sitting and self.maria_sitting and not self.show_game_overlay:
            self.show_game_overlay = True
            # Hide dialogue when game starts
            self.dialog.visible = False
            self.interacting = False
            if DEBUG:
                print(f"Both sitting! Showing game overlay. shani_sitting={self.shani_sitting}, maria_sitting={self.maria_sitting}")
        
        # Update Maria animation
        if self.maria_anim and not self.maria_sitting:
            anim_key = f"{'walk' if is_moving else 'idle'}_{self.player_facing}"
            if self.maria_anim.current != anim_key:
                self.maria_anim.play(anim_key)
            self.maria_anim.update(dt * 1000)  # Convert seconds to milliseconds
        
        # Update Shani animation
        if self.shani_anim:
            self.shani_anim.update(dt * 1000)  # Convert seconds to milliseconds
        
        # Update celebration and fireworks
        if self.celebration_active:
            if DEBUG and self.celebration_timer == 0:
                print(f"Celebration active! Firework count: {len(self.fireworks)}")
            self.celebration_timer += dt
            # Update firework particles
            for particle in self.fireworks[:]:
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                particle['vy'] += 200 * dt  # Gravity
                particle['life'] -= dt
                if particle['life'] <= 0:
                    self.fireworks.remove(particle)
            
            # After 3 seconds of celebration, start fade out
            if self.celebration_timer >= 3.0 and not self.fade_out:
                self.fade_out = True
                if DEBUG:
                    print("Starting fade out to next scene")
        
        # Handle fade out
        if self.fade_out:
            self.fade_alpha += dt * 150  # Fade over ~1.7 seconds
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # Transition to transition scene with message
                if self.manager:
                    from .transition_scene import TransitionScene
                    from .disney_scene import DisneyScene
                    message = "After their first date Shani and Maria went out on many more dates..."
                    self.manager.go_to(TransitionScene(message, DisneyScene, self.manager, duration=5.0))

    def draw(self, surface: pygame.Surface):
        surface.fill((20, 20, 30))
        
        # Draw background image if available
        if self.background:
            surface.blit(self.background, (0, self.background_offset_y))
        else:
            # Fallback if image didn't load
            surface.fill((60, 50, 70))
        
        # Draw Shani
        if self.shani_sitting and self.shani_sitting_sprite:
            # Use static sitting sprite
            scaled = pygame.transform.scale(self.shani_sitting_sprite, (128, 128))
            surface.blit(scaled, (self.shani_pos[0], self.shani_pos[1]))
        elif self.shani_anim:
            self.shani_anim.draw(surface, self.shani_pos[0], self.shani_pos[1], scale=2.0)
        
        # Redraw wine glass on top of Shani when she's sitting (to fix layering)
        if self.shani_sitting and self.background:
            # Extract and redraw the wine glass region from background
            # Need to get the rect position relative to the background (without offset)
            glass_rect = self.wine_glass2_rect
            if glass_rect:
                # The glass rect has already been offset, so subtract it to get background coordinates
                bg_rect = pygame.Rect(glass_rect.x, glass_rect.y - self.background_offset_y, 
                                     glass_rect.width, glass_rect.height)
                glass_subsurface = self.background.subsurface(bg_rect)
                # Blit at the screen position (which includes the offset)
                surface.blit(glass_subsurface, (glass_rect.x, glass_rect.y))
        
        # Draw Maria
        if self.maria_sitting and self.maria_sitting_sprite:
            # Use static sitting sprite
            scaled = pygame.transform.scale(self.maria_sitting_sprite, (128, 128))
            surface.blit(scaled, (int(self.player_pos[0]), int(self.player_pos[1])))
        elif self.maria_anim:
            self.maria_anim.draw(surface, int(self.player_pos[0]), int(self.player_pos[1]), scale=2.0)
        
        # Redraw wine glass on top of Maria when she's sitting (to fix layering)
        if self.maria_sitting and self.background:
            glass_rect = self.wine_glass1_rect
            if glass_rect:
                # The glass rect has already been offset, so subtract it to get background coordinates
                bg_rect = pygame.Rect(glass_rect.x, glass_rect.y - self.background_offset_y,
                                     glass_rect.width, glass_rect.height)
                glass_subsurface = self.background.subsurface(bg_rect)
                # Blit at the screen position (which includes the offset)
                surface.blit(glass_subsurface, (glass_rect.x, glass_rect.y))
        
        # Debug: draw collision boxes
        if DEBUG:
            for rect in self.collision_rects:
                pygame.draw.rect(surface, (255, 0, 0), rect, 2)
            # Draw all 4 interactable object zones in green
            pygame.draw.rect(surface, (0, 255, 0), self.wine_bottle_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.wine_glass1_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.wine_glass2_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.box_rect, 2)
            
            # Draw Maria's interaction area (inflated rect) in yellow
            maria_rect = pygame.Rect(int(self.player_pos[0]) + 40, int(self.player_pos[1]), 48, 128)
            maria_interact_rect = maria_rect.inflate(0, 120)  # Same as in handle_event
            pygame.draw.rect(surface, (255, 255, 0), maria_interact_rect, 2)
            
            # Draw Maria's collision box (head area: 48x40)
            # Character is 64x64 scaled 2x = 128x128, offset to center the 48-wide collision box
            maria_rect = pygame.Rect(int(self.player_pos[0]) + 40, int(self.player_pos[1]), 48, 40)
            pygame.draw.rect(surface, (0, 255, 255), maria_rect, 2)  # Cyan for Maria
            
            # Draw Shani's collision box (head area: 48x40)
            shani_rect = pygame.Rect(self.shani_pos[0] + 40, self.shani_pos[1], 48, 40)
            pygame.draw.rect(surface, (255, 255, 0), shani_rect, 2)  # Yellow for Shani
        
        # Draw dialog
        if self.dialog and (self.interacting or self.cutscene_step == 2):
            w, h = surface.get_size()
            self.dialog.draw(surface, (w - 760) // 2, (h - 120) // 2)
        
        # Draw game overlay (questions)
        if self.show_game_overlay and self.current_question < len(self.questions):
            w, h = surface.get_size()
            box = pygame.Rect((w - 520)//2, (h - 220)//2, 520, 220)
            
            # Red background
            pygame.draw.rect(surface, (180, 40, 40), box)
            
            # Dark border
            pygame.draw.rect(surface, (80, 20, 20), box, 4)
            
            # Get current question
            current_q = self.questions[self.current_question]
            title = self.font.render(current_q['question'], True, (255, 240, 230))
            surface.blit(title, (box.x + (box.w - title.get_width())//2, box.y + 24))

            # Option 1 button (always correct answer) - white background with red text
            option1_rect = pygame.Rect(box.x + 60, box.y + 140, 160, 48)
            pygame.draw.rect(surface, (255, 255, 255), option1_rect)
            pygame.draw.rect(surface, (80, 20, 20), option1_rect, 2)
            opt1txt = self.font.render(current_q['option1'], True, (180, 40, 40))
            surface.blit(opt1txt, (option1_rect.x + (option1_rect.w - opt1txt.get_width())//2, option1_rect.y + 12))

            # Option 2 button - white background with red text
            option2_rect = pygame.Rect(box.x + 300, box.y + 140, 160, 48)
            pygame.draw.rect(surface, (255, 255, 255), option2_rect)
            pygame.draw.rect(surface, (80, 20, 20), option2_rect, 2)
            opt2txt = self.font.render(current_q['option2'], True, (180, 40, 40))
            surface.blit(opt2txt, (option2_rect.x + (option2_rect.w - opt2txt.get_width())//2, option2_rect.y + 12))
        
        # Draw fireworks particles
        if self.celebration_active:
            for particle in self.fireworks:
                # Calculate alpha based on remaining life
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    # Draw particle as a small circle with RGB color
                    particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                    particle_surface.set_alpha(alpha)
                    pygame.draw.circle(particle_surface, particle['color'], (4, 4), 4)
                    surface.blit(particle_surface, (int(particle['x']), int(particle['y'])))
        
        # Draw fade out overlay
        if self.fade_out and self.fade_alpha > 0:
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surface, (0, 0))
