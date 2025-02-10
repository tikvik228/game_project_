import pygame
import sys
import csv
from load_image import load_image
from tiles import Floor, Wall
from player import Player
from scout import Scout
from inventory import Inventory
from constants import *
from gun import Gun
from sentry import Sentry
from ammo_and_medikit import Ammo, MediKit
from interface_buttons import BackMenuButton, PauseButton
from random import randint


width, height = 800, 600
screen = pygame.display.set_mode((width, height))
menu_background = load_image("temporary_menu_background.png")

levels = ["level1.txt", "level2.txt", "level3.txt"]  # список с txt файлами уровней


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
    l = min(0, l)
    l = max(-(camera.width-width), l)
    t = max(-(camera.height-height), t)
    t = min(0, t)
    return pygame.Rect(l, t, w, h)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    pygame.display.set_caption("названия нет")
    screen.fill("black")
    menu_sprites = pygame.sprite.Group()
    font = pygame.font.Font("data/pixel_font.ttf", 24)  # создание шрифта
    new_game_line = font.render(f"Начать новую игру", True, "white")  # надпись новая игра
    continue_line = font.render(f"Продолжить", True, "white")  # надпись продолжить
    exit_line = font.render(f"Выход", True, "white")  # надпись выход

    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        screen.blit(menu_background, (0, 0))
        screen.blit(new_game_line, (500, 300))
        screen.blit(continue_line, (500, 350))
        screen.blit(exit_line, (500, 400))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and\
               pygame.Rect(500, 400, exit_line.get_width(), exit_line.get_height()).collidepoint(event.pos):
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and\
               pygame.Rect(500, 300, new_game_line.get_width(), new_game_line.get_height()).collidepoint(event.pos):
                # если была запущена новая игра
                with open('data/save.csv', 'w', newline='', encoding="utf8") as f:
                    pass # очистка
                for num, lvl_map in enumerate(levels):  # цикл карт
                    res = run_level(lvl_map, num + 1)  # передаем нужную карту и номер уровня
                    while res == "death":  # пока возврат равен смерти, перезапускать функцию с той же картой
                        res = run_level(lvl_map, num + 1)
                    if res == "leaved":  # выход из цикла при покидании игры
                        break
            if event.type == pygame.MOUSEBUTTONDOWN and\
               pygame.Rect(500, 350, continue_line.get_width(), continue_line.get_height()).collidepoint(event.pos):
                # если с сохранения
                current_level = 1
                with open('data/save.csv', 'r', newline='', encoding="utf8") as f:
                    if f.readlines():
                        f.seek(0)
                        reader = list(csv.DictReader(f, delimiter=';', quotechar='"'))
                        current_level = int(reader[0]["Номер уровня"]) + 1
                for lvl_map in levels[current_level - 1:]:  # запуск с уровня следующего за сохраненным
                    res = run_level(lvl_map, current_level)
                    while res == "death":
                        res = run_level(lvl_map, current_level)
                    if res == "leaved":
                        break
        menu_sprites.draw(screen)
        menu_sprites.update(pygame.mouse.get_pos())
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()


def load_map_file(file):
    """вспомогательная функция обработки файла карты,
    возвращает карту уровня, карту декораций, данные об оружии и точках роботов"""
    with open(f"data/levels/{file}", 'r') as f:
        level_map = []
        decorations_map = []
        weapon = []
        robots_points = []
        for i in f:
            if i.strip() == "DECORATIONS":
                break
            level_map.append(list(i.strip()))
        for line in f:
            if line.strip() == "WEAPON INFO":
                break
            decorations_map.append(list(line.strip()))
        for gun in f:
            if gun.strip() == "ROBOT POINTS":
                break
            weapon.append((gun.split()[0], int(gun.split()[1]), int(gun.split()[2])))
        for point in f:
            robots_points.append((tuple(map(int, point.split()[:2])), tuple(map(int, point.split()[2:]))))
        return level_map, decorations_map, weapon, robots_points


def run_level(file, lvl_number):
    """функция уровня"""
    ended = False

    level_interface = pygame.sprite.Group() # объявление групп
    level_entities = pygame.sprite.Group()
    level_dynamics = pygame.sprite.Group()
    level_statics = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    floor_group = pygame.sprite.Group()
    hero_group = pygame.sprite.Group()
    guns_group = pygame.sprite.Group()
    scouts = pygame.sprite.Group()
    sentries = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    ray_group = pygame.sprite.Group()
    ammo_group = pygame.sprite.Group()
    medikit_group = pygame.sprite.Group()

    back_to_menu = BackMenuButton(10, 10, level_interface)
    pause_button = PauseButton(62, 10, level_interface)

    level_map, decor_map, weapon, points = load_map_file(file)
    for numr, row in enumerate(level_map):  # вся строка
        for numc, col in enumerate(row):  # каждый символ
            if col == "#":  # стена
                Wall(numc, numr, decor_map, walls_group, level_statics)
            elif col == "-":  # пол
                Floor(numc, numr, decor_map, floor_group, level_statics)
            elif col == "@":  # конечная плитка
                end_tile = Floor(numc, numr, decor_map, floor_group, level_statics)
            elif col == "s":  # турель - sentry
                Sentry(ray_group, numc, numr, sentries, level_entities)
                Floor(numc, numr, decor_map, floor_group, level_statics)
            elif col == "p":  # игрок
                hero = Player(numc, numr, hero_group, level_entities)
                Floor(numc, numr, decor_map, floor_group, level_statics)
            elif col == "a":  # патроны
                Ammo(numc, numr, ammo_group, level_dynamics)
                Floor(numc, numr, decor_map, floor_group, level_statics)
            elif col == "m":  # аптечка
                MediKit(numc, numr, medikit_group, level_dynamics)
                Floor(numc, numr, decor_map, floor_group, level_statics)

    for w in weapon:
        # проверка на корректность координат оружия
        if w[2] < len(level_map) and w[1] < len(level_map[0]) and level_map[w[2]][w[1]] not in ("#", "s", ".") and\
           w[0] in all_equipment.keys():
            Gun(all_equipment[w[0]]["name"], all_equipment[w[0]]["image"], w[1], w[2], guns_group, level_dynamics)

    for sett in points:
        # проверка точек робота
        flag = False
        for pnt_coords in sett: # отдельно координаты начальной точки и точки по умолчанию
            if level_map[pnt_coords[1]][pnt_coords[0]] in ("#", "s", ".") or pnt_coords[0] >= len(level_map[0]) or\
               pnt_coords[1] >= len(level_map):
                flag = True
                break
        if not flag:
            Scout(sett[0][0], sett[0][1], sett[1][0], sett[1][1],  scouts, level_entities)

    hero_inv = Inventory()
    inv_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                pygame.K_8, pygame.K_9, pygame.K_0]

    # обработка предыдущего сохранения
    with open('data/save.csv', 'r', newline='', encoding="utf8") as f:
        reader = list(csv.DictReader(f, delimiter=';'))
        if reader:
            hero.health = int(reader[0]["здоровье"])
            for n in range(0, 10):
                cell = reader[0][f"ячейка {n}"]

                if cell:
                    hero_inv.add_to_inventory(reader[0][f"ячейка {n}"].split()[0], int(reader[0][f"ячейка {n}"].split()[1]))

    total_level_width = len(level_map[0]) * TILE_WIDTH  #ширина уровня
    total_level_height = len(level_map) * TILE_HEIGHT  # высота
    camera = Camera(camera_configure, total_level_width, total_level_height)

    entities_quantity = len(level_entities) - 1 # количество мобов на уровне не включая игрока
    dead = [] # список для умерших сущностей, обе переменные нужны для финальных подсчетов убитых мобов

    guns_quantity = len(guns_group) # тоже для финальных подсчетов

    running = True
    move_left = move_right = move_up = move_down = False
    show_inventory = False
    image_direction = "down"
    fps = 60
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    paused = False

    font = pygame.font.Font("data/pixel_font.ttf", 18)
    while running:
        if paused:  # проверка поставленной паузы
            screen.blit(font.render(f"Нажмите любую кнопку для продолжения", True, "white"),
                        (200, 200))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    paused = False
            pygame.display.flip()
        else:
            screen.fill("black")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and back_to_menu.rect.collidepoint(event.pos):
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and pause_button.rect.collidepoint(event.pos):
                    paused = True
                # обработка нажатий клавиш движения
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
                for k in inv_keys:
                    if key[k]: # если одна из клавиш инвентаря (123456780) была нажата
                        hero.change_inv_cell(hero_inv, inv_keys.index(k)) # обновить данные о выбранной ячейке у игрока
                        hero_inv.selected_cell = inv_keys.index(k)
                        hero_inv.draw_operator(screen, show_inventory, 2000)  # показать инвентарь на 2с

                if event.type == pygame.MOUSEBUTTONDOWN and pause_button.rect.collidepoint(event.pos) is False:
                    hero.try_to_shoot(hero_inv, bullets_group)

            if hero.is_dead:
                return "death"

            hero.update(move_left, move_right, move_up, move_down, image_direction, walls_group, bullets_group, sentries)
            scouts.update(*hero.rect.center, hero.current_cell, level_map, walls_group, scouts, bullets_group)
            sentries.update(*hero.rect.center, walls_group, bullets_group)

            camera.update(hero)

            medikit_group.update(hero)
            bullets_group.update(walls_group)

            # обновляем положение всех спрайтов
            for st in level_statics: # статики - пол, стены, мертвые мобы, отрисовываются раньше всех
                screen.blit(st.image, camera.apply(st))

            for d in level_dynamics: # за ними аптечки, патроны, оружие
                screen.blit(d.image, camera.apply(d))

            for bul in bullets_group: # потом отрисовка пуль
                screen.blit(bul.image, camera.apply(bul))

            for ray in ray_group: # потом лучи
                screen.blit(ray.image, camera.apply(ray))

            for e in level_entities:  # выше всех рисуются мобы и игрок
                # если только умер, создать на его месте патроны, и переместить из entities в statics
                if e.is_dead and e not in dead:
                    Ammo(*e.current_cell, ammo_group, level_dynamics)
                    dead.append(e)
                    level_statics.add(e)
                    level_entities.remove(e)
                screen.blit(e.image, camera.apply(e))

            hero_inv.draw_operator(screen, show_inventory, 0)

            for gun in guns_group:  # проверка перенесена в главный цикл из-за взаимодействий с инвентарем
                if hero.rect.colliderect(gun.rect):
                    hero_inv.add_to_inventory(gun.name, randint(1, all_equipment[gun.name]["ammo_quantity"]))
                    hero_inv.draw_operator(screen, show_inventory, 2000)
                    gun.kill()
            for am in ammo_group:  # тоже
                am.update()
                if hero.rect.colliderect(am.rect) and hero.curr_inv_pos is not None and hero_inv.inv[hero.curr_inv_pos] is not None:
                    hero_inv.inv[hero.curr_inv_pos][1] += all_equipment[hero_inv.inv[hero.curr_inv_pos][0]]["ammo_quantity"]
                    hero_inv.draw_operator(screen, show_inventory, 2000)
                    am.kill()

            level_interface.draw(screen)
            text_surface = font.render(f"Здоровье: {hero.health}", True, "white")
            screen.blit(text_surface, (660, 10))

            if end_tile.rect.colliderect(hero):
                # запись сохранения
                with open('data/save.csv', 'w', newline='', encoding="utf8") as f:
                    data = {"Номер уровня": lvl_number, "здоровье": hero.health}
                    for num, item in enumerate(hero_inv.inv):
                        if item:
                            data[f"ячейка {num}"] = item[0] + " " + str(item[1])
                        else:
                            data[f"ячейка {num}"] = item
                    writer = csv.DictWriter(
                        f, fieldnames=list(data.keys()),
                        delimiter=';', quoting=csv.QUOTE_NONE, quotechar='"')
                    writer.writeheader()
                    writer.writerow(data)
                ended = True
                running = False
            clock.tick(fps)
            pygame.display.flip()

    if ended:  # показ окна с результатами если уровень был пройден
        time = round((pygame.time.get_ticks() - start_time) / 1000)
        while ended:
            screen.fill("black")
            back = font.render("выйти в меню", True, "white")
            screen.blit(back, (500, 400))
            next_lvl = font.render("следующий уровень", True, "white")
            screen.blit(next_lvl, (500, 450))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(500, 400, back.get_width(),
                   back.get_height()).collidepoint(event.pos):
                    return "leaved"
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(500, 450, next_lvl.get_width(),
                   next_lvl.get_height()).collidepoint(event.pos):
                    return "next"
            text_surface = font.render(f"Уровень {lvl_number} пройден", True, "white")
            screen.blit(text_surface, (100, 150))
            text_surface = font.render(f"Время: {time // 60}мин {time % 60}с", True, "white")
            screen.blit(text_surface, (100, 200))
            text_surface = font.render(f"Врагов убито: {entities_quantity - len(level_entities) + 1} / {entities_quantity}",
                                       True, "white")
            screen.blit(text_surface, (100, 250))
            text_surface = font.render(f"Оружия подобрано: {guns_quantity - len(guns_group)} / {guns_quantity}",
                                       True, "white")
            screen.blit(text_surface, (100, 300))


            pygame.display.flip()

    return "leaved"


if __name__ == '__main__':
    main()