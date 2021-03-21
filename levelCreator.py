import pygame
from Enemy import Asteroid, FirstEnemy
import os
import random




class AbstractSpawner:
    def __init__(self, images: list, display_size: list, add_function, get_amount):
        self.images = images
        self.add_to_group = add_function
        self.display_size = display_size
        self.get_amount = get_amount
        self.run_spawn = True

    def switch(self):
        self.run_spawn = not self.run_spawn


class AsteroidSpawner(AbstractSpawner):
    cooldawn = 1900
    min_cooldawn = 880
    max_cooldawn = 1500

    def __init__(self, images: list, display_size: list, add_function, get_amount):
        super().__init__(images, display_size, add_function, get_amount)
        self.last_spawn = 0
        self.died_amount = 0

    def spawn_enemy(self):
        self.add_to_group(Asteroid(self.add_to_group, self.images, random.randrange(
            10, self.display_size[0]-10)), ('all', 'enemy'))

    def spawn(self, now):
        if self.run_spawn:
            if now - self.last_spawn > round(self.cooldawn):
                self.spawn_enemy()
                self.last_spawn = now

    def update_cooldawn(self, amount):
        self.cooldawn += amount
        return self.cooldawn

    @property
    def getCooldawn(self):
        return self.cooldawn, self.min_cooldawn, self.max_cooldawn


class FirstEnemySpawner(AbstractSpawner):
    spawn_cooldawn = 3500
    max_amount = 3

    def __init__(self, images: list, display_size: list, add_function, get_amount):
        super().__init__(images, display_size, add_function, get_amount)
        self.last_spawn = 0
        self.died_amount = 0

    def spawn_enemy(self):
        self.add_to_group(FirstEnemy(
            self.images, self.display_size, self.add_to_group), ('all', 'enemy'))

    def spawn(self, now):
        if self.run_spawn:
            if now > 1000:
                if now - self.last_spawn > self.spawn_cooldawn:
                    if self.get_amount(FirstEnemy) < self.max_amount:
                        self.spawn_enemy()
                        self.last_spawn = now


class AbstractLevelCreator:
    def __init__(self):
        self.mobs = []
        self.kill_list = {}
        self.__waves = {}

        self.groups = {
            'all': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'player': pygame.sprite.Group(),
            'items': pygame.sprite.Group()
        }

    def add_to_group(self, what: object, towhat: list):
        for i in towhat:
            self.groups[i].add(what)

    @property
    def get_all(self):
        return self.groups['all']

    @property
    def get_enemy(self):
        return self.groups['enemy']

    @property
    def get_player(self):
        return self.groups['player']

    def get_amount(self, class_name):
        amount = 0

        for i in self.groups['all']:
            if isinstance(i, class_name):
                amount += 1

        return amount

    def updateKillList(self, what: str):
        self.kill_list[what] += 1

    def getKills(self, what: str):
        return self.kill_list[what]


class FirstLevelCreator(AbstractLevelCreator, AsteroidSpawner, FirstEnemySpawner):
    def __init__(self, display_size, add_function, get_amount):
        super().__init__()

        self.add_to_group = add_function
        self.get_amount = get_amount
        self.now_wave = 1
        self.kill_list = {
            'FirstEnemy': 0,
            'Asteroid': 0
        }
        self.spawn_speed = {
            'Asteroid': -1.5,
            'FirstEnemy': 0
        }

        display = pygame.display.set_mode(display_size)
        path = os.getcwd()

        enemy = {'asteroid': {
            'default': [pygame.image.load(path+'\\img\\Enemy\\asteroid' + str(i)+'.png').convert_alpha() for i in range(1, 7)],
            'burst': [pygame.image.load(path+'\\img\\Enemy\\burst\\asteroid_burst' + str(i)+'.png').convert_alpha() for i in range(1, 5)]
        },
            'flightenemy': {
            'default': [pygame.image.load(path+'\\img\\Enemy\\FirstEnemy\\1Enemy' + str(i)+'.png').convert_alpha() for i in range(1, 3)],
            'burst': [pygame.image.load(path+'\\img\\Enemy\\FirstEnemy\\burst\\1Enemy' + str(i)+'.png').convert_alpha() for i in range(1, 10)],
            'shell': {
                'default': pygame.image.load(path+'\\img\\Enemy\\FirstEnemy\\Shell\\RedShell.png').convert_alpha(),
                'burst': [pygame.image.load(path+'\\img\\Enemy\\FirstEnemy\\Shell\\RedShell'+str(i)+'.png').convert_alpha() for i in range(1, 4)]
            }
        }
        }

        self.__FirstEnemySpawner = FirstEnemySpawner(
            enemy['flightenemy'], display_size, add_function, get_amount)
        self.__AsteroidSpawner = AsteroidSpawner(
            enemy['asteroid'], display_size, add_function, get_amount)

    def updateLevel(self, now):
        self.__AsteroidSpawner.spawn(now)
        self.__FirstEnemySpawner.spawn(now)

    def updateCooldawn(self):
        n, min_, max_ = self.__AsteroidSpawner.getCooldawn
        if max_ < n - self.spawn_speed['Asteroid'] < min_:
            self.spawn_speed['Asteroid'] *= -1

        self.__AsteroidSpawner.update_cooldawn(-1.5)
