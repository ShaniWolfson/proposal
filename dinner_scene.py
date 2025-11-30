import pygame
import math
import os
from scene import Scene
from dialogue import DialogueBox
import assets
from tilemap import load_dinner_tilemap, load_collision_map

# Debug flag - set to True to enable debug output and see collision boxes
DEBUG = True


class DinnerScene(Scene):
    """Italian family dinner scene with manual Player 2 (Shani) entrance and proposal flow.

    Controls:
    - Number keys 1-6 to talk to family/friends
    - SPACE to advance dialogues
    - P to trigger Player 2 entrance (manual)
    - Mouse click YES on proposal overlay to accept
    """
    
    # NPC positions for drawing and collision detection
    NPC_POSITIONS = [
        (200, 580),   # Mom - left side
        (280, 580),   # Dad - next to Mom
        (850, 580),   # Gio - right side
        (450, 590),   # Loriana - bottom left
        (550, 590),   # Oresti - bottom left
        (730, 640),   # Marisa - bottom right
    ]

    def __init__(self, manager=None):
        super().__init__(manager)
        self.font = None
        self.dialog = None
        # NPC positions (for display only)
        self.npcs = [
            ("Mom", "Wow this is nice! I love you egg"),
            ("Dad", "Aye where's Uncle Ralph? I am happy for you sweetie"),
            ("Gio", "MARIA! MAURICE! WOW! THIS IS AMAZING! This might be almost as good as dancing with the stars"),
            ("Loriana", "This was nonconsentual. Shani just added me to this game without asking. But since I am here, I am happy for you Maria"),
            ("Oresti", "Oh so you can play a video game but you can't play DND? Just kiddingyou did well kiddo"),
            ("Marisa", "I can't believe I'm in a video game! Maria, you look amazing like this!"),
        ]
        self.player_pos = (512, 780)  # Maria starting position - bottom center, slightly higher
        self.last_npc_collision = None  # Track last NPC collision for dialogue closing

        # Player 2 (Shani) state
        self.p2_active = False
        self.p2_x = 1280.0 + 40.0  # Use float for smoother movement
        self.p2_y = 420.0
        self.p2_speed = 180
        self.p2_stage = 0
        self.p2_dialog_lines = [
            "Hey I have something for you",
            "Oh shoot, where is it!? ",
            "....Shani do you have it?",
        ]

        # proposal overlay with questions
        self.proposal_active = False
        self.show_proposal = False
        self.fireworks = []
        self.firework_timer = 0.0
        self.fireworks_running = False
        # after fireworks, show a short "That went well" message
        self.post_message_shown = False
        self.post_message_timer = 0.0
        
        # Only the marriage proposal question (no warm-up questions)
        self.current_question = 0
        self.questions = [
            {
                'question': 'Maria, will you marry me?',
                'option1': 'YES',
                'option2': 'NO'
            }
        ]
        
        # Emote system
        self.npc_emotes = []  # List of active emote states (npc_index, start_time)
        self.emote_duration = 3.0  # Play emote animation for 3 seconds


    def _setup_character(self, char_name, initial_anim_priority=None):
        """Load and setup a character's animation manager.
        
        Args:
            char_name: Name of character (e.g., 'maria', 'shani', 'gio')
            initial_anim_priority: List of animation names to try, in priority order
                                   (e.g., ['walk_left', 'idle_left', 'idle'])
        
        Returns:
            AnimationManager instance or None
        """
        try:
            from lpc_demo import Animation, AnimationManager, IDLE_SPEED, WALK_SPEED, SIT_SPEED
        except Exception:
            return None
        
        try:
            anims = assets.get_animations(char_name, size=(48, 64))
            if not anims:
                return None
        except Exception:
            return None
        
        mgr = AnimationManager()
        
        # Add all animations with appropriate settings
        for name, frames in anims.items():
            if not frames:
                continue
            
            # For walk animations, filter out transparent/empty frames for smoother looping
            if 'walk' in name:
                visible_frames = []
                for frame in frames:
                    try:
                        mask = pygame.mask.from_surface(frame)
                        if mask.count() > 0:  # Frame has visible pixels
                            visible_frames.append(frame)
                    except Exception:
                        visible_frames.append(frame)  # Keep frame if mask fails
                if visible_frames:
                    frames = visible_frames
            
            # Detect speed from animation name
            if 'idle' in name:
                speed = IDLE_SPEED
            elif 'walk' in name or 'run' in name:
                speed = WALK_SPEED
            elif 'sit' in name:
                speed = SIT_SPEED
            elif 'emote' in name:
                speed = 100  # Emote animations play faster
            else:
                speed = 150
            
            loop = 'sit' not in name  # Only sit animations don't loop
            
            try:
                mgr.add(name, Animation(frames, speed_ms=speed, loop=loop))
            except Exception:
                pass
        
        # Start with preferred animation
        if initial_anim_priority:
            for anim_name in initial_anim_priority:
                if anim_name in mgr.animations:
                    mgr.play(anim_name)
                    break
        elif mgr.animations:
            # Default to first animation
            first = next(iter(mgr.animations.keys()))
            mgr.play(first)
        
        return mgr

    def _find_best_anim_key(self, mgr, base, facing):
        """Find best matching animation key for given base and facing direction."""
        try:
            keys = list(mgr.animations.keys())
        except Exception:
            return None
        
        exact = f"{base}_{facing}"
        if exact in keys:
            return exact
        
        # Prefer keys that end with the facing and include the base
        candidates = [k for k in keys if k.endswith(f"_{facing}") and base in k]
        if candidates:
            return candidates[0]
        
        # Any key that ends with the facing
        candidates = [k for k in keys if k.endswith(f"_{facing}")]
        if candidates:
            return candidates[0]
        
        # Any key that contains the base
        candidates = [k for k in keys if base in k]
        if candidates:
            return candidates[0]
        
        if base in keys:
            return base
        
        # Try idle variants
        if f"idle_{facing}" in keys:
            return f"idle_{facing}"
        if 'idle' in keys:
            return 'idle'
        
        # Fallback to first available animation
        return keys[0] if keys else None

    def _update_character_animation(self, anim_mgr, facing, is_moving):
        """Update character animation based on movement state and facing direction."""
        if not anim_mgr:
            return
        
        base = 'walk' if is_moving else 'idle'
        chosen = self._find_best_anim_key(anim_mgr, base, facing)
        
        if chosen:
            try:
                if is_moving:
                    anim_mgr.play(chosen)
                else:
                    anim_mgr.hold_last(chosen)
            except Exception:
                pass
    
    def _update_npc_facing(self, maria_x, maria_y):
        """Make all NPCs with sprites face toward Maria's position (unless they're emoting)."""
        for npc_index, npc_anim_mgr in self.npc_sprites.items():
            if not npc_anim_mgr:
                continue
            
            # Skip NPCs that are currently emoting
            if any(idx == npc_index for idx, _ in self.npc_emotes):
                continue
                
            npc_x, npc_y = self.NPC_POSITIONS[npc_index]
            dx = maria_x - npc_x
            dy = maria_y - npc_y
            
            # Determine which direction Maria is relative to NPC (never face up/backward)
            if abs(dx) > abs(dy):
                npc_facing = 'right' if dx > 0 else 'left'
            else:
                # If Maria is above NPC, face left/right instead of up
                if dy < 0:
                    # Maria is above - face left or right based on horizontal position
                    npc_facing = 'right' if dx > 0 else 'left'
                else:
                    # Maria is below - face down
                    npc_facing = 'down'
            
            # Find and set the appropriate idle animation facing Maria
            anim_key = self._find_best_anim_key(npc_anim_mgr, 'idle', npc_facing)
            if anim_key and npc_anim_mgr.current != anim_key:
                try:
                    npc_anim_mgr.hold_last(anim_key)
                except Exception:
                    pass

    def start(self):
        self.font = pygame.font.SysFont(None, 28)
        self.dialog = DialogueBox(self.font, 760, 120)
        
        # Load tilemap background
        try:
            dinner_folder = os.path.join('art', 'backgrounds', 'dinner')
            self.tilemap_layers = load_dinner_tilemap(dinner_folder)
            # Game is now 1024x1024, tilemap is 16x16 tiles at 16px
            # Scale: 1024 / 256 = 4x (16px tiles → 64px display tiles)
            self.tilemap_scale = 4.0
            
            # Load collision map
            collision_file = os.path.join(dinner_folder, 'data', 'collisions.js')
            self.collision_rects = load_collision_map(collision_file, tile_size=16, scale=self.tilemap_scale)
        except Exception as e:
            print(f"Could not load tilemap: {e}")
            self.tilemap_layers = []
            self.collision_rects = []
        
        # Setup character animations
        self.maria_anim_mgr = self._setup_character('maria', ['idle', 'idle_down'])
        self.shani_anim_mgr = self._setup_character('shani', ['walk_left', 'walk', 'idle_left', 'idle'])
        self.mom_anim_mgr = self._setup_character('mom', ['idle_down', 'idle'])
        self.dad_anim_mgr = self._setup_character('dad', ['idle_down', 'idle'])
        self.gio_anim_mgr = self._setup_character('gio', ['idle_down', 'idle'])
        self.loriana_anim_mgr = self._setup_character('loriana', ['idle_down', 'idle'])
        self.oresti_anim_mgr = self._setup_character('oresti', ['idle_down', 'idle'])
        self.marisa_anim_mgr = self._setup_character('marisa', ['idle_down', 'idle'])
        
        # Character sprite registry: maps NPC index to animation manager
        self.npc_sprites = {
            0: self.mom_anim_mgr,  # Mom at position index 0
            1: self.dad_anim_mgr,  # Dad at position index 1
            2: self.gio_anim_mgr,  # Gio at position index 2
            3: self.loriana_anim_mgr,  # Loriana at position index 3
            4: self.oresti_anim_mgr,  # Oresti at position index 4
            5: self.marisa_anim_mgr,  # Marisa at position index 5
        }
        


    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not self.p2_active:
                # Trigger proposal sequence - set meeting position
                self.p2_active = True
                self.p2_stage = 0
                self.meeting_pos = (512, 750)
                self.maria_at_meeting = False
                self.shani_at_meeting = False
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.dialog.next()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_proposal and self.proposal_active:
                mx, my = event.pos
                box, option1_rect, option2_rect = self._get_proposal_rects()
                if option1_rect.collidepoint(mx, my):
                    # Marriage proposal accepted!
                    self._start_fireworks()
                elif option2_rect.collidepoint(mx, my):
                    # NO is not clickable — ignore
                    pass

    def _start_fireworks(self):
        self.fireworks = []
        for i in range(12):
            self.fireworks.append({
                'x': 100 + (i * 80) % 1200,
                'y': 120 + (i % 4) * 40,
                't': 0.0,
                'color': (255, 200 - (i%3)*40, 80 + (i%4)*30)
            })
        self.fireworks_running = True
        self.firework_timer = 6.0

    def update(self, dt: float):
        # Allow moving Maria with arrow keys/WASD for testing
        try:
            keys = pygame.key.get_pressed()
            old_mx, old_my = self.player_pos
            mx, my = old_mx, old_my
            speed = 200
            moving = False
            # determine direction; prefer horizontal over vertical if both pressed
            dirx = 0
            diry = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                mx -= int(speed * dt)
                moving = True
                dirx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                mx += int(speed * dt)
                moving = True
                dirx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                my -= int(speed * dt)
                moving = True
                diry = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                my += int(speed * dt)
                moving = True
                diry = 1
            
            # Check collision and revert if needed
            collision_result = self._check_collision(mx, my)
            if collision_result:
                mx, my = old_mx, old_my
                # If collision is with NPC, trigger their dialogue (only if not already showing)
                if isinstance(collision_result, tuple) and collision_result[0] == 'npc':
                    npc_index = collision_result[1]
                    
                    # Show dialogue if not already visible
                    if npc_index < len(self.npcs) and not self.dialog.visible:
                        name, dialogue = self.npcs[npc_index]
                        if dialogue:  # Only show dialogue if there is one
                            self.dialog.set_lines([f"{name}: {dialogue}"])
                    
                    # Track that we're colliding with this NPC
                    self.last_npc_collision = npc_index
            else:
                # No collision - close dialogue if it was from an NPC collision
                if hasattr(self, 'last_npc_collision') and self.last_npc_collision is not None:
                    if self.dialog.visible:
                        self.dialog.visible = False
                    self.last_npc_collision = None
            
            # choose facing direction — prefer vertical (up/down) over horizontal like lpc_demo
            if diry < 0:
                facing = 'up'
            elif diry > 0:
                facing = 'down'
            elif dirx < 0:
                facing = 'left'
            elif dirx > 0:
                facing = 'right'
            else:
                facing = getattr(self, 'maria_facing', 'down')
            self.maria_facing = facing
            self.player_pos = (mx, my)
            # Update Maria's animation
            self._update_character_animation(self.maria_anim_mgr, self.maria_facing, moving)
            
            # Make all NPCs with sprites face Maria continuously
            self._update_npc_facing(mx, my)
        except Exception:
            pass
        if self.p2_active and not self.show_proposal:
            if self.p2_stage == 0:
                # Move both Maria and Shani to meeting position
                meeting_x, meeting_y = self.meeting_pos
                
                # Move Maria to meeting position (left side)
                if not self.maria_at_meeting:
                    maria_target_x = meeting_x - 30
                    maria_target_y = meeting_y
                    mx, my = self.player_pos
                    
                    dx = maria_target_x - mx
                    dy = maria_target_y - my
                    distance = math.hypot(dx, dy)
                    
                    if distance > 5:
                        # Maria still moving
                        nx = dx / distance if distance > 0 else 0
                        ny = dy / distance if distance > 0 else 0
                        speed = 150  # Maria's walking speed
                        mx += nx * speed * dt
                        my += ny * speed * dt
                        self.player_pos = (mx, my)
                        
                        # Determine Maria's facing
                        if abs(dx) > abs(dy):
                            facing = 'left' if dx < 0 else 'right'
                        else:
                            facing = 'up' if dy < 0 else 'down'
                        self.maria_facing = facing
                        self._update_character_animation(self.maria_anim_mgr, facing, is_moving=True)
                    else:
                        self.maria_at_meeting = True
                        self.maria_facing = 'right'
                        self._update_character_animation(self.maria_anim_mgr, 'right', is_moving=False)
                
                # Move Shani to meeting position (right side)
                if not self.shani_at_meeting:
                    shani_target_x = meeting_x + 30
                    shani_target_y = meeting_y
                    
                    dx = shani_target_x - self.p2_x
                    dy = shani_target_y - self.p2_y
                    distance = math.hypot(dx, dy)
                    
                    if distance > 5:
                        # Shani still moving
                        nx = dx / distance if distance > 0 else 0
                        ny = dy / distance if distance > 0 else 0
                        self.p2_x += nx * self.p2_speed * dt
                        self.p2_y += ny * self.p2_speed * dt
                        
                        # Determine Shani's facing
                        if abs(dx) > abs(dy):
                            facing = 'left' if dx < 0 else 'right'
                        else:
                            facing = 'up' if dy < 0 else 'down'
                        self._update_character_animation(self.shani_anim_mgr, facing, is_moving=True)
                    else:
                        self.shani_at_meeting = True
                        self._update_character_animation(self.shani_anim_mgr, 'left', is_moving=False)
                
                # Both reached meeting position
                if self.maria_at_meeting and self.shani_at_meeting:
                    self.p2_stage = 1
                    self.dialog.set_lines([self.p2_dialog_lines[0]])
                    
                    # Trigger emote animations for all NPCs
                    import time
                    current_time = time.time()
                    for npc_idx in range(len(self.npcs)):
                        self.npc_emotes.append((npc_idx, current_time))
                        if npc_idx in self.npc_sprites:
                            npc_mgr = self.npc_sprites[npc_idx]
                            if hasattr(npc_mgr, 'animations'):
                                if 'emote_down' in npc_mgr.animations:
                                    npc_mgr.play('emote_down')
                                elif 'emote' in npc_mgr.animations:
                                    npc_mgr.play('emote')
            elif self.p2_stage == 1:
                # wait until dialog consumed
                if not self.dialog.visible:
                    # show next line
                    if len(self.p2_dialog_lines) > 1:
                        self.dialog.set_lines([self.p2_dialog_lines[1]])
                        # mark consumed so next will show
                        self.p2_dialog_lines.pop(0)
                    else:
                        self.p2_stage = 2
            elif self.p2_stage == 2:
                # final call to Maria
                if not self.dialog.visible:
                    # show 'Maria?' and then kneel -> proposal
                    self.dialog.set_lines([self.p2_dialog_lines[-1]])
                    # after that, open proposal overlay and hide dialogue
                    self.show_proposal = True
                    self.proposal_active = True
                    self.dialog.visible = False

        # Keep NPCs emoting - don't clean up emotes, let them continue until the end
        
        if self.fireworks_running:
            self.firework_timer -= dt
            for f in self.fireworks:
                f['t'] += dt
            if self.firework_timer <= 0:
                self.fireworks_running = False
                # start post-proposal message
                self.post_message_shown = True
                self.post_message_timer = 3.0

        # After fireworks + post message, transition back to menu
        if self.post_message_shown and not self.fireworks_running:
            self.post_message_timer -= dt
            if self.post_message_timer <= 0:
                # go back to menu
                try:
                    import importlib
                    mod = importlib.import_module('menu_scene')
                    cls = getattr(mod, 'MenuScene')
                    if self.manager:
                        self.manager.go_to(cls(self.manager))
                except Exception:
                    pass

        # Cursor repulsion logic: push the mouse away from the NO button
        if self.show_proposal and self.proposal_active and not self.fireworks_running and self.current_question == 0:
            try:
                box, yes_rect, no_rect = self._get_proposal_rects()
                mx, my = pygame.mouse.get_pos()
                cx = no_rect.x + no_rect.w / 2
                cy = no_rect.y + no_rect.h / 2
                dx = mx - cx
                dy = my - cy
                dist = math.hypot(dx, dy)
                # repulsion radius and strength
                radius = 120
                if dist < radius and dist > 0:
                    # normalized direction from NO center to mouse
                    nx = dx / dist
                    ny = dy / dist
                    # push amount grows when closer
                    push = (radius - dist) * 1.6
                    new_x = mx + nx * push
                    new_y = my + ny * push
                    surf = pygame.display.get_surface()
                    if surf:
                        sw, sh = surf.get_size()
                        new_x = max(0, min(sw - 1, int(new_x)))
                        new_y = max(0, min(sh - 1, int(new_y)))
                        try:
                            pygame.mouse.set_pos((new_x, new_y))
                        except Exception:
                            # some platforms may restrict set_pos; ignore gracefully
                            pass
                elif dist == 0:
                    # exactly at center, nudge upward
                    try:
                        pygame.mouse.set_pos((int(mx), int(my - 40)))
                    except Exception:
                        pass
            except Exception:
                pass

        # Update all character animations
        dt_ms = int(dt * 1000)
        for mgr_name in ['maria_anim_mgr', 'shani_anim_mgr', 'mom_anim_mgr', 'dad_anim_mgr', 'gio_anim_mgr', 'loriana_anim_mgr', 'oresti_anim_mgr', 'marisa_anim_mgr']:
            mgr = getattr(self, mgr_name, None)
            if mgr:
                try:
                    mgr.update(dt_ms)
                except Exception:
                    pass

    def draw(self, surface: pygame.Surface):
        # Draw tilemap background if available
        if self.tilemap_layers:
            for tilemap, layer_data in self.tilemap_layers:
                tilemap.draw_layer(surface, layer_data, scale=self.tilemap_scale)
        else:
            # Fallback: solid color background
            surface.fill((80, 40, 30))
            w, h = surface.get_size()
            # draw table
            pygame.draw.rect(surface, (160, 120, 80), (200, 340, 880, 160))

        # Draw NPCs around table
        for i, (name, _) in enumerate(self.npcs):
            x, y = self.NPC_POSITIONS[i]
            # Draw sprite if available, otherwise draw circle placeholder
            sprite_mgr = self.npc_sprites.get(i)
            if sprite_mgr:
                sprite_mgr.draw(surface, x - 48, y - 64, scale=2.0)  # center sprite (48x64 at 2x = 96x128)
                # Draw name above sprite (like Maria and Shani)
                txt = self.font.render(name, True, (10, 10, 10))
                surface.blit(txt, (x - txt.get_width()//2, y - 70))  # above sprite
            else:
                pygame.draw.circle(surface, (200, 180, 150), (x, y), 28)
                txt = self.font.render(name, True, (10, 10, 10))
                surface.blit(txt, (x - txt.get_width()//2, y - 10))
            


        # Maria at table (player)
        mx, my = self.player_pos
        if self.maria_anim_mgr:
            self.maria_anim_mgr.draw(surface, mx, my, scale=2.0)
        else:
            pygame.draw.rect(surface, (255, 150, 200), (mx, my, 96, 128))  # 2× size
        mlabel = self.font.render("Maria", True, (10, 10, 10))
        surface.blit(mlabel, (mx, my - 25))

        # draw Shani if active
        if self.p2_active:
            if self.shani_anim_mgr:
                self.shani_anim_mgr.draw(surface, int(self.p2_x), int(self.p2_y), scale=2.0)
            else:
                pygame.draw.rect(surface, (120, 170, 240), (int(self.p2_x), int(self.p2_y), 96, 128))  # 2× size
            sl = self.font.render("Shani", True, (10, 10, 10))
            surface.blit(sl, (int(self.p2_x), int(self.p2_y) - 25))

        # Debug: Draw collision boxes if DEBUG is True
        if DEBUG:
            if hasattr(self, 'collision_rects'):
                for rect in self.collision_rects:
                    pygame.draw.rect(surface, (255, 0, 0, 100), rect, 2)
            
            # Maria's collision boxes
            mx, my = self.player_pos
            # Body collision (for environment like tables) - purple
            pygame.draw.rect(surface, (255, 0, 255), pygame.Rect(mx + 24, my, 48, 128), 2)
            # Head collision (for NPCs) - green
            pygame.draw.rect(surface, (0, 255, 0), pygame.Rect(mx + 24, my, 48, 40), 2)
            
            # NPC collision boxes
            for nx, ny in self.NPC_POSITIONS:
                pygame.draw.rect(surface, (255, 255, 0), pygame.Rect((nx - 48) + 24, ny - 64, 48, 40), 2)
            
            # Shani collision box
            if self.p2_active:
                pygame.draw.rect(surface, (0, 255, 255), pygame.Rect(int(self.p2_x) + 24, int(self.p2_y), 48, 40), 2)

        # dialog box - centered on screen
        if self.dialog:
            w, h = surface.get_size()
            # Center horizontally and vertically, moved up 30 pixels
            dialog_x = (w - 760) // 2  # dialog width is 760
            dialog_y = (h - 120) // 2 - 30  # dialog height is 120, moved up 30px
            self.dialog.draw(surface, dialog_x, dialog_y)

        # proposal overlay with questions
        if self.show_proposal:
            box, option1_rect, option2_rect = self._get_proposal_rects()
            pygame.draw.rect(surface, (240, 240, 250), box)
            pygame.draw.rect(surface, (30, 30, 30), box, 2)
            
            # Get current question
            current_q = self.questions[self.current_question]
            title = self.font.render(current_q['question'], True, (10, 10, 10))
            surface.blit(title, (box.x + (box.w - title.get_width())//2, box.y + 24))

            # Option 1 button (always correct answer)
            pygame.draw.rect(surface, (60, 180, 120), option1_rect)
            opt1txt = self.font.render(current_q['option1'], True, (255, 255, 255))
            surface.blit(opt1txt, (option1_rect.x + (option1_rect.w - opt1txt.get_width())//2, option1_rect.y + 12))

            # Option 2 button - wobble on marriage proposal question
            if self.current_question == 0:  # Only one question (marriage proposal)
                # NO button wobbles away from cursor
                try:
                    mx, my = pygame.mouse.get_pos()
                    cx = option2_rect.x + option2_rect.w / 2
                    cy = option2_rect.y + option2_rect.h / 2
                    d = math.hypot(mx - cx, my - cy)
                    wobble = 0
                    if d < 160:
                        wobble = int((160 - d) / 24)
                    wobble_rect = option2_rect.move(0, -wobble)
                except Exception:
                    wobble_rect = option2_rect
                
                pygame.draw.rect(surface, (200, 80, 80), wobble_rect)
                opt2txt = self.font.render(current_q['option2'], True, (255, 255, 255))
                surface.blit(opt2txt, (wobble_rect.x + (wobble_rect.w - opt2txt.get_width())//2, wobble_rect.y + 12))
            else:
                # Regular button for non-marriage questions
                pygame.draw.rect(surface, (180, 180, 190), option2_rect)
                opt2txt = self.font.render(current_q['option2'], True, (255, 255, 255))
                surface.blit(opt2txt, (option2_rect.x + (option2_rect.w - opt2txt.get_width())//2, option2_rect.y + 12))

        # fireworks
        if self.fireworks_running:
            for f in self.fireworks:
                # simple radial burst growing with time
                r = int((f['t'] + 0.1) * 40)
                for a in range(8):
                    ang = a * (math.pi * 2 / 8) + f['t']
                    fx = int(f['x'] + math.cos(ang) * r)
                    fy = int(f['y'] + math.sin(ang) * r)
                    pygame.draw.circle(surface, f['color'], (fx, fy), max(2, 6 - int(f['t'])))

        # post-proposal message
        if self.post_message_shown and not self.fireworks_running:
            msg = self.font.render("That went well.", True, (255, 240, 220))
            surface.blit(msg, ((w - msg.get_width()) // 2, 80))

    def _check_collision(self, x, y):
        """Check if position collides with environment or other characters.
        Returns: True for environment collision, ('npc', index) for NPC collision, False for no collision
        """
        # Maria's collision box (head area: 48x40)
        maria_rect = pygame.Rect(x + 24, y, 48, 40)
        
        # Environment collision - use body rect to prevent walking through tables/objects
        # Body rect covers from head to feet for solid objects like tables
        body_rect = pygame.Rect(x + 24, y, 48, 128)
        if hasattr(self, 'collision_rects'):
            for coll_rect in self.collision_rects:
                if body_rect.colliderect(coll_rect):
                    return True
        
        # NPC collision (head area: 48x40)
        for i, (nx, ny) in enumerate(self.NPC_POSITIONS):
            # NPCs drawn at (nx-48, ny-64), collision box at top
            npc_rect = pygame.Rect((nx - 48) + 24, ny - 64, 48, 40)
            if maria_rect.colliderect(npc_rect):
                return ('npc', i)
        
        # Shani collision (head area)
        if self.p2_active:
            shani_rect = pygame.Rect(int(self.p2_x) + 24, int(self.p2_y), 48, 40)
            if maria_rect.colliderect(shani_rect):
                return True
        
        return False

    def _get_proposal_rects(self):
        """Return (box_rect, yes_rect, no_rect) for current display size."""
        w, h = pygame.display.get_surface().get_size()
        box = pygame.Rect((w - 520)//2, (h - 220)//2, 520, 220)
        yes_rect = pygame.Rect(box.x + 60, box.y + 140, 160, 48)
        no_rect = pygame.Rect(box.x + 300, box.y + 140, 160, 48)
        return box, yes_rect, no_rect
