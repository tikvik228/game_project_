import pygame
from load_image import load_image
from tiles import TILE_WIDTH, TILE_HEIGHT
from bullet import Bullet
from random import randint
import copy
import math
WIDTH = 31
HEIGHT = 50
SPEED = 4
DAMAGE = 5
RADIOUS = TILE_HEIGHT * 2

class Scout(pygame.sprite.Sprite):

    def __init__(self, x_tile, y_tile, x_tile_default, y_tile_default, *group):
        super().__init__(*group)
        self.image = load_image("scout_v1.png")
        self.rect = self.image.get_rect()
        self.rect.center = x_tile * TILE_WIDTH + 0.5 * TILE_WIDTH, y_tile * TILE_HEIGHT + 0.5 * TILE_HEIGHT
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.period = randint(700, 1000)
        self.current_cell = x_tile, y_tile
        self.last_shoot_time = -self.period
        self.path = None
        self.next_tile_cords = self.rect.center
        self.next_tile = self.current_cell
        self.begin_cell = x_tile, y_tile
        self.default_cell = x_tile_default, y_tile_default
        self.player_found = False
        self.what_direction = self.default_cell
        self.health = 50

    def define_your_current_tile(self, floor_group):
        for i in floor_group:
            if i.rect.collidepoint(self.rect.centerx, self.rect.centery):
                self.current_cell = i.x_cell, i.y_cell

    def update(self, player_x, player_y, player_cell, map, floor_group, walls_group, level1_entities, bullets_group):
        self.define_your_current_tile(floor_group)
        check = self.next_tile_in_way(player_cell, map)
        if not check:
            return
        if not self.player_found:
            if len(self.path) > 4:
                if (((self.what_direction[0]) + 0.5) * TILE_WIDTH, ((self.what_direction[1]) + 0.5) * TILE_HEIGHT) == self.rect.center:
                    if self.what_direction == self.default_cell:
                        self.what_direction = self.begin_cell
                    else:
                        self.what_direction = self.default_cell
                self.next_tile_in_way(self.what_direction, map)
            else:
                self.player_found = True

        ban = (((player_cell[0] - 0.5) * TILE_WIDTH, (player_cell[1] + 0.5) * TILE_HEIGHT), ((player_cell[0] + 1.5) * TILE_WIDTH, (player_cell[1] + 0.5) * TILE_HEIGHT),
               ((player_cell[0] + 0.5) * TILE_WIDTH, (player_cell[1] - 0.5) * TILE_HEIGHT), ((player_cell[0] + 0.5) * TILE_WIDTH, (player_cell[1] + 1.5) * TILE_HEIGHT))
        if self.rect.center not in ban:
            #print("you can move")
            if (int(self.next_tile_cords[0]), int(self.next_tile_cords[1])) == self.rect.center:
                #print("came")
                self.horizontal_speed = 0
                self.vertical_speed = 0
                #if not self.shoot_check(player_x, player_y):
                #print(self.path)
                yes = True
                for other in level1_entities:
                    if other.next_tile == (self.path[0][1], self.path[0][0]) and other != self:
                        yes = False
                if yes:
                    self.next_tile = (self.path[0][1], self.path[0][0])
                    self.next_tile_cords = (((self.path[0][1]) + 0.5) * TILE_WIDTH, ((self.path[0][0]) + 0.5) * TILE_HEIGHT)

            #print(self.next_tile, self.current_cell, self.next_tile_cords, self.rect.center)
            if self.next_tile[0] - self.current_cell[0] == -1:
                #print("left")
                self.horizontal_speed = -SPEED
                self.vertical_speed = 0
            elif self.next_tile[0] - self.current_cell[0] == 1:
                #print("right")
                self.horizontal_speed = SPEED
                self.vertical_speed = 0
            if self.next_tile[1] - self.current_cell[1] == -1:
                #print("up")
                self.vertical_speed = -SPEED
                self.horizontal_speed = 0
            elif self.next_tile[1] - self.current_cell[1] == 1:
                #print("down")
                self.vertical_speed = SPEED
                self.horizontal_speed = 0

            #res = self.collide(walls_group)
            #if res == 3:
            self.rect.x += self.horizontal_speed
            self.rect.y += self.vertical_speed
            #if res == 2:
                #self.rect.x += self.horizontal_speed
            #if res == 1:
                #self.rect.y += self.vertical_speed
        else:
            self.vertical_speed = 0
            self.horizontal_speed = 0
        self.shoot_check(player_x, player_y)
        self.collide(bullets_group)


    def next_tile_in_way(self, player_cell, map):
        if player_cell == self.current_cell:
            #print("same tile")
            return "same tile"
        path_board = copy.deepcopy(map)
        curr_cords = (self.current_cell[1], self.current_cell[0])
        open_list = []
        closed_list = []
        collected_cords = [curr_cords]
        while curr_cords != (player_cell[1], player_cell[0]):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue
                    if (curr_cords[0] + dy, curr_cords[1] + dx) in closed_list:
                        continue
                    if curr_cords[1] + dx < 0 or curr_cords[1] + dx >= len(map[0]) or curr_cords[0] + dy < 0 or curr_cords[0] + dy >= len(map):
                        continue
                    if (path_board[curr_cords[0] + dy][curr_cords[1] + dx] != "-"
                            and (curr_cords[0] + dy, curr_cords[1] + dx) != (player_cell[1], player_cell[0])):
                        continue
                    if dx == 0 or dy == 0:
                        if curr_cords == (self.current_cell[1], self.current_cell[0]):
                            len_to_start = 10
                        else:
                            len_to_start = 10 + path_board[curr_cords[0]][curr_cords[1]][0]
                    else:
                        continue
                    finish_weight = (abs(curr_cords[0] + dy - player_cell[1]) + abs(curr_cords[1] + dx - player_cell[0])) * 10
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
        path_cells = [(player_cell[1], player_cell[0])]
        parent = path_board[player_cell[1]][player_cell[0]][2]
        while parent != (self.current_cell[1], self.current_cell[0]):
            path_cells.append(parent)
            parent = path_board[parent[0]][parent[1]][2]
        self.path = path_cells[::-1]
        return True

    def collide(self, bullets_group):
        for i in bullets_group:
            if pygame.sprite.collide_rect(self, i) and i.sender == "player":
                self.health -= i.damage
                i.kill()
                if self.health <= 0:
                    self.kill()

    def shoot_check(self, player_x, player_y):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_shoot_time < self.period:
            return False
        if (abs(player_x - self.rect.centerx) ** 2 + abs(player_y - self.rect.centery) ** 2) ** 0.5 <= RADIOUS:
            angle = math.degrees(math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx))
            Bullet("bullet_temp.png", angle, self.rect.center, 5, DAMAGE, "enemy")
            Bullet("bullet_temp.png", angle + 10, self.rect.center, 5, DAMAGE, "enemy")
            Bullet("bullet_temp.png", angle - 10, self.rect.center, 5, DAMAGE, "enemy")
            self.last_shoot_time = curr_time
            #self.period = randint(700, 1000)
            return True
        return False

