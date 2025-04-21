# sprites.py
import pygame
import random
from settings import *
from os.path import join, dirname, abspath
from player import Player # <<< --- FIX 1: Import Player --- >>>

# Define Health Bar colors (Keep existing definitions)
HEALTH_BAR_WIDTH = 40
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_OFFSET_Y = 10
HEALTH_COLOR = (0, 255, 0)
HEALTH_BG_COLOR = (255, 0, 0)
HEALTH_BORDER_COLOR = (0, 0, 0)

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(*groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((0, 100, 0, 0)) # Kept original fill
        self.rect = self.image.get_rect(center=pos)

class Tear(pygame.sprite.Sprite):
    # Constructor already accepts enemy_sprites from previous fix
    def __init__(self, surf, pos, direction, groups, collision_sprites, enemy_sprites):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites
        self.image = surf.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        try:
            self.direction = direction.normalize()
        except ValueError:
            self.direction = pygame.math.Vector2(0,-1) # Default if zero vector
        self.speed = 600 # Keep original speed
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.lifetime = 1200
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        # Kept original update logic
        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime: self.kill(); return
        if pygame.sprite.spritecollide(self, self.collision_sprites, False): self.kill(); return
        enemies_hit = pygame.sprite.spritecollide(self, self.enemy_sprites, False)
        if enemies_hit:
            for enemy in enemies_hit:
                if hasattr(enemy, 'take_damage'): enemy.take_damage(1)
            self.kill()
            return


class Enemy_Greed(pygame.sprite.Sprite):
    # <<< --- FIX 2: Added enemy_sprites parameter --- >>>
    def __init__(self, pos, groups, collision_sprites, player, enemy_sprites):
        super().__init__(groups)
        self.player = player
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites # <<< --- FIX 3: Store enemy_sprites --- >>>
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'enemy.png')
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200 # <<< Kept original speed value >>>

        self.max_hit_points = 7
        self.hit_points = 7

    def move(self, dt):
        # Kept original move logic
        player_pos = self.player.rect.center
        enemy_pos = self.rect.center
        self.direction = pygame.math.Vector2(player_pos) - pygame.math.Vector2(enemy_pos)
        if self.direction.magnitude() > 0: self.direction = self.direction.normalize()
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        # <<< --- FIX 4: Check against walls, player, AND other enemies --- >>>
        collidable_entities = list(self.collision_sprites) + [self.player] + list(self.enemy_sprites)

        for entity in collidable_entities:
            # Don't collide with self
            if entity == self:
                continue

            # Use hitbox_rect if available, else regular rect
            entity_hitbox = getattr(entity, 'hitbox_rect', entity.rect)

            if entity_hitbox.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: # Moving right
                        self.hitbox_rect.right = entity_hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox_rect.left = entity_hitbox.right
                    self.rect.centerx = self.hitbox_rect.centerx
                    # Stop horizontal movement upon collision? Optional, but helps prevent sticking
                    # self.direction.x = 0
                else: # Vertical
                    if self.direction.y > 0: # Moving down
                        self.hitbox_rect.bottom = entity_hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox_rect.top = entity_hitbox.bottom
                    self.rect.centery = self.hitbox_rect.centery
                    # Stop vertical movement upon collision? Optional
                    # self.direction.y = 0

    def take_damage(self, amount):
        # Kept original logic
        self.hit_points -= amount
        print(f"Enemy_Greed took {amount} damage, HP: {self.hit_points}/{self.max_hit_points}")
        if self.hit_points <= 0: self.kill(); print("Enemy_Greed defeated!")

    def draw_health_bar(self, surface, offset):
        # Kept original logic
        health_ratio = max(0, self.hit_points / self.max_hit_points)
        bar_x = self.rect.left - offset.x
        bar_y = self.rect.bottom + HEALTH_BAR_OFFSET_Y - offset.y
        bg_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BG_COLOR, bg_rect)
        health_rect = pygame.Rect(bar_x, bar_y, int(HEALTH_BAR_WIDTH * health_ratio), HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_COLOR, health_rect)
        pygame.draw.rect(surface, HEALTH_BORDER_COLOR, bg_rect, 1)

    def update(self, dt):
        # Kept original logic
        self.move(dt)


class Spider(pygame.sprite.Sprite):
    # <<< --- FIX 2: Added enemy_sprites parameter --- >>>
    def __init__(self, pos, groups, collision_sprites, player, enemy_sprites):
        super().__init__(groups)
        self.player = player
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites # <<< --- FIX 3: Store enemy_sprites --- >>>

        # Image setup (Kept original logic)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'spider.png')
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            temp_image = pygame.transform.scale(self.original_image, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
            self.image = temp_image
        except pygame.error:
             print(f"Warning: Could not load spider.png, using enemy.png instead.")
             image_path = join(base_folder, 'images', 'assets', 'enemy.png')
             self.original_image = pygame.image.load(image_path).convert_alpha()
             temp_image = pygame.transform.scale(self.original_image, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
             temp_image.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_ADD) # Tint fallback
             self.image = temp_image

        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)

        # Movement (Kept original values/logic)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 120
        self.speed_t_player = 320
        self.t_player = False
        self.state = 'idle'
        self.move_duration = 1000
        self.stop_duration = 500
        self.last_state_change_time = pygame.time.get_ticks()

        # Stats (Kept original values)
        self.max_hit_points = 5
        self.hit_points = 5

    def get_movement_direction(self):
        # Kept original logic
        if random.random() < 2/3:
            self.t_player = True
            player_pos = self.player.rect.center
            enemy_pos = self.rect.center
            direction = pygame.math.Vector2(player_pos) - pygame.math.Vector2(enemy_pos)
            if direction.magnitude() > 0: return direction.normalize()
            else: return pygame.math.Vector2(0, 0)
        else:
            self.t_player = False
            rand_dir = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if rand_dir.magnitude() > 0: return rand_dir.normalize()
            else: return pygame.math.Vector2(1, 0)

    def move(self, dt):
        if self.direction.magnitude() > 0 and self.t_player:
            self.hitbox_rect.x += self.direction.x * self.speed_t_player * dt
            self.collision('horizontal')
            self.hitbox_rect.y += self.direction.y * self.speed_t_player * dt
            self.collision('vertical')
            self.rect.center = self.hitbox_rect.center
        elif self.direction.magnitude() > 0:
            self.hitbox_rect.x += self.direction.x * self.speed * dt
            self.collision('horizontal')
            self.hitbox_rect.y += self.direction.y * self.speed * dt
            self.collision('vertical')
            self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        collidable_entities = list(self.collision_sprites) + [self.player] + list(self.enemy_sprites)

        for entity in collidable_entities:
            if entity == self:
                continue

            entity_hitbox = getattr(entity, 'hitbox_rect', entity.rect)

            if entity_hitbox.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = entity_hitbox.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = entity_hitbox.right
                    self.rect.centerx = self.hitbox_rect.centerx
                    self.direction.x = 0
                else:
                    if self.direction.y > 0: # Moving down
                        self.hitbox_rect.bottom = entity_hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox_rect.top = entity_hitbox.bottom
                    self.rect.centery = self.hitbox_rect.centery
                    self.direction.y = 0

    def take_damage(self, amount):
        self.hit_points -= amount
        print(f"Spider took {amount} damage, HP: {self.hit_points}/{self.max_hit_points}")
        if self.hit_points <= 0: self.kill(); print("Spider defeated!")

    def draw_health_bar(self, surface, offset):
        health_ratio = max(0, self.hit_points / self.max_hit_points)
        bar_x = self.rect.left - offset.x
        bar_y = self.rect.bottom + HEALTH_BAR_OFFSET_Y - offset.y
        bg_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BG_COLOR, bg_rect)
        health_rect = pygame.Rect(bar_x, bar_y, int(HEALTH_BAR_WIDTH * health_ratio), HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_COLOR, health_rect)
        pygame.draw.rect(surface, HEALTH_BORDER_COLOR, bg_rect, 1)

    def update(self, dt):
         # Kept original update logic
        current_time = pygame.time.get_ticks()
        time_since_last_change = current_time - self.last_state_change_time

        if self.state == 'idle':
            self.direction = self.get_movement_direction()
            self.state = 'moving'
            self.last_state_change_time = current_time
            self.move(dt)

        elif self.state == 'moving':
            if time_since_last_change >= self.move_duration:
                self.state = 'stopping'
                self.direction = pygame.math.Vector2(0, 0)
                self.last_state_change_time = current_time
            else:
                self.move(dt)

        elif self.state == 'stopping':
            if time_since_last_change >= self.stop_duration:
                self.state = 'idle'
                self.last_state_change_time = current_time


class Rock(CollisionSprite):
    # Kept original Rock class
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE), groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'rock.png')
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

class Coin(pygame.sprite.Sprite):
    # Kept original Coin class
    def __init__(self, pos, groups):
        super().__init__(groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'coin.png')
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        pass