import pygame
from settings import *

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
