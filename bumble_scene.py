import pygame
import random
from scene import Scene


class BumbleScene(Scene):
    """Simple swipe-style scene: Maria swipes through profiles until she finds Shani."""

    def __init__(self, manager=None):
        super().__init__(manager)
        # Four profiles before Shani - can only reject these
        self.profiles = [
            {
                "name": "Broke Becky",
                "age": "24",
                "character": "loriana",
                "occupation": "Professional Chicken Nugget Connoisseur",
                "looking_for": "A sugar daddy who appreciates the finer things (like 50-piece nugget meals)",
                "hobbies": "Online shopping, spending money I don't have, taste-testing every nugget shape",
                "match": False
            },
            {
                "name": "Helpless Hannah", 
                "age": "28",
                "character": "marisa",
                "occupation": "Self-Proclaimed Netflix Critic & Professional Couch Potato",
                "looking_for": "Someone to carry me emotionally (and maybe physically). My ex might tag along sometimes",
                "hobbies": "Binge-watching reality TV, ugly crying, asking 'what are we?' on the first date",
                "match": False
            },
            {
                "name": "Judgmental Jessica",
                "age": "32 (actually 45)",
                "character": "mom",
                "occupation": "Aspiring Instagram Influencer (12 followers, 11 are my mom's accounts)",
                "looking_for": "An unpaid personal photographer who knows my best angles. Must be OK with 47 retakes",
                "hobbies": "Critiquing everyone's life choices, perfecting my ring light setup, #livingmybestlife",
                "match": False
            },
            {
                "name": "Chaotic Casey",
                "age": "26",
                "character": "maria",
                "occupation": "Professional Chaos Creator & Amateur Arsonist",
                "looking_for": "Someone with good insurance. I can't promise I won't accidentally set you on fire",
                "hobbies": "Starting drama, pulling fire alarms, getting banned from public spaces",
                "match": False
            },
            {
                "name": "Shani",
                "age": "27",
                "character": "shani",
                "occupation": "Software Engineer (I turn coffee into code)",
                "looking_for": "Someone adventurous, kind, and patient with my terrible puns. Bonus if your name is Maria!",
                "hobbies": "Hiking, debugging life's problems, perfecting the art of the dad joke",
                "match": True
            },
        ]
        self.index = 0
        self.font = None
        self.transition_timer = 0.0
        self.matched = False
        self.character_sprites = {}
        self.heart_image = None
        self.hearts = []  # List of heart positions and properties
        self.heart_spawn_timer = 0.0

    def start(self):
        self.font = pygame.font.SysFont(None, 36)
        self.index = 0
        self.matched = False
        self._load_character_sprites()
        
        # Load heart image
        try:
            self.heart_image = pygame.image.load("art/backgrounds/red_heart.png").convert_alpha()
            # Scale heart to reasonable size
            self.heart_image = pygame.transform.scale(self.heart_image, (40, 40))
        except Exception as e:
            print(f"Failed to load red_heart.png: {e}")
    
    def _load_character_sprites(self):
        """Load character sprites for profiles."""
        for profile in self.profiles:
            char_name = profile.get("character")
            if char_name:
                try:
                    sprite_sheet = pygame.image.load(f"art/characters/{char_name}/idle.png").convert_alpha()
                    # Get the front-facing sprite (third row down - y=128)
                    sprite = sprite_sheet.subsurface(pygame.Rect(0, 128, 64, 64))
                    self.character_sprites[char_name] = sprite
                except Exception as e:
                    print(f"Failed to load sprite for {char_name}: {e}")

    def handle_event(self, event: pygame.event.EventType):
        if event.type == pygame.KEYDOWN:
            cur = self.profiles[self.index]
            if event.key in (pygame.K_x, pygame.K_LEFT, pygame.K_a):
                # Reject - always allowed
                self._reject()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_c, pygame.K_RIGHT, pygame.K_d):
                # Accept - only allowed for Shani (the match)
                if cur.get("match"):
                    self._accept()
                # Otherwise, do nothing (can't accept non-matches)

    def _reject(self):
        if self.index < len(self.profiles) - 1:
            self.index += 1

    def _accept(self):
        """Handle accepting Shani's profile - triggers match animation."""
        self.matched = True
        self.transition_timer = 8.0

    def _spawn_heart(self):
        """Spawn a new heart with random properties."""
        x = random.randint(0, 1024)
        y = -50  # Start from top
        speed = random.randint(80, 150)
        size_mult = random.uniform(0.7, 1.3)
        self.hearts.append({'x': x, 'y': y, 'speed': speed, 'size_mult': size_mult})

    def _update_hearts(self, dt: float):
        """Update heart positions and remove off-screen hearts."""
        for heart in self.hearts[:]:
            heart['y'] += heart['speed'] * dt
            if heart['y'] > 820:
                self.hearts.remove(heart)

    def update(self, dt: float):
        if self.matched:
            # Spawn hearts continuously
            if self.heart_image:
                self.heart_spawn_timer += dt
                if self.heart_spawn_timer > 0.15:
                    self.heart_spawn_timer = 0
                    self._spawn_heart()
            
            # Update heart positions
            self._update_hearts(dt)
            
            # Transition to next scene
            self.transition_timer -= dt
            if self.transition_timer <= 0 and self.manager:
                from transition_scene import TransitionScene
                from drive_scene import DriveScene
                next_scene_factory = lambda m: DriveScene('car', 10.0, 'night', m)
                self.manager.go_to(TransitionScene(
                    "It's time to drive to the city\nfor your first date with Shani!",
                    next_scene_factory,
                    duration=5.0,
                    manager=self.manager
                ))

    def _draw_title(self, surface: pygame.Surface, w: int):
        """Draw the 'Welcome to Bumble!' title with shadow."""
        title_font = pygame.font.SysFont(None, 64, bold=True)
        shadow_surf = title_font.render("Welcome to Bumble!", True, (200, 150, 0))
        shadow_x = (w - shadow_surf.get_width()) // 2
        surface.blit(shadow_surf, (shadow_x + 3, 33))
        
        title_surf = title_font.render("Welcome to Bumble!", True, (255, 255, 255))
        title_x = (w - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, 30))

    def _draw_card_background(self, surface: pygame.Surface, box: pygame.Rect):
        """Draw the card shadow and white background."""
        shadow_box = pygame.Rect(box.x + 8, box.y + 8, box.width, box.height)
        pygame.draw.rect(surface, (200, 150, 0, 80), shadow_box, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), box, border_radius=12)

    def _draw_character_sprite(self, surface: pygame.Surface, char_name: str, box: pygame.Rect):
        """Draw the character sprite centered at top of card."""
        if char_name and char_name in self.character_sprites:
            sprite = self.character_sprites[char_name]
            scaled_sprite = pygame.transform.scale(sprite, (192, 192))
            sprite_x = box.x + (box.width - 192) // 2
            sprite_y = box.y + 30
            surface.blit(scaled_sprite, (sprite_x, sprite_y))

    def _draw_icon(self, surface: pygame.Surface, icon_type: str, x: int, y: int, size: int = 20):
        """Draw a simple icon (briefcase, heart, or star)."""
        icon_color = (120, 120, 130)
        if icon_type == "briefcase":
            pygame.draw.rect(surface, icon_color, (x + 2, y + 8, size - 4, size - 8), 2)
            pygame.draw.rect(surface, icon_color, (x + 6, y + 4, size - 12, 6), 2)
        elif icon_type == "heart":
            center_x = x + size // 2
            pygame.draw.circle(surface, icon_color, (center_x - 5, y + 6), 5, 2)
            pygame.draw.circle(surface, icon_color, (center_x + 5, y + 6), 5, 2)
            pygame.draw.polygon(surface, icon_color, [
                (center_x - 10, y + 8),
                (center_x, y + 18),
                (center_x + 10, y + 8)
            ], 2)
        elif icon_type == "star":
            center_x = x + size // 2
            center_y = y + size // 2
            points = []
            for i in range(5):
                angle = i * 144 - 90
                px = center_x + int(8 * pygame.math.Vector2(1, 0).rotate(angle).x)
                py = center_y + int(8 * pygame.math.Vector2(1, 0).rotate(angle).y)
                points.append((px, py))
            pygame.draw.polygon(surface, icon_color, points, 2)

    def _draw_info_badge(self, surface: pygame.Surface, box: pygame.Rect, icon_type: str, 
                        label: str, content: str, y_pos: int, label_font, info_font) -> int:
        """Draw an info badge with icon, label, and wrapped content. Returns new y position."""
        badge_padding = 12
        badge_x = box.x + 30
        badge_width = box.width - 60
        max_content_width = badge_width - 80
        
        # Wrap text content
        words = content.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if info_font.size(test_line)[0] <= max_content_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw background
        badge_height = badge_padding * 2 + 20 + (len(lines) * 26)
        badge_rect = pygame.Rect(badge_x, y_pos, badge_width, badge_height)
        pygame.draw.rect(surface, (245, 245, 250), badge_rect, border_radius=8)
        
        # Draw icon
        self._draw_icon(surface, icon_type, badge_x + badge_padding, y_pos + badge_padding, 22)
        
        # Draw label
        label_surf = label_font.render(label, True, (50, 50, 50))
        surface.blit(label_surf, (badge_x + badge_padding + 35, y_pos + badge_padding))
        
        # Draw content lines
        content_y = y_pos + badge_padding + 28
        for line in lines:
            line_surf = info_font.render(line, True, (80, 80, 80))
            surface.blit(line_surf, (badge_x + badge_padding + 35, content_y))
            content_y += 26
        
        return y_pos + badge_height + 12

    def draw(self, surface: pygame.Surface):
        surface.fill((255, 200, 0))  # Yellow background
        w, h = surface.get_size()
        
        # Draw title
        self._draw_title(surface, w)
        
        # Card dimensions
        box_w = 700
        box_h = h - 140
        box = pygame.Rect((w - box_w) // 2, 100, box_w, box_h)
        
        # Draw card background
        self._draw_card_background(surface, box)

        # Current profile
        cur = self.profiles[self.index]
        name_font = pygame.font.SysFont(None, 48, bold=True)
        label_font = pygame.font.SysFont(None, 26, bold=True)
        info_font = pygame.font.SysFont(None, 26)
        small_font = pygame.font.SysFont(None, 24)
        
        # Draw character sprite
        self._draw_character_sprite(surface, cur.get("character"), box)
        
        # Name and age
        text_y = box.y + 240
        name_age_text = f"{cur['name']}, {cur['age']}"
        name_age_surf = name_font.render(name_age_text, True, (10, 10, 10))
        name_age_x = box.x + (box.width - name_age_surf.get_width()) // 2
        surface.blit(name_age_surf, (name_age_x, text_y))
        
        # Draw profile badges
        current_y = text_y + 60
        current_y = self._draw_info_badge(surface, box, "briefcase", "Occupation", cur['occupation'], current_y, label_font, info_font)
        current_y = self._draw_info_badge(surface, box, "heart", "Looking for", cur['looking_for'], current_y, label_font, info_font)
        current_y = self._draw_info_badge(surface, box, "star", "Hobbies", cur['hobbies'], current_y, label_font, info_font)
        
        # Hint text below the card
        is_match = cur.get("match", False)
        hint = "Press X to reject"
        if is_match:
            hint += " — Press C to accept"
        hint_surf = small_font.render(hint, True, (0, 0, 0))
        hint_x = (w - hint_surf.get_width()) // 2
        surface.blit(hint_surf, (hint_x, box.y + box_h + 15))

        if self.matched:
            # Draw hearts
            if self.heart_image:
                for heart in self.hearts:
                    # Scale heart based on size_mult
                    size = int(40 * heart['size_mult'])
                    scaled_heart = pygame.transform.scale(self.heart_image, (size, size))
                    # Get rect for centered blitting
                    rect = scaled_heart.get_rect(center=(heart['x'], heart['y']))
                    surface.blit(scaled_heart, rect)
            
            m = pygame.font.SysFont(None, 48).render("It's a match!", True, (255, 50, 120))
            surface.blit(m, ((w - m.get_width()) // 2, box.y - 64))


