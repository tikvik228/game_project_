import pygame.sprite
from load_image import load_image
TILE_WIDTH = 64
TILE_HEIGHT = 64


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y,  *group):
        super().__init__(*group)
        self.image = load_image("wall_tile.png")
        self.x_cell = x
        self.y_cell = y
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        self.rect = pygame.Rect(self.x_cell * TILE_WIDTH, self.y_cell * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = load_image("floor_tile.png")
        self.x_cell = x
        self.y_cell = y
        self.image = pygame.transform.scale(self.image, (TILE_WIDTH, TILE_HEIGHT))
        self.rect = pygame.Rect(self.x_cell * TILE_WIDTH, self.y_cell * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
