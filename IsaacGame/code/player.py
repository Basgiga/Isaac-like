from settings import *
import pygame
from os.path import join, dirname, abspath

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        base_folder = dirname(dirname(abspath(__file__)))
        image_path = join(base_folder, 'images', 'player', 'isaac_sprite.png')
        self.original_image = pygame.image.load(image_path).convert_alpha()
        new_width = 512/7
        new_height = 603/7
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=pos)
        self.image.set_colorkey((0, 0, 0))
        self.hitbox_rect = self.rect.inflate(-20,-30)

        # movement
        self.direction = pygame.Vector2() # no inputs = no movement
        self.speed = 250 # speed
        self.collision_sprites = collision_sprites # seeing the collision sprites

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a]) # right/left
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w]) # down/up
        self.direction = self.direction.normalize() if self.direction else self.direction # keep same speed



    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt #movement in time
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt #  --||--
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                #print(direction)

    def update(self,dt):
        self.input()
        self.move(dt)

