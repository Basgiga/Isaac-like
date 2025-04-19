import pygame.sprite
from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, surface, target_position):  # Changed 'self.display_surface' to 'surface'
        self.offset.x = -(target_position[0] - WIDTH / 2)
        self.offset.y = -(target_position[1] - HEIGHT / 2)

        for sprite in self:
            draw_pos = sprite.rect.center + self.offset  # Calculate draw position relative to the camera
            draw_rect = sprite.image.get_rect(center=draw_pos)  # Get a rect centered at the draw position
            surface.blit(sprite.image, draw_rect.topleft)