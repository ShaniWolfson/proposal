import pygame
import math
import os
from scene import Scene
from dialogue import DialogueBox
import assets
from tilemap import load_apartment_tilemap, load_apartment_collision_map, load_apartment_object_rects
from lpc_demo import AnimationManager, IDLE_SPEED, WALK_SPEED

# Debug flag - set to True to enable debug output and see collision boxes
DEBUG = True


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
        self.player_pos = [-100, 824]  # Start off-screen left, will move to door after delay
        self.player_speed = 200
        self.player_facing = 'right'
        
        # Shani character (standing by the table)
        self.shani_pos = [750, 600]  # Near the table with wine
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
        self.background_scale = 4.0  # Scale 256x256 to 1024x1024
        self.collision_rects = []
        
        # Animation managers
        self.maria_anim = None
        self.shani_anim = None
        
        # Interactable objects on the table (4 objects: wine bottle, 2 wine glasses, box)
        # These will be loaded from TMJ Object Layer 1 to match their collision boxes
        self.box_rect = None
        self.wine_glass1_rect = None
        self.wine_bottle_rect = None
        self.wine_glass2_rect = None
        self.interacting = False
        self.current_interaction = None  # Track which object is being interacted with

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.dialog = DialogueBox(self.font, 760, 120)
        
        apartment_folder = os.path.join('art', 'backgrounds', 'apartment')
        try:
            # Load and scale background image (256x256 -> 1024x1024)
            bg_path = os.path.join(apartment_folder, 'untitled.png')
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1024, 1024))
            
            # Load collision map from TMJ file
            self.collision_rects = load_apartment_collision_map(
                apartment_folder, 
                tile_size=16, 
                scale=self.background_scale
            )
            
            # Load object collision boxes from TMJ Object Layer 1
            object_rects = load_apartment_object_rects(
                apartment_folder,
                tile_size=16,
                scale=self.background_scale
            )
            
            # Sort objects by x-position (left to right) and assign to interaction boxes
            if len(object_rects) >= 4:
                sorted_objs = sorted(object_rects, key=lambda r: r.x)
                self.box_rect = sorted_objs[0]          # Leftmost
                self.wine_glass1_rect = sorted_objs[1]  # 2nd from left
                self.wine_bottle_rect = sorted_objs[2]  # 3rd from left
                self.wine_glass2_rect = sorted_objs[3]  # Rightmost
            
            # Add manual table collision
            self.collision_rects.append(pygame.Rect(320, 830, 300, 70))
            
            # Add boundary walls
            wall_thickness = 10
            self.collision_rects.extend([
                pygame.Rect(0, 0, 1024, wall_thickness),  # Top
                pygame.Rect(0, 1014, 1024, wall_thickness),  # Bottom
                pygame.Rect(35, 0, wall_thickness, 1024),  # Left (offset to avoid black area)
                pygame.Rect(1014, 0, wall_thickness, 1024)  # Right
            ])
            
        except Exception as e:
            print(f"Could not load apartment background: {e}")
            self.background = None
        
        # Setup Maria animations (facing right)
        self.maria_anim = self._setup_character('maria', ['idle_right', 'idle'])
        
        # Setup Shani animations (facing left)
        self.shani_anim = self._setup_character('shani', ['idle_left', 'idle'])
    
    def _setup_character(self, char_name, initial_anim_priority):
        """Load and setup a character's animation manager."""
        from lpc_demo import Animation, SIT_SPEED
        
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

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.cutscene_active:
                # Check if near any table objects
                maria_rect = pygame.Rect(self.player_pos[0] + 40, self.player_pos[1], 48, 20)
                
                # Check wine bottle
                if maria_rect.colliderect(self.wine_bottle_rect):
                    if not self.interacting:
                        self.dialog.set_lines([
                            "The wine bottle from our first date.",
                            "Kosher wine - who knew it could taste so good?",
                            "That night changed everything."
                        ])
                        self.interacting = True
                        self.current_interaction = 'wine_bottle'
                    else:
                        if self.dialog.visible:
                            self.dialog.next()
                        else:
                            self.interacting = False
                            self.current_interaction = None
                
                # Check first wine glass
                elif maria_rect.colliderect(self.wine_glass1_rect):
                    if not self.interacting:
                        self.dialog.set_lines([
                            "Your glass from that evening.",
                            "I remember how nervous I was.",
                            "But everything felt so natural with you."
                        ])
                        self.interacting = True
                        self.current_interaction = 'glass1'
                    else:
                        if self.dialog.visible:
                            self.dialog.next()
                        else:
                            self.interacting = False
                            self.current_interaction = None
                
                # Check second wine glass
                elif maria_rect.colliderect(self.wine_glass2_rect):
                    if not self.interacting:
                        self.dialog.set_lines([
                            "My glass...",
                            "I couldn't stop staring at you.",
                            "You were so beautiful in the candlelight."
                        ])
                        self.interacting = True
                        self.current_interaction = 'glass2'
                    else:
                        if self.dialog.visible:
                            self.dialog.next()
                        else:
                            self.interacting = False
                            self.current_interaction = None
                
                # Check box
                elif maria_rect.colliderect(self.box_rect):
                    if not self.interacting:
                        self.dialog.set_lines([
                            "The chocolates you brought.",
                            "Dark chocolate - my favorite.",
                            "You remembered from our first conversation."
                        ])
                        self.interacting = True
                        self.current_interaction = 'box'
                    else:
                        if self.dialog.visible:
                            self.dialog.next()
                        else:
                            self.interacting = False
                            self.current_interaction = None

    def update(self, dt: float):
        # Handle intro cutscene
        if self.cutscene_active:
            if self.cutscene_step == -1:
                # Step -1: Initial 3 second delay (Maria off-screen)
                self.cutscene_timer += dt
                if self.cutscene_timer >= 3.0:
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
                target_y = 824
                
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
                
                # Only check space key if cooldown expired
                if self.space_key_cooldown <= 0:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        if self.dialog.visible:
                            self.dialog.next()
                            self.space_key_cooldown = 0.3  # 300ms cooldown between advances
                        else:
                            # Dialogue finished, end cutscene
                            self.cutscene_active = False
                            self.player_can_move = True
        
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
        
        # Update Maria animation
        if self.maria_anim:
            anim_key = f"{'walk' if is_moving else 'idle'}_{self.player_facing}"
            if self.maria_anim.current != anim_key:
                self.maria_anim.play(anim_key)
            self.maria_anim.update(dt * 1000)  # Convert seconds to milliseconds
        
        # Update Shani animation
        if self.shani_anim:
            self.shani_anim.update(dt * 1000)  # Convert seconds to milliseconds

    def draw(self, surface: pygame.Surface):
        surface.fill((20, 20, 30))
        
        # Draw background image if available
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            # Fallback if image didn't load
            surface.fill((60, 50, 70))
        
        # Draw Shani
        if self.shani_anim:
            self.shani_anim.draw(surface, self.shani_pos[0], self.shani_pos[1], scale=2.0)
        
        # Draw Maria
        if self.maria_anim:
            self.maria_anim.draw(surface, int(self.player_pos[0]), int(self.player_pos[1]), scale=2.0)
        
        # Debug: draw collision boxes
        if DEBUG:
            for rect in self.collision_rects:
                pygame.draw.rect(surface, (255, 0, 0), rect, 2)
            # Draw all 4 interactable object zones in green
            pygame.draw.rect(surface, (0, 255, 0), self.wine_bottle_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.wine_glass1_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.wine_glass2_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), self.box_rect, 2)
            
            # Draw Maria's collision box (head area: 48x40)
            # Character is 64x64 scaled 2x = 128x128, offset to center the 48-wide collision box
            maria_rect = pygame.Rect(int(self.player_pos[0]) + 40, int(self.player_pos[1]), 48, 40)
            pygame.draw.rect(surface, (0, 255, 255), maria_rect, 2)  # Cyan for Maria
            
            # Draw Shani's collision box (head area: 48x40)
            shani_rect = pygame.Rect(self.shani_pos[0] + 40, self.shani_pos[1], 48, 40)
            pygame.draw.rect(surface, (255, 255, 0), shani_rect, 2)  # Yellow for Shani
        
        # Draw title
        title = self.font.render("First Date — Your UWS Apartment", True, (240, 240, 240))
        surface.blit(title, (20, 20))
        
        # Draw dialog
        if self.dialog and (self.interacting or self.cutscene_step == 2):
            w, h = surface.get_size()
            self.dialog.draw(surface, (w - 760) // 2, (h - 120) // 2)
