import pygame
from load_image import load_image


class BackMenuButton(pygame.sprite.Sprite):
    """кнопка возврата в меню"""
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = load_image("buttons/Home.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class PauseButton(pygame.sprite.Sprite):
    """кнопка паузы"""
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = load_image("buttons/Pause.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

