import pygame
from load_image import load_image
from constants import TILE_WIDTH, TILE_HEIGHT
from bullet import Bullet
import math
SPEED = 10
DAMAGE = 5
RADIOUS = TILE_HEIGHT * 6
ANIMATION_DELAY = 50
ANIMATION_ORIG = [('sentry_files/sentry1.png'),
            ('sentry_files/sentry2.png'),
            ('sentry_files/sentry3.png'),
            ('sentry_files/sentry4.png'),
            ('sentry_files/sentry5.png'),
            ('sentry_files/sentry6.png'),
            ('sentry_files/sentry7.png'),
            ('sentry_files/sentry8.png'),
            ('sentry_files/sentry9.png'),
            ('sentry_files/sentry10.png')]


class Ray(pygame.sprite.Sprite):
    def __init__(self, cords, length, angle, group):
        # в инит принимается длина луча, угол поворота и координаты центра турели, откуда исходит луч
        super().__init__(group)
        self.main_image = load_image("sentry_files/ray.png")
        self.image = self.main_image.copy()
        self.angle = angle
        self.length = length
        self.rect = self.image.get_rect()
        self.rect.center = cords
        self.cords = cords
        self.mask = pygame.mask.from_surface(self.image)
        self.invisible = True  # флаг видимости/ невидимости луча

    def update(self, length, angle):
        self.length = length
        self.angle = angle

        # удлиняем изображение
        len_img = pygame.transform.scale(self.main_image, (self.length, self.main_image.get_height()))
        # создаем прозрачную поверхность в два раза большую чем луч и накладываем его на эту поверхность,
        # это нужно для вращения луча не вокруг своего центра, а вокруг крайней точки
        pos_of_rotate = (len_img.get_width(), len_img.get_height() / 2)
        w, h = len_img.get_size()
        new_img = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
        new_img.blit(len_img, (w - pos_of_rotate[0], h - pos_of_rotate[1]))

        new_img = pygame.transform.rotate(new_img, 180 - self.angle) # поворот нового изображения
        if self.invisible: # скрыть / не скрывать луч
            new_img.set_alpha(0)
        else:
            new_img.set_alpha(90)
        rect = new_img.get_rect()
        rect.center = self.cords  # устанавливаем центр нового изображения в центр турели
        self.rect = rect
        self.image = new_img
        self.mask = pygame.mask.from_surface(new_img)


class Sentry(pygame.sprite.Sprite):
    def __init__(self, ray_group, x_tile, y_tile, *group):
        super().__init__(*group)
        self.frames = []
        for num in range(1, 11):
            self.frames.append(load_image(f"sentry_files/sentry{num}.png"))
        self.sentry_image = self.frames[0]
        self.base = load_image(f"sentry_files/sentrys_base.png")  # основа с тенью размером с клетку (64х64)
        self.image = self.base.copy()  # изображение, на которое будет накладываться картинка турели
        self.rect = self.image.get_rect()
        self.rect.center = x_tile * TILE_WIDTH + 0.5 * TILE_WIDTH, y_tile * TILE_HEIGHT + 0.5 * TILE_HEIGHT
        self.current_cell = x_tile, y_tile
        self.health = 80
        self.is_dead = False
        self.ray = None
        self.ray_group = ray_group
        self.can_shoot = False
        self.angle = 0
        self.last_update_rotate = pygame.time.get_ticks()
        self.rot_speed = 8

        self.period = 300 # период между выстрелами
        self.last_shoot_time = -self.period

        self.last_anim_update = pygame.time.get_ticks()
        self.curr_frame = 0  # текущий кадр анимации

        self.check = True  # флаг есть стены между игроком и турелью / нет стен

    def update(self, player_x, player_y, walls_group, bullets_group):
        if self.is_dead:  # после смерти никакой обработки не происходит
            return
        self.animation()
        rad = (abs(player_x - self.rect.centerx) ** 2 + abs(player_y - self.rect.centery) ** 2) ** 0.5  # расстояние между игроком и турелью
        angle = math.degrees(math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx)) # угол между ними
        if rad <= RADIOUS:
            if not self.ray: # создать луч если еще не был создан
                self.ray = Ray(self.rect.center, rad, angle, self.ray_group)
            self.ray.update(rad, angle)
            self.check = any(pygame.sprite.collide_mask(i, self.ray) for i in walls_group)  # проверка на коллид луча со стенами
            if self.check:  # если пересекается, скрыть луч, поставить обычную картинку, двигаться как обычно
                self.can_shoot = False
                self.curr_frame = 0
                self.ray.invisible = True
                self.rotate("left")
            else:
                self.ray.invisible = False
                if angle <= 0:  # преобразование в градусы от 0 до 360
                    need_angle = -1 * angle
                else:
                    need_angle = 360 - angle

                # выбираем, как быстрее повернуться: сравниваем просто разность и сложение расстояний до 0
                if abs(need_angle - self.angle) < min((need_angle, self.angle)) + 360 - max((need_angle, self.angle)):
                    # так как турель поворачивается на определенное количество градусов за раз, попасть точно в градус
                    # игрока не получится. Поэтому турель считает нужным поворачиваться дальше только если разница в
                    # уменьшится, а не пока градусы совпадут.
                    if need_angle > self.angle and abs(self.angle + self.rot_speed - need_angle) < abs(self.angle - need_angle):
                        self.can_shoot = False
                        self.rotate("left")
                    elif need_angle < self.angle and abs(self.angle - self.rot_speed - need_angle) < abs(self.angle - need_angle):
                        self.can_shoot = False
                        self.rotate("right")
                    else:
                        self.can_shoot = True
                        if self.curr_frame == 7:  # если текущий кадр - стреляющая турель
                            self.try_to_shoot(bullets_group, angle)
                else:
                    if need_angle > self.angle and abs(self.angle + self.rot_speed - need_angle) < abs(self.angle - need_angle):
                        self.can_shoot = False
                        self.rotate("right")
                    elif need_angle < self.angle and abs(self.angle - self.rot_speed - need_angle) < abs(self.angle - need_angle):
                        self.can_shoot = False
                        self.rotate("left")
                    else:
                        self.can_shoot = True
                        if self.curr_frame == 7:
                            self.try_to_shoot(bullets_group, angle)
        else: # если игрок ушел из радиуса поражения, убрать луч, поставить обычное изображение и просто вращаться
            self.can_shoot = False
            self.curr_frame = 0
            self.rotate("left")
            if self.ray:
                self.ray.kill()
            self.ray = None
        self.collide(bullets_group)

    def try_to_shoot(self, bullets_group, angle):
        """функция стрельбы"""
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_shoot_time < self.period:
            return
        Bullet("bullets/sentrys_bullet.png", angle + 5, self.rect.center, SPEED, DAMAGE, "enemy", bullets_group)
        Bullet("bullets/sentrys_bullet.png", angle - 5, self.rect.center, SPEED, DAMAGE, "enemy", bullets_group)
        self.last_shoot_time = curr_time

    def rotate(self, direction):
        """функция, изменяющая self.angle"""
        now = pygame.time.get_ticks()
        if now - self.last_update_rotate > 50:
            self.last_update_rotate = now
            if direction == "right":
                self.angle = (self.angle - self.rot_speed) % 360
            else:
                self.angle = (self.angle + self.rot_speed) % 360

    def animation(self):
        """анимация турели"""
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_anim_update >= ANIMATION_DELAY:
            self.image = self.base.copy()  # self.image очищается
            new_img = pygame.transform.rotate(self.frames[self.curr_frame], self.angle) # нужное изображение поворачивается
            rect = new_img.get_rect(center=self.rect.center)
            self.image.blit(new_img, (rect.left - self.rect.left, rect.top - self.rect.top))  # накладывается на self.image

            # если ведется стрельба, или велась только что (игрок ушел с нужного угла, стрельба прервалась,
            # но изображение процесса стрельбы осталось), то переключить кадр на следующий
            if (not self.can_shoot and self.curr_frame != 0) or self.can_shoot:
                self.curr_frame = (self.curr_frame + 1) % len(self.frames)
            self.last_anim_update = curr_time

    def collide(self, bullets_group):
        """проверка пересечений с пулями"""
        for i in bullets_group:
            if pygame.sprite.collide_rect(self, i) and i.sender == "player":
                self.health -= i.damage
                i.kill()
                if self.health <= 0:
                    self.is_dead = True
                    if self.ray:
                        self.ray.kill()
                        self.ray = None
                        self.image = self.base.copy()
                        new_img = pygame.transform.rotate(load_image("sentry_files/killed_sentry.png"), self.angle)
                        rect = new_img.get_rect(center=self.rect.center)
                        self.image.blit(new_img, (rect.left - self.rect.left, rect.top - self.rect.top))