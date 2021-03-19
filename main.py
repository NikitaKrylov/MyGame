import pygame
import random
import os
import sys
from levelCreator import FirstLevelCreator
from Enemy import *
from Player import Player, Heart
from Shells import LiteShell, Shell
from items import HeartItem
import ctypes


class Download:  # загрузка основных компонентов игры
    def __init__(self, display_size):
        display = pygame.display.set_mode(display_size)
        self.path = os.getcwd()
        self.AMO = {
            'default': {
                'default': pygame.image.load(self.path+f'\img\spaceship\shape.png').convert_alpha(),
                'burst': []
            },
            'lite': {
                'default': pygame.image.load(self.path+f'\img\spaceship\lite.png').convert_alpha(),
                'burst': [pygame.image.load(self.path+f'\img\spaceship\lite' + str(i) + '.png').convert_alpha() for i in range(1, 5)]
            }
        }
        self.interface = {
            'toolbar': [pygame.image.load(self.path+r'\img\interface\Toolbar\navigate'+str(i)+'.png').convert_alpha() for i in range(1, 6)],
        }

        self.font = {'font': pygame.image.load(self.path+r'\img\font\space2.png').convert_alpha(),
                     'blurfont': pygame.image.load(self.path+r'\img\font\font2.png').convert_alpha(),
                     'menu': pygame.image.load(self.path+r'\img\font\menu.png').convert_alpha(),
                     'menu2': pygame.image.load(self.path+r'\img\font\menu2.png').convert_alpha(),
                     'buttons': {
                         'continue': pygame.image.load(self.path+r'\img\interface\Continue.png').convert_alpha(),
                         'quite': pygame.image.load(self.path+r'\img\interface\Quite.png').convert_alpha(),
                         'settings': pygame.image.load(self.path+r'\img\interface\Settings.png').convert_alpha()
        }
        }


class Menu(pygame.sprite.Sprite):
    def __init__(self, images, display, display_size, **functions):
        scale = (display_size[0]*0.68)/images[0].get_width()
        self.menu_image = pygame.transform.scale(images[0], (round(
            images[0].get_width()*scale), round(images[0].get_height()*scale)))

        self.blur_font = images[1]
        self.rect = self.menu_image.get_rect(
            center=(display_size[0]//2, display_size[1]//2))

        self.buttons_list = [
            Button(images[2]['continue'], self.rect.center,
                   functions['continue_']),
            Button(images[2]['quite'], (self.rect.centerx,
                                        self.rect.centery+self.rect.height//3), functions['quite']),
            Button(images[2]['settings'], (self.rect.centerx,
                                           self.rect.centery+self.rect.height//5.5), functions['settings'])
        ]

    def draw(self, display):
        display.blit(self.blur_font, (0, 0))
        display.blit(self.menu_image, self.rect)

        for button in self.buttons_list:
            button.draw(display)

    def update(self, mouse):
        for button in self.buttons_list:
            if button.rect.collidepoint(mouse.get_pos()):
                if mouse.get_pressed()[0]:
                    button.run_function()
                else:
                    button.hover = True
            else:
                button.hover = False


class Button(pygame.sprite.Sprite):
    def __init__(self, image, center, function):
        self.function = function
        self.hover = False
        self.default_image = image
        self.rect = self.default_image.get_rect(center=center)

        self.crop_image = pygame.transform.scale(
            self.default_image, (int(self.default_image.get_width()*1.2), int(self.default_image.get_height()*1.2)))
        self.crop_rect = self.crop_image.get_rect(center=center)

    def update(self):
        if self.hover:
            return self.crop_image, self.crop_rect
        else:
            return self.default_image, self.rect

    def draw(self, display):
        image, pos = self.update()
        display.blit(image, pos)

    def run_function(self):
        self.function()


class Score:
    def __init__(self, font_size: int):
        self.score_count = '00000000000'
        self.last_score = self.score_count
        self.font_ = pygame.font.Font(
            os.getcwd()+r'\addone\karmafuture.ttf', font_size)
        self.text = self.font_.render(self.score_count, True, (221, 221, 221))

    def draw(self, display, display_size):
        if self.last_score != self.score_count:
            self.text = self.font_.render(
                self.score_count, True, (221, 221, 221))
            self.last_score = self.score_count

        display.blit(
            self.text, (int(display_size[0]//1.8), 7))

    def update_score(self, exp):
        count = list(self.score_count)[:-len(str(exp+int(self.score_count)))]
        count.append(str(exp+int(self.score_count)))
        self.score_count = ''.join(count)

    def remove_score(self):
        pass


class Toolbar:
    def __init__(self, images, shells_image, x, y):
        self.tb_images = images
        self.tb_rect = self.tb_images[1].get_rect(center=(x, y))
        self.shells_image = {}

        for name, image in shells_image.items():
            image = image['default']
            size = (image.get_width(), image.get_height())
            change_index = self.tb_rect.height * 0.6//size[1]

            image = pygame.transform.scale(
                image, (int(size[0]*change_index), int(size[1]*change_index)))
            self.shells_image.update({name: image})

        self.position_list = [(i+2, self.tb_rect.y-2) for i in range((self.tb_rect.width//7)
                                                                     * 2+self.tb_rect.x, self.tb_rect.x+self.tb_rect.width, self.tb_rect.width//7)]

        self.number_list = {i+49: i for i in range(0, len(self.tb_images))}

        self.objects = {0: [LiteShell, self.shells_image['lite']], 1: [
            LiteShell, self.shells_image['lite']]}
        self.iteral = 0

    def scroll(self, command):  # переключение элементов тулбара
        if command == 5:
            if self.iteral + 1 <= len(self.objects)-1:
                self.iteral += 1
            else:
                self.iteral = 0
        elif command == 4:
            if self.iteral - 1 >= 0:
                self.iteral -= 1
            else:
                self.iteral = len(self.objects)-1

        elif command in self.number_list:
            if self.number_list[command] > len(self.objects)-1:
                pass
            else:
                self.iteral = self.number_list[command]

    def draw(self, display):
        display.blit(self.tb_images[self.iteral], self.tb_rect)

        for num, list in self.objects.items():
            display.blit(list[1], (self.position_list[num][0]+self.tb_rect.width//7//2-list[1].get_width()//2,
                                   self.position_list[num][1]+self.tb_rect.height//4))


class Game(Download, FirstLevelCreator):
    def __init__(self, display_width=800, display_height=1000):
        pygame.init()
        self.display_size = self.display_width, self.display_height = (
            display_width, display_height)
        print(self.display_size)

        super().__init__(self.display_size)

        FirstLevelCreator.__init__(
            self, self.display_size, self.add_to_group, self.get_amount_objects)

        self.y_font = [0, self.font['font'].get_height()*-1]
        self.display = pygame.display.set_mode(
            self.display_size)
        self.clock = pygame.time.Clock()
        self.__Run = True
        self.__show_menu_bool = False
        self.last_sleep = 0
        self.elampsed_time = 0

        self.player = Player(self.display_width//2-50,
                             self.display_height//2-50, self.display_size)

        self.Score = Score(42)

        self.objectGroups = {
            'all': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'player': pygame.sprite.Group(),
            'items': pygame.sprite.Group()
        }

        self.Toolbar = Toolbar(
            self.interface['toolbar'], self.AMO, int(self.display_width//2), 1220)
        self.Menu = Menu(
            (self.font['menu2'], self.font['blurfont'], self.font['buttons']), self.display, self.display_size, continue_=self.show_menu, settings=self.settings, quite=self.exit_game)

        pygame.time.set_timer(pygame.USEREVENT, 1000)

# -----------------------------------ОТРИСОКВКА И ОБНОВЛЕНИЕ-------------------------------------------------------
    def draw_interface(self):
        self.Score.draw(self.display, self.display_size)
        self.Toolbar.draw(self.display)

        for i in self.player.heart_list:
            i.draw(self.display)

    def draw_font(self):
        self.display.blit(self.font['font'], (0, self.y_font[0]))
        self.display.blit(self.font['font'], (0, self.y_font[1]))

    def draw_objects(self):  # отрисовка элементов
        for i in self.get_all_objects:
            i.draw(self.display)

        self.player.draw(self.display)

    def update_game_element(self):
        now = self.get_game_time

        self.player.update(now)

        for i in range(len(self.y_font)):
            if self.y_font[i] >= self.display_height:
                self.y_font[i] = -1400

        for i in range(len(self.y_font)):
            self.y_font[i] += 1

        for i in self.get_all_objects:
            i.update(now)

        for i in self.player.heart_list:
            i.update(now)

        self.updateLevel(self.get_game_time)


# --------------------------------------ОБРАБОТЧИК ЗАЖАТЫХ КЛАВИШЬ-----------------------------------------------

    def keyHandler(self, key):  # обрабатывает зажатые клавишиd
        if True not in key:
            self.player.speed['accel'] = 2

        elif self.player.speed['accel'] < self.player.speed['finite']:
            self.player.speed['accel'] += 0.25

        if key[pygame.K_w] and self.player.rect.top > 0:
            self.player.rect.y -= int(self.player.speed['accel'])

        if key[pygame.K_s] and self.player.rect.bottom < self.display_height:
            self.player.rect.y += int(self.player.speed['accel'])

        if key[pygame.K_a] and self.player.rect.left > 0:
            self.player.rect.x -= int(self.player.speed['accel'])
            self.player.acting_images = self.player.left_move

        if key[pygame.K_d] and self.player.rect.right < self.display_width:
            self.player.rect.x += int(self.player.speed['accel'])
            self.player.acting_images = self.player.right_move

        if not key[pygame.K_d] and not key[pygame.K_a]:
            self.player.acting_images = self.player.images


# -------------------------------------------ИГРОВЫЕ МЕХАННИКИ-----------------------------------------------

    def collide_screen(self):  # проверка вышли ли элементы за предел экрана\
        for element in self.get_all_objects:
            if not isinstance(element, FirstEnemy):
                if element.rect.top >= self.display_height + 150 or element.rect.bottom <= -150:
                    element.kill()
                if element.rect.left >= self.display_width or element.rect.right <= 0:
                    element.kill()

    def collide_objects(self):
        for element in self.get_all_objects:  # все элементы на экране
            if isinstance(element, AbstractEnemy):  # если element враг
                for hitted_rect in element.hitted_rects:

                    # проверка коллизии со снарядом
                    if not isinstance(element, Shell):
                        for shell in self.get_player:
                            if shell.rect.colliderect(hitted_rect):
                                if not element.run_burst and not shell.run_burst:
                                    element.XP -= shell.DAMAGE
                                    shell.run_burst = True

                                    if element.XP <= 0:
                                        self.updateKillList(str(element))
                                        element.run_burst = True
                                        self.Score.update_score(element.EXP)

                    # проверка коллизии с игроком
                    for player_rect in self.player.hitted_rects:
                        if player_rect.colliderect(hitted_rect):
                            if isinstance(element, FlyingEnemy):
                                self.player.hit(1)
                                self.player.rect.y += self.player.rect.height
                            else:
                                if not element.run_burst:
                                    if self.player.hit(element.DAMAGE) <= 0:
                                        self.exit_game()

                                element.run_burst = True

            elif isinstance(element, HeartItem):
                for player_rect in self.player.hitted_rects:
                    if player_rect.colliderect(element.rect):
                        self.player.heal(1)
                        element.kill()
# ---------------------------------------ТЕХНИЧЕСКИЕ МОМЕНТЫ-------------------------------------------

    def exit_game(self):
        self.__Run = False

    def check_show_menu(self):
        return self.__show_menu_bool

    def show_menu(self):
        self.__show_menu_bool = not self.__show_menu_bool

    def settings(self):
        pass

    def last_spawner_sleeped(self, settings):
        self.last_sleep = settings

    @property
    def get_game_time(self):
        return self.elampsed_time

    @get_game_time.setter
    def get_game_time(self, now):
        t = now-self.last_sleep
        if t > 0:
            self.elampsed_time = t

    def add_to_group(self, what: object, where: list):
        for group in where:
            self.objectGroups[group].add(what)

    def get_amount_objects(self, class_name):
        amount = 0

        for i in self.objectGroups['all']:
            if isinstance(i, class_name):
                amount += 1

        return amount

    @property
    def get_all_objects(self):
        return self.objectGroups['all']

    @property
    def get_player(self):
        return self.objectGroups['player']

# -------------------------------------------ГЛАВНЫЙ ЦИКЛ-----------------------------------------------

    def run_game(self):
        while self.__Run:
            # обрабатывает зажатые клавиши
            self.keyHandler(pygame.key.get_pressed())

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.exit_game()

                elif event.type == pygame.USEREVENT:
                    self.updateCooldawn()

                elif event.type == pygame.VIDEORESIZE:
                    self.display_size = self.display_width, self.display_height = event.size
                    self.Toolbar.__init__(self.interface['toolbar'], self.AMO, int(
                        self.display_width//2), self.display_height-self.interface['toolbar'][0].get_height())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.Strike(self.get_game_time,
                                           self.Toolbar.objects[self.Toolbar.iteral][0], self.AMO, self.add_to_group)

                    if event.button in [4, 5]:
                        self.Toolbar.scroll(event.button)

                elif event.type == pygame.KEYDOWN:
                    if event.key in self.Toolbar.number_list:
                        self.Toolbar.scroll(event.key)

                    elif event.key == pygame.K_ESCAPE:

                        self.show_menu()

            if not self.__show_menu_bool:
                self.draw_font()
                self.draw_objects()
                self.draw_interface()

                self.collide_objects()
                self.collide_screen()
                self.update_game_element()
                self.get_game_time = pygame.time.get_ticks()
                self.last_spawner_sleeped(0)

            else:

                self.Menu.draw(self.display)
                self.Menu.update(pygame.mouse)
                self.last_spawner_sleeped(
                    pygame.time.get_ticks())

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

# -------------------------------------------ТЕХНИЧЕСКИЕ ФУНКЦИИ-----------------------------------------------


if __name__ == "__main__":
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    game = Game(int(screensize[1]*.75), int(screensize[1]*.9))
    game.run_game()
