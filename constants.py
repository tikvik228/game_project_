# файл с общими константами в игре и словарем характеристик оружия

TILE_WIDTH = 64
TILE_HEIGHT = 64

# информация о всех оружиях в игре
all_equipment = {"pistol": {"name": "pistol",
                            "image": "weapon/pistol.png",
                            "skin_directory": "player_pistol",
                            "bullet_image": "bullets/pistol_bullet.png",
                            "bullet_damage": 10,
                            "bullet_speed": 5,
                            "ammo_quantity": 5},
                 "lasergun": {"name": "lasergun",
                              "image": "weapon/lasergun.png",
                              "skin_directory": "player_lasergun",
                              "bullet_image": "bullets/lasergun_bullet.png",
                              "bullet_speed": 10,
                              "bullet_damage": 18,
                              "ammo_quantity": 3},
                 "revolver": {"name": "revolver",
                              "image": "weapon/revolver.png",
                              "skin_directory": "player_revolver",
                              "bullet_image": "bullets/bullet_temp.png",
                              "bullet_speed": 4,
                              "bullet_damage": 15,
                              "ammo_quantity": 4}}
# здесь присутствует информация о револьвере, его изображение есть в файлах игры, но в самой игре он не появляется, тк
# анимации игрока с револьвером пока нет

