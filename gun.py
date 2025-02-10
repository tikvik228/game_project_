import pygame
from load_image import load_image
from constants import TILE_WIDTH, TILE_HEIGHT

class Gun(pygame.sprite.Sprite):
    """класс оружия, лежащего на уровне"""
    def __init__(self, name, img, x_tile, y_tile, *group):
        super().__init__(*group)
        self.name = name
        self.image = load_image(img)
        self.rect = self.image.get_rect()
        self.rect.center = x_tile * TILE_WIDTH + 0.5 * TILE_WIDTH, y_tile * TILE_HEIGHT + 0.5 * TILE_HEIGHT
