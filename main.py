import pygame
from load_image import load_image
from tiles import *
from player import *
from scout import *
from bullet import *
from inventory import *
from gun import *
from random import randint



width, height = 800, 600
screen = pygame.display.set_mode((width, height))
menu_background = load_image("temporary_menu_background.png")


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+width / 2, -t+height / 2

    l = min(0, l)                           # Не движемся дальше левой границы
    l = max(-(camera.width-width), l)   # Не движемся дальше правой границы
    t = max(-(camera.height-height), t) # Не движемся дальше нижней границы
    t = min(0, t)                           # Не движемся дальше верхней границы

    return pygame.Rect(l, t, w, h)
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
    all_level1_sprites = pygame.sprite.Group()
    level1_entities = pygame.sprite.Group() # пока пустая группа
    hero_group = pygame.sprite.Group()
    guns_group = pygame.sprite.Group()
    with open("data/level1.txt", 'r') as map:
        level1_map = []
        for i in map:
            level1_map.append(list(i.strip()))
    walls_group = pygame.sprite.Group()
    floor_group = pygame.sprite.Group()
    for numr, row in enumerate(level1_map): # вся строка
        for numc, col in enumerate(row): # каждый символ
            if col == "#":
                Wall(numc, numr, walls_group, all_level1_sprites)
            elif col == "-":
                Floor(numc, numr, floor_group, all_level1_sprites)
    hero = Player(6, 1, hero_group, all_level1_sprites)

    pist = Gun(all_equipment["pistol"]["name"], all_equipment["pistol"]["image"], 10, 2, guns_group, all_level1_sprites)
    shotgun = Gun(all_equipment["shotgun"]["name"], all_equipment["shotgun"]["image"], 17, 15, guns_group, all_level1_sprites)


    Scout(20, 19, 6, 19, level1_entities, all_level1_sprites)
    Scout(1, 6, 8, 12, level1_entities, all_level1_sprites)
    Scout(12, 6, 14, 13, level1_entities, all_level1_sprites)

    hero_inv = Inventory()
    print(level1_map)
    total_level_width = len(level1_map[0]) * TILE_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level1_map) * TILE_HEIGHT  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)
    running = True
    move_left = move_right = move_up = move_down = False
    show_inventory = False
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
            if key[pygame.K_s]:
                move_down = True
                move_up = False
                image_direction = "down"
            elif key[pygame.K_w]:
                move_up = True
                move_down = False
                image_direction = "up"
            else:
                move_up = move_down = False
            if key[pygame.K_d]:
                move_right = True
                move_left = False
                image_direction = "right"
            elif key[pygame.K_a]:
                move_left = True
                move_right = False
                image_direction = "left"
            else:
                move_left = move_right = False

            if key[pygame.K_TAB]:
                show_inventory = True
            else:
                show_inventory = False
            inv_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                        pygame.K_8, pygame.K_9, pygame.K_0]
            for k in inv_keys:
                if key[k]:
                    hero.change_inv_cell(hero_inv, inv_keys.index(k))
                    hero_inv.selected_cell = inv_keys.index(k)
                    hero_inv.draw_operator(screen, show_inventory, 2000)

            if event.type == pygame.MOUSEBUTTONDOWN:
                hero.try_to_shoot(hero_inv)

        #walls_group.draw(screen)
        #floor_group.draw(screen)

        #hero_group.draw(screen)
        hero.update(move_left, move_right, move_up, move_down, image_direction, walls_group, floor_group, bullets_group)
        level1_entities.update(*hero.rect.center, hero.current_cell, level1_map, floor_group, walls_group, level1_entities, bullets_group)
        camera.update(hero)
        # обновляем положение всех спрайтов
        for e in all_level1_sprites:
            screen.blit(e.image, camera.apply(e))
        for bul in bullets_group:
            bul.draw(screen, camera.state.topleft)
        bullets_group.update(walls_group)

        hero_inv.draw_operator(screen, show_inventory, 0)

        for gun in guns_group:
            if hero.rect.colliderect(gun.rect):
                hero_inv.add_to_inventory(gun.name)
                hero_inv.draw_operator(screen, show_inventory, 2000)
                gun.kill()
        #hero_inv.draw_inventory(screen)
        #for sprite in bullets_group:
        #    sprite.draw(screen)
        #bullets_group.update(walls_group)

        #level1_entities.draw(screen)
        #level1_entities.update(*hero.rect.center, hero.current_cell, level1_map, floor_group, walls_group)

        end_level1 = pygame.draw.rect(screen, "red", (10, 10, 20, 20))  # заглушка
        font = pygame.font.Font(None, 24)
        text_surface = font.render("<--", True, "white")
        screen.blit(text_surface, (10, 10))

        end_level1 = pygame.draw.rect(screen, "red", (750, 10,30, 20))  # заглушка
        font = pygame.font.Font(None, 24)
        text_surface = font.render(str(hero.health), True, "white")
        screen.blit(text_surface, (750, 10))
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