import pygame.sprite
from load_image import load_image
from constants import TILE_WIDTH, TILE_HEIGHT

# ключи - символы на карте декораций, значения - названия файлов с изображениями соответствующих клеток
decor = {"-": "default_floor.png", "#": "default_wall.png", "@": "end_tile.png", "*": "tube.png",
         "%": "wire_wall.png", "<": "damaged_floor1.png", ">": "damaged_floor2.png", "^": "heavy_damaged_floor.png",
         "=": "left_shaded_floor.png", "'": "corner_floor.png", "+": "top_shaded_floor.png"}


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y,  decor_map, *group):
        super().__init__(*group)
        try:
            self.image = load_image("tiles/" + decor[decor_map[y][x]])
        except Exception:
            self.image = load_image("tiles/default_wall.png")  # загрузить дефолтное изображение в случае ошибки
        self.x_cell = x
        self.y_cell = y
        self.rect = pygame.Rect(self.x_cell * TILE_WIDTH, self.y_cell * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, decor_map, *group):
        super().__init__(*group)
        try:
            self.image = load_image("tiles/" + decor[decor_map[y][x]])
        except Exception:
            self.image = load_image("tiles/default_floor.png")
        self.x_cell = x
        self.y_cell = y
        self.rect = pygame.Rect(self.x_cell * TILE_WIDTH, self.y_cell * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
