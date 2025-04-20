import pygame
from os.path import join
from os import walk


def nwd(a, b):
    if b == 0:
        return a
    else:
        return nwd(b, a % b)
# Pygame settings
WIDTH = 1400
HEIGHT = 800
FPS = 60
TILE_SIZE = int(nwd(WIDTH,HEIGHT)//3.5)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ROOM_WIDTH_TILES = 10
ROOM_HEIGHT_TILES = 8

print(nwd(WIDTH,HEIGHT))