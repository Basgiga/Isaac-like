import pygame
from settings import *
from os.path import join, dirname, abspath

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(*groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((0, 100, 0, 100))  # Fully transparent
        self.rect = self.image.get_rect(center=pos)

class Tear(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups, collision_sprites):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
        self.image = surf.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = direction.normalize()
        self.speed = 600
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.lifetime = 1200
        self.spawn_time = pygame.time.get_ticks()


    def update(self, dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
        if not self.screen_rect.colliderect(self.rect):
            self.kill()
        if pygame.sprite.spritecollide(self, self.collision_sprites, False):
            self.kill()

class Enemy_Greed(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'enemy.png')  # Path to greed enemy image
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.collision_sprites = collision_sprites
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 100  # Adjust as needed

    def update(self, dt):
        # Basic movement: just move down for now
        self.direction = pygame.Vector2(0, 1)
        self.rect.y += self.direction.y * self.speed * dt

        # Collision check (very basic for now)
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                self.direction.y = 0  # Stop moving if there's a collision


class Rock(CollisionSprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE), groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'rock.png')  # Path to rock image
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.collision_sprites = collision_sprites

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'assets', 'coin.png')  # Path to coin image
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        # Coin doesn't move (for now)
        pass