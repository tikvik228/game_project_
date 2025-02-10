import math
import pygame
from load_image import load_image


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img, angle, pos, speed, damage, sender, group):
        super().__init__(group)
        self.angle = angle
        self.image = pygame.transform.rotate(load_image(img), 180 - self.angle)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.damage = damage
        self.sender = sender  # отправитель пули -  player/enemy

    def update(self, walls_group):  # перемещение пули по траектории
        self.rect.x += round(self.speed * math.cos(math.radians(self.angle)))
        self.rect.y += round(self.speed * math.sin(math.radians(self.angle)))
        if pygame.sprite.spritecollideany(self, walls_group):
            self.kill()