import pygame
from load_image import load_image
from tiles import *
from player import *



width, height = 800, 600
screen = pygame.display.set_mode((width, height))
menu_background = load_image("temporary_menu_background.png")


class levelOneButton(pygame.sprite.Sprite):

    def __init__(self, *group):
        super().__init__(*group)
        self.image_default = load_image("level1_button.png")
        self.image_pointed = load_image("level1_button_pointed.png")
        self.image = self.image_default
        self.rect = self.image.get_rect()
        self.rect.x = 418
        self.rect.y = 368

    def update(self, *args):
        if args and self.rect.collidepoint(args[0]):
            self.image = self.image_pointed
        else:
            self.image = self.image_default


class levelTwoButton(pygame.sprite.Sprite):

    def __init__(self, *group):
        super().__init__(*group)
        self.image_default = load_image("level2_button.png")
        self.image_pointed = load_image("level2_button_pointed.png")
        self.image = self.image_default
        self.rect = self.image.get_rect()
        self.rect.x = 568
        self.rect.y = 368

    def update(self, *args):
        if args and self.rect.collidepoint(args[0]):
            self.image = self.image_pointed
        else:
            self.image = self.image_default



def main():
    pygame.init()
    pygame.display.set_caption("названия нет")
    screen.fill("black")
    menu_sprites = pygame.sprite.Group()
    one = levelOneButton(menu_sprites)
    two = levelTwoButton(menu_sprites)
    level1_passed = False

    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        screen.blit(menu_background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and one.rect.collidepoint(event.pos):
                if not level1():
                    running = False
                level1_passed = True
            if event.type == pygame.MOUSEBUTTONDOWN and two.rect.collidepoint(event.pos) and level1_passed:
                if not level2():
                    running = False
        menu_sprites.draw(screen)
        menu_sprites.update(pygame.mouse.get_pos())
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()


def level1():
    level1_entities = pygame.sprite.Group() # пока пустая группа
    hero_group = pygame.sprite.Group()
    level1_map = [[0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
              [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
              [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
              [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1],
              [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1],
              [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
              [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
              [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]
    walls_group = pygame.sprite.Group()
    floor_group = pygame.sprite.Group()
    for numr, row in enumerate(level1_map): # вся строка
        for numc, col in enumerate(row): # каждый символ
            print(numc, numr)
            if col:
                Wall(numc, numr, walls_group)
            else:
                Floor(numc, numr, floor_group)
    hero = Player(0, 1, hero_group)
    running = True
    move_left = move_right = move_up = move_down = False
    image_direction = "down"
    fps = 60
    clock = pygame.time.Clock()
    while running:
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and end_level1.collidepoint(event.pos):
                running = False

            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                move_down = True
                move_up = False
                image_direction = "down"
            elif key[pygame.K_UP]:
                move_up = True
                move_down = False
                image_direction = "up"
            else:
                move_up = move_down = False
            if key[pygame.K_RIGHT]:
                move_right = True
                move_left = False
                image_direction = "right"
            elif key[pygame.K_LEFT]:
                move_left = True
                move_right = False
                image_direction = "left"
            else:
                move_left = move_right = False
        walls_group.draw(screen)
        floor_group.draw(screen)
        hero_group.draw(screen)
        hero.update(move_left, move_right, move_up, move_down, image_direction, walls_group, floor_group)
        level1_entities.draw(screen)

        end_level1 = pygame.draw.rect(screen, "red", (10, 10, 20, 20))  # заглушка
        font = pygame.font.Font(None, 24)
        text_surface = font.render("<--", True, "white")
        screen.blit(text_surface, (10, 10))
        #level1_entities.update()
        clock.tick(fps)
        pygame.display.flip()
    return True


def level2():
    level2_sprites = pygame.sprite.Group()  # пока пустая группа

    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        screen.fill("black")
        end_level1 = pygame.draw.rect(screen, "red", (300, 200, 200, 100)) #
        font = pygame.font.Font(None, 23)
        text_surface = font.render("Выйти из второго уровня", True, "white")
        screen.blit(text_surface, (305, 240))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and end_level1.collidepoint(event.pos):
                running = False
        level2_sprites.draw(screen)
        level2_sprites.update()
        clock.tick(fps)
        pygame.display.flip()
    return True


if __name__ == '__main__':
    main()