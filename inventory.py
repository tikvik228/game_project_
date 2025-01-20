import pygame
from load_image import load_image
from random import randint


all_equipment = {"pistol": {"name": "pistol",
                            "image": "pistol.png",
                            "skin_directory": "player_pistol",
                            "bullet_image": "bullet_temp.png",
                            "bullet_damage": 10},
                 "shotgun": {"name": "shotgun",
                             "image": "shotgun.png",
                             "skin_directory": "player_shotgun",
                             "bullet_image": "bullet_temp.png",
                             "bullet_damage": 25}}

class Inventory():
    def __init__(self):
        self.inv = [None] * 10
        self.cell_image = ""
        self.pointed_cell_image = ""
        self.border_image = ""
        self.begin_time = 0
        self.period = 0
        self.selected_cell = None

    def add_to_inventory(self, weapon):
        for num, i in enumerate(self.inv):
            if i is None:
                print(weapon)
                self.inv[num] = [weapon, randint(0, 12)]
                break
        print(self.inv)

    def draw_operator(self, screen, can_show_tab, time):
        if can_show_tab:
            self.draw_inventory(screen)
            self.begin_time = 0
            self.period = 0
            return

        if time:
            self.begin_time = pygame.time.get_ticks()
            self.period = time

        if not can_show_tab:
            if self.period:
                if pygame.time.get_ticks() <= self.begin_time + self.period:
                    self.draw_inventory(screen)
                else:
                    self.begin_time = 0
                    self.period = 0

    def draw_inventory(self, screen):
        for i in range(len(self.inv)):
            pygame.draw.rect(screen, (255, 255, 255), (151 + i * 48 + i * 2, 530, 48, 48))
            if i == self.selected_cell:
                pygame.draw.rect(screen, (0, 0, 0), (151 + i * 48 + i * 2, 530, 48, 48), width=2)
            if self.inv[i] is not None:
                img = load_image(all_equipment[self.inv[i][0]]["image"])
                screen.blit(img, (151 + i * 48 + i * 2 + ((48 - img.get_width()) // 2), 530 + ((48 - img.get_height()) // 2) , img.get_width(), img.get_height()))

                font = pygame.font.Font(None, 20)
                text_surface = font.render(str(self.inv[i][1]), True, "black")
                screen.blit(text_surface, (151 + i * 48 + i * 2 + 5, 560))