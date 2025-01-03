import pygame
from load_image import load_image
from tiles import TILE_WIDTH, TILE_HEIGHT
WIDTH = 24
HEIGHT = 48
SPEED = 3


class Player(pygame.sprite.Sprite):

    def __init__(self, x_tile, y_tile, *group):
        super().__init__(*group)
        self.image = load_image("player_v2.png")
        self.rect = self.image.get_rect()
        self.rect.x = x_tile * TILE_WIDTH
        self.rect.y = y_tile * TILE_HEIGHT
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.current_cell = None

    def define_your_current_tile(self, floor_group):
        for i in floor_group:
            if i.rect.collidepoint(self.rect.centerx, self.rect.centery):
                self.current_cell = i.x_cell, i.y_cell

    def update(self, left, right, up, down, direction, walls_group, floor_group):
        if left:
            self.horizontal_speed = -SPEED
        elif right:
            self.horizontal_speed = SPEED
        else:
            self.horizontal_speed = 0
        if up:
            self.vertical_speed = -SPEED
        elif down:
            self.vertical_speed = SPEED
        else:
            self.vertical_speed = 0

        if direction == "down":
            if self.vertical_speed:
                self.image = load_image("player_v2.png")
                # анимация
            else:
                self.image = load_image("player_v2.png")
                #сделать статичное изображение

        if direction == "up":
            if self.vertical_speed:
                self.image = load_image("player_up_v2.png")
                # анимация
            else:
                self.image = load_image("player_up_v2.png")
                #сделать статичное изображение

        if direction == "right":
            if self.horizontal_speed:
                self.image = load_image("player_right_v2.png")
                # анимация
            else:
                self.image = load_image("player_right_v2.png")
                # сделать статичное изображение

        if direction == "left":
            if self.horizontal_speed:
                self.image = load_image("player_left_v2.png")
                # анимация
            else:
                self.image = load_image("player_left_v2.png")
                #сделать статичное изображение
        res = self.collide(walls_group)
        if res == 3:
            self.rect.x += self.horizontal_speed
            self.rect.y += self.vertical_speed
        if res == 2:
            self.rect.x += self.horizontal_speed
        if res == 1:
            self.rect.y += self.vertical_speed

        self.define_your_current_tile(floor_group)

    def collide(self, walls_group):
        can_move = True
        can_move_vertical = True
        can_move_horizontal = True
        for i in walls_group:
            if i.rect.colliderect(pygame.Rect(self.rect.left + self.horizontal_speed, self.rect.top + self.vertical_speed, WIDTH, HEIGHT)):
                can_move = False
            if i.rect.colliderect(pygame.Rect(self.rect.left, self.rect.top + self.vertical_speed, WIDTH, HEIGHT)):
                can_move_vertical = False
            if i.rect.colliderect(pygame.Rect(self.rect.left + self.horizontal_speed, self.rect.top, WIDTH, HEIGHT)):
                can_move_horizontal = False
        if can_move:
            return 3
        elif can_move_horizontal:
            return 2
        elif can_move_vertical:
            return 1
        return 0