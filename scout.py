import pygame
from load_image import load_image
from constants import TILE_WIDTH, TILE_HEIGHT
from bullet import Bullet
from random import randint
import copy
import math
SPEED = 2
DAMAGE = 5
RADIOUS = TILE_HEIGHT * 3
ANIMATION_DELAY = 150


class Scout(pygame.sprite.Sprite):

    def __init__(self, x_tile, y_tile, x_tile_default, y_tile_default, *group):
        super().__init__(*group)
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.period = randint(700, 1000) # для каждого робота задержка между стрельбой немного отличается
        self.current_cell = x_tile, y_tile
        self.last_shoot_time = -self.period
        self.can_shoot = False
        self.path = None  # список текущего пути
        self.next_tile = self.current_cell  # следущая клетка в пути
        self.begin_cell = x_tile, y_tile  # начальная клетка
        self.default_cell = x_tile_default, y_tile_default  # клетка на которую робот стремится из начальной клетки
        self.player_found = False  # флаг найден ли игрок или нет
        self.what_direction = self.default_cell  # поле, в котором содержится цель робота (который еще не нашел игрока).
        # содержит либо begin_cell либо default_cell
        self.health = 50
        self.is_dead = False
        self.damaged = False # флаг нужен для анимации ранения (спрайт загорается красным цветом)

        self.last_anim_update = pygame.time.get_ticks()
        self.curr_frame = 0  # номер текущего кадра

        # для каждого направления движения влево, вправо, вверх, вниз существуют анимации движения и стрельбы,
        # все они хранятся в списках в словаре с соответствующими ключами.
        self.left_move, self.left_shoot = [], []
        self.right_move, self.right_shoot = [], []
        self.up_move, self.up_shoot = [], []
        self.down_move, self.down_shoot = [], []
        self.directions = {"left": (self.left_move, self.left_shoot), "right": (self.right_move, self.right_shoot),
                           "up": (self.up_move, self.up_shoot), "down": (self.down_move, self.down_shoot)}
        self.current_direction = "left" # поле с текущим направлением
        for d in self.directions.keys():  # загрузка изображений в нужные списки в словаре
            for i in range(1, 5):
                if i <= 2:
                    self.directions[d][0].append(load_image(f'scout_files/{d}/{d}_move_{i}.png'))
                else:
                    self.directions[d][0].append(load_image(f'scout_files/{d}/{d}_move_{i - 2}.png'))
                self.directions[d][1].append(load_image(f'scout_files/{d}/{d}_shoot_{i}.png'))

        self.image = self.directions[self.current_direction][0][0]  # начальный image
        self.rect = self.image.get_rect()
        self.rect.center = x_tile * TILE_WIDTH + 0.5 * TILE_WIDTH, y_tile * TILE_HEIGHT + 0.5 * TILE_HEIGHT
        self.next_tile_cords = self.rect.center  # координаты центра следующей точки в пути

    def define_your_current_tile(self):
        self.current_cell = self.rect.centerx // 64, self.rect.centery // 64

    def update(self, player_x, player_y, player_cell, lvl_map, walls_group, scouts, bullets_group):
        if self.is_dead: # ничего не обновлять при смерти
            return
        self.define_your_current_tile()

        # действия до момента обнаружения игрока (робот ездит по маршруту между двумя заданными клетками)
        if self.player_found is False:
            # проверка находится ли игрок на близком расстоянии от игрока
            if abs(self.current_cell[0] - player_cell[0]) <= 2 and abs(self.current_cell[1] - player_cell[1]) <= 2:
                mini_map = []
                for i in range(self.current_cell[1] - 2, self.current_cell[1] + 3):
                    mini_map.append(list(lvl_map[i][self.current_cell[0] - 2:self.current_cell[0] + 3]))
                # если находится, "вырезать" из основной карты маленькую, чтобы проверить, можно ли в ее рамках
                # добраться до игрока. Это нужно, чтобы робот не замечал игрока по другую сторону стены в совершенно
                # другой комнате
                check = self.next_tile_in_way((player_cell[0] - self.current_cell[0] + 2,
                                              player_cell[1] - self.current_cell[1] + 2), (2, 2), mini_map)
                if check:
                    # если добраться можно, поднимается флаг игрок найден, поведение робота изменяется
                    self.player_found = True
                else:
                    # если нельзя, то продолжать определять маршрут в заданном направлении, которое поочередно меняется
                    # между двумя заданными координатами маршрута
                    if (((self.what_direction[0]) + 0.5) * TILE_WIDTH,
                       ((self.what_direction[1]) + 0.5) * TILE_HEIGHT) == self.rect.center:
                        if self.what_direction == self.default_cell:
                            self.what_direction = self.begin_cell
                        else:
                            self.what_direction = self.default_cell
                    self.next_tile_in_way(self.what_direction, self.current_cell, lvl_map)
            else:
                # если игрок не обнаружен, делать описанное в комме выше
                if (((self.what_direction[0]) + 0.5) * TILE_WIDTH,
                   ((self.what_direction[1]) + 0.5) * TILE_HEIGHT) == self.rect.center:
                    if self.what_direction == self.default_cell:
                        self.what_direction = self.begin_cell
                    else:
                        self.what_direction = self.default_cell
                self.next_tile_in_way(self.what_direction, self.current_cell, lvl_map)

        if self.player_found:
            # если игрок найден, определить маршрут до игрока
            self.next_tile_in_way(player_cell, self.current_cell, lvl_map)

        ban = (((player_cell[0] - 0.5) * TILE_WIDTH, (player_cell[1] + 0.5) * TILE_HEIGHT),
               ((player_cell[0] + 1.5) * TILE_WIDTH, (player_cell[1] + 0.5) * TILE_HEIGHT),
               ((player_cell[0] + 0.5) * TILE_WIDTH, (player_cell[1] - 0.5) * TILE_HEIGHT),
               ((player_cell[0] + 0.5) * TILE_WIDTH, (player_cell[1] + 1.5) * TILE_HEIGHT))
        # ban -кортеж из координат центров клеток, смежных с клеткой игрока. Это максимальные точки приближения к игроку
        if self.rect.center not in ban:

            # если пришел к нужным координатам (координате центра следущей клетки маршрута)
            if (int(self.next_tile_cords[0]), int(self.next_tile_cords[1])) == self.rect.center:
                self.horizontal_speed = 0
                self.vertical_speed = 0

                # проверка, не будет ли следующая клетка маршрута совпадать с той, куда уже стремится другой робот
                # нужно для того, чтобы они не стояли на одной клетке и не сливались таким образом друг с другом
                ok = True
                for other in scouts:
                    if other != self and (not other.is_dead) and other.next_tile == (self.path[0][1], self.path[0][0]):
                        ok = False
                        break
                if ok:  # если клетка прошла проверку, назначить ее своей следующей клеткой, куда будет стремиться робот
                    self.next_tile = (self.path[0][1], self.path[0][0])
                    self.next_tile_cords = (((self.path[0][1]) + 0.5) * TILE_WIDTH, ((self.path[0][0]) + 0.5) * TILE_HEIGHT)

            # само передвижение в направлении нужной клетки и смена направления изображения
            if self.next_tile[0] - self.current_cell[0] == -1:
                self.current_direction = "left"
                self.horizontal_speed = -SPEED
                self.vertical_speed = 0

            elif self.next_tile[0] - self.current_cell[0] == 1:
                self.current_direction = "right"
                self.horizontal_speed = SPEED
                self.vertical_speed = 0

            if self.next_tile[1] - self.current_cell[1] == -1:
                self.current_direction = "up"
                self.vertical_speed = -SPEED
                self.horizontal_speed = 0

            elif self.next_tile[1] - self.current_cell[1] == 1:
                self.current_direction = "down"
                self.vertical_speed = SPEED
                self.horizontal_speed = 0

            self.rect.x += self.horizontal_speed
            self.rect.y += self.vertical_speed

        else: # если текущий центр робота в бане, остановится
            self.vertical_speed = 0
            self.horizontal_speed = 0

        self.animation()
        self.try_to_shoot(player_x, player_y, bullets_group)
        self.collide(bullets_group)

    def next_tile_in_way(self, target_cell, my_cell, lvl_map):
        """функция определения маршрута от клетки робота до цели по алгоритму A*"""
        if target_cell == my_cell:
            return "same tile"
        path_board = copy.deepcopy(lvl_map)
        curr_cords = (my_cell[1], my_cell[0])
        open_list = []
        closed_list = []
        collected_cords = [curr_cords]
        while curr_cords != (target_cell[1], target_cell[0]):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue
                    if (curr_cords[0] + dy, curr_cords[1] + dx) in closed_list:
                        continue
                    if curr_cords[1] + dx < 0 or curr_cords[1] + dx >= len(lvl_map[0]) or curr_cords[0] + dy < 0 or curr_cords[0] + dy >= len(lvl_map):
                        continue
                    if (path_board[curr_cords[0] + dy][curr_cords[1] + dx] in ("#", "s", ".") # преградами считаются стены и турели ( + пустоты во избежание ошибок)
                            and (curr_cords[0] + dy, curr_cords[1] + dx) != (target_cell[1], target_cell[0])):
                        continue
                    if dx == 0 or dy == 0:
                        if curr_cords == (my_cell[1], my_cell[0]):
                            len_to_start = 10
                        else:
                            len_to_start = 10 + path_board[curr_cords[0]][curr_cords[1]][0]
                    else:
                        continue
                    finish_weight = (abs(curr_cords[0] + dy - target_cell[1]) + abs(curr_cords[1] + dx - target_cell[0])) * 10
                    parent_cell = curr_cords
                    if (curr_cords[0] + dy, curr_cords[1] + dx) in open_list and path_board[curr_cords[0] + dy][curr_cords[1] + dx][0] > len_to_start:
                        path_board[curr_cords[0] + dy][curr_cords[1] + dx][0] = len_to_start
                        path_board[curr_cords[0] + dy][curr_cords[1] + dx][2] = parent_cell

                    if (curr_cords[0] + dy, curr_cords[1] + dx) not in open_list:
                        path_board[curr_cords[0] + dy][curr_cords[1] + dx] = [len_to_start, finish_weight, parent_cell]
                        open_list.append((curr_cords[0] + dy, curr_cords[1] + dx))
            if not open_list:
                return False
            less_weight = 0
            next_cords = ()
            for cords in open_list:
                if not less_weight:
                    less_weight = path_board[cords[0]][cords[1]][0] + path_board[cords[0]][cords[1]][1]
                    next_cords = cords
                    continue
                if (path_board[cords[0]][cords[1]][0] + path_board[cords[0]][cords[1]][1]) < less_weight:
                    less_weight = path_board[cords[0]][cords[1]][0] + path_board[cords[0]][cords[1]][1]
                    next_cords = cords
            closed_list.append(curr_cords)
            curr_cords = next_cords
            open_list.remove(curr_cords)
            collected_cords.append(curr_cords)
        path_cells = [(target_cell[1], target_cell[0])]
        parent = path_board[target_cell[1]][target_cell[0]][2]
        while parent != (my_cell[1], my_cell[0]):
            path_cells.append(parent)
            parent = path_board[parent[0]][parent[1]][2]
        self.path = path_cells[::-1]
        return True

    def collide(self, bullets_group):
        """проверка на столкновение с пулями игрока"""
        for i in bullets_group:
            if pygame.sprite.collide_rect(self, i) and i.sender == "player":
                self.health -= i.damage
                i.kill()
                self.damaged = True
                if self.health <= 0:
                    self.is_dead = True
                    self.image = load_image("scout_files/dead_scout_v1.png")
                    self.rect = self.image.get_rect()
                    self.rect.center = (self.current_cell[0] * TILE_WIDTH + 0.5 * TILE_WIDTH,
                                        self.current_cell[1] * TILE_HEIGHT + 0.5 * TILE_HEIGHT)

    def try_to_shoot(self, player_x, player_y, bullets_group):
        """функция стрельбы"""
        if not self.player_found:
            return
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_shoot_time < self.period:
            return
        if (abs(player_x - self.rect.centerx) ** 2 + abs(player_y - self.rect.centery) ** 2) ** 0.5 <= RADIOUS:
            self.can_shoot = True
            angle = math.degrees(math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx))
            # выпускает три пули: одну точно по центру игрока, другие с отклонениями в 10 градусов
            Bullet("bullets/bullet_temp.png", angle, self.rect.center, 5, DAMAGE, "enemy", bullets_group)
            Bullet("bullets/bullet_temp.png", angle + 10, self.rect.center, 5, DAMAGE, "enemy", bullets_group)
            Bullet("bullets/bullet_temp.png", angle - 10, self.rect.center, 5, DAMAGE, "enemy", bullets_group)
            self.last_shoot_time = curr_time
            return
        self.can_shoot = False

    def animation(self):
        """функция анимации"""
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_anim_update >= ANIMATION_DELAY:
            if self.damaged:  # если был ранен, поставить соответствующее изображение и поставить этот флаг в False
                self.image = load_image(f"scout_files/damaged/{self.current_direction}.png")
                self.damaged = False
            elif self.can_shoot:
                self.image = self.directions[self.current_direction][1][self.curr_frame]
            else:
                self.image = self.directions[self.current_direction][0][self.curr_frame]
            self.curr_frame = (self.curr_frame + 1) % 4
            self.last_anim_update = curr_time


