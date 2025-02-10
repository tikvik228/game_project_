import pygame
from load_image import load_image
from constants import TILE_WIDTH, TILE_HEIGHT
from random import randint


class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.frames = []
        for num in range(1, 9):
            self.frames.append(load_image(f"ammo_files/ammo{num}.png"))
        self.curr_frame = 0
        self.image = self.frames[self.curr_frame]
        self.rect = self.image.get_rect()
        self.rect.center = x * TILE_WIDTH + 0.5 * TILE_WIDTH, y * TILE_HEIGHT + 0.5 * TILE_HEIGHT
        self.x_cell = x
        self.y_cell = y
        self.last_anim_update = pygame.time.get_ticks()
        self.animation_delay = 100

    def update(self):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_anim_update >= self.animation_delay:
            self.curr_frame = (self.curr_frame + 1) % len(self.frames)
            self.image = self.frames[self.curr_frame]
            self.last_anim_update = curr_time


class MediKit(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.frames = []
        for num in range(1, 13):
            self.frames.append(load_image(f"medikit_files/kit{num}.png"))
        self.curr_frame = 0
        self.image = self.frames[self.curr_frame]
        self.rect = self.image.get_rect()
        self.rect.center = x * TILE_WIDTH + 0.5 * TILE_WIDTH, y * TILE_HEIGHT + 0.5 * TILE_HEIGHT
        self.x_cell = x
        self.y_cell = y
        self.last_anim_update = pygame.time.get_ticks()
        self.animation_delay = 100
        self.regen = randint(25, 50)

    def update(self, hero):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.last_anim_update >= self.animation_delay:
            self.curr_frame = (self.curr_frame + 1) % len(self.frames)
            self.image = self.frames[self.curr_frame]
            self.last_anim_update = curr_time

        if self.rect.colliderect(hero.rect):
            hero.health += self.regen
            self.kill()