import math
import pygame
from load_image import load_image

bullets_group = pygame.sprite.Group()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img, angle, pos, speed, damage):
        super().__init__(bullets_group)
        self.image = load_image(img)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = speed
        self.damage = damage
        self.angle = angle

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, 180 - self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)

    def update(self, walls_group):
        # перемещаем пулю по траектории
        self.rect.x += round(self.speed * math.cos(math.radians(self.angle)))
        self.rect.y += round(self.speed * math.sin(math.radians(self.angle)))

        if pygame.sprite.spritecollideany(self, walls_group):
            self.kill()