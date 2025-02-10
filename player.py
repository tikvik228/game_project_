import pygame
from load_image import load_image
from constants import *
from bullet import Bullet
WIDTH = 24
HEIGHT = 48
SPEED = 2
ANIMATION_DELAY = 150


class Player(pygame.sprite.Sprite):
    def __init__(self, x_tile, y_tile,  *group):
        super().__init__(*group)
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.current_cell = x_tile, y_tile
        self.health = 200
        self.curr_inv_pos = None # номер текущей нажатой ячейки в инвентаре
        self.bullet_angle = 90
        self.is_dead = False

        self.last_anim_update = pygame.time.get_ticks()
        self.curr_frame = 0

        # та же логика, что и в словаре с анимациями робота
        self.left_move, self.right_move, self.up_move, self.down_move = [], [], [], []
        self.left_stand, self.right_stand, self.up_stand, self.down_stand = [], [], [], []
        self.directions = {"left": (self.left_move, self.left_stand), "right": (self.right_move, self.right_stand),
                           "up": (self.up_move, self.up_stand), "down": (self.down_move, self.down_stand)}
        self.current_direction = "down"  # текущее направление изображения спрайта
        self.current_skin_directory = "default"  # название директории с текущим скином, сейчас скин по умолчанию
        self.skin_was_changed = False  # переменная нужна,чтобы обновлять словарь с изображениями лишь при необходимости
        for d in self.directions.keys():
            self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/move_1.png'))
            self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
            self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/move_2.png'))
            self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
            self.directions[d][1].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
        self.image = self.directions[self.current_direction][1][0]  # выбор первого изображения
        self.rect = self.image.get_rect()
        self.rect.center = x_tile * TILE_WIDTH + 0.5 * TILE_WIDTH, y_tile * TILE_HEIGHT + 0.5 * TILE_HEIGHT

    def define_your_current_tile(self):
        self.current_cell = self.rect.centerx // 64, self.rect.centery // 64

    def update(self, left, right, up, down, direction, walls_group, bullet_group, sentries):
        if self.health <= 0:
            self.is_dead = True
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
        self.current_direction = direction
        if self.current_direction == "down":
            self.bullet_angle = 90  # вместе с направлением спрайта изменяется угол выпускаемых пуль

        if self.current_direction == "up":
            self.bullet_angle = -90

        if self.current_direction == "right":
            self.bullet_angle = 0

        if self.current_direction == "left":
            self.bullet_angle = 180
        res = self.collide(walls_group, bullet_group, sentries)
        if res == 3:
            self.rect.x += self.horizontal_speed
            self.rect.y += self.vertical_speed
        if res == 2:
            self.rect.x += self.horizontal_speed
        if res == 1:
            self.rect.y += self.vertical_speed

        self.define_your_current_tile()
        self.animation()

    def collide(self, walls_group, bullet_group, sentries):
        """функция проверяет столкновения с пулями, а так же проверяет, можно ли игроку идти
        в выбранных направлениях, не врежется ли он в стену или в турель"""
        for i in bullet_group:
            if pygame.sprite.collide_rect(self, i) and i.sender == "enemy":
                self.health -= i.damage
                i.kill()
        # проверка на столкновение происходит так: проверяется столкновение прямоугольников, заданных по будущим
        # координатам игрока со стенами. всего их три: прямоугольник учитывающий и вертикальную, и горизонтальную
        # скорости, учитывающий только вертикальную и только горизонтальную. То есть даже если двинуться по двум
        # направлениям сразу нельзя, но по одному из них можно, скорость в запрещенном направлении будет нулевая,
        # а в разрешенном такая и останется. Действие этой функции хорошо проявляется в "скольжении" по стенкам уровня.
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
        for s in sentries:
            if s.is_dead:
                continue
            if s.rect.colliderect(pygame.Rect(self.rect.left + self.horizontal_speed, self.rect.top + self.vertical_speed, WIDTH, HEIGHT)):
                can_move = False
            if s.rect.colliderect(pygame.Rect(self.rect.left, self.rect.top + self.vertical_speed, WIDTH, HEIGHT)):
                can_move_vertical = False
            if s.rect.colliderect(pygame.Rect(self.rect.left + self.horizontal_speed, self.rect.top, WIDTH, HEIGHT)):
                can_move_horizontal = False
        if can_move:
            return 3
        elif can_move_horizontal:
            return 2
        elif can_move_vertical:
            return 1
        return 0

    def change_inv_cell(self, inventory, num):
        """смена кнопки инвентаря и текущей директории"""
        self.curr_inv_pos = num
        self.skin_was_changed = True
        if inventory.inv[self.curr_inv_pos] is not None:
            self.current_skin_directory = all_equipment[inventory.inv[self.curr_inv_pos][0]]["skin_directory"]
        else:
            self.current_skin_directory = "default"

    def try_to_shoot(self, inventory, bullets_group):
        """стрельба"""
        if self.curr_inv_pos is not None and inventory.inv[self.curr_inv_pos] is not None and inventory.inv[self.curr_inv_pos][1] != 0:
            bul_img = all_equipment[inventory.inv[self.curr_inv_pos][0]]["bullet_image"]
            bul_dmg = all_equipment[inventory.inv[self.curr_inv_pos][0]]["bullet_damage"]
            bul_speed = all_equipment[inventory.inv[self.curr_inv_pos][0]]["bullet_speed"]
            Bullet(bul_img, self.bullet_angle, self.rect.center, bul_speed, bul_dmg, "player", bullets_group)
            inventory.inv[self.curr_inv_pos][1] -= 1

    def animation(self):
        """анимация игрока"""
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_anim_update >= ANIMATION_DELAY:
            if self.skin_was_changed:  # обновление словаря только если скин был изменен
                self.left_move, self.right_move, self.up_move, self.down_move = [], [], [], []
                self.left_stand, self.right_stand, self.up_stand, self.down_stand = [], [], [], []
                self.directions = {"left": (self.left_move, self.left_stand), "right": (self.right_move, self.right_stand),
                                   "up": (self.up_move, self.up_stand), "down": (self.down_move, self.down_stand)}
                for d in self.directions.keys():
                    self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/move_1.png'))
                    self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
                    self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/move_2.png'))
                    self.directions[d][0].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
                    self.directions[d][1].append(load_image(f'player_files/{self.current_skin_directory}/{d}/stand.png'))
                self.skin_was_changed = False
            if self.vertical_speed != 0 or self.horizontal_speed != 0:
                self.image = self.directions[self.current_direction][0][self.curr_frame]
                self.curr_frame = (self.curr_frame + 1) % 4
            else:
                self.image = self.directions[self.current_direction][1][0]
                self.curr_frame = 0
            self.last_anim_update = curr_time