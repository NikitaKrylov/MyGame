import pygame
import random
import os
import sys
from levelCreator import FirstLevelCreator
from Enemy import *
from Player import Player, Heart
from Shells import LiteShell, Shell, Bullet, Orange
from items import HeartItem, AbstractItem
from scaler import Scale
import ctypes


class Download:  # загрузка основных компонентов игры
    def __init__(self, display_size):
        self.display = pygame.display.set_mode(display_size)
        self._display_size = display_size
        self.path = os.getcwd()
        self.AMO = {
            'lastlite': {
                'icon': pygame.image.load(self.path+f'\img\shells\lastlite\icon.png').convert_alpha(),
                'default': pygame.image.load(self.path+f'\img\shells\lastlite\lite.png').convert_alpha(),
                'burst': [pygame.image.load(self.path+f'\img\shells\lastlite\lite' + str(i) + '.png').convert_alpha() for i in range(1, 5)]
            },
            'lite': {
                'icon': pygame.image.load(self.path+f'\img\shells\lite\icon.png').convert_alpha(),
                'default': pygame.image.load(self.path+f'\img\shells\lite\shell.png').convert_alpha(),
                'burst': [pygame.image.load(self.path+f'\img\shells\lite\shell' + str(i) + '.png').convert_alpha() for i in range(1, 5)]
            },
            'orange': {
                'icon': pygame.image.load(self.path+f'\img\shells\orange\icon.png').convert_alpha(),
                'default':  pygame.image.load(self.path+f'\img\shells\orange\orange.png').convert_alpha(),
                'burst': [pygame.image.load(self.path+f'\img\shells\orange\orange.png').convert_alpha()]
            }
        }
        self.interface = {
            'toolbar': [pygame.image.load(self.path+r'\img\interface\Toolbar\navigate'+str(i)+'.png').convert_alpha() for i in range(1, 6)],
            'menu': [pygame.image.load(self.path+r'\img\font\menu2.png').convert_alpha(), pygame.image.load(self.path+r'\img\font\font3.png').convert_alpha()],
            'labels': {
                'menu': pygame.image.load(self.path+r'\img\font\Menu.png').convert_alpha(),
                'died': pygame.image.load(self.path+r'\img\font\YouDied.png').convert_alpha()
            },
            'buttons': {
                'continue': pygame.image.load(self.path+r'\img\interface\Continue.png').convert_alpha(),
                'exit': pygame.image.load(self.path+r'\img\interface\Quite.png').convert_alpha(),
                'settings': pygame.image.load(self.path+r'\img\interface\Settings.png').convert_alpha(),
                'restart': pygame.image.load(self.path+r'\img\interface\Restart.png').convert_alpha()
            }
        }

        self.font = pygame.image.load(
            self.path+r'\img\font\space2.png').convert_alpha()


class AbstractMenu(pygame.sprite.Sprite):
    def __init__(self, menu_images, display_size):
        scale = (display_size[0]*0.68)/menu_images['menu'][0].get_width()
        self.menu_image = Scale()._image(menu_images['menu'][0], scale)
        self.blur_font = menu_images['menu'][1]
        self.label = None
        self.buttons_list = []

        self.rect = self.menu_image.get_rect(
            center=(display_size[0]//2, display_size[1]//2))
        self.font_size = 40
        self.font_stile = pygame.font.Font(
            os.getcwd()+r'\addone\karmafuture.ttf', self.font_size)
        self.score_int = 0
        self.score_text = self.font_stile.render(
            f'Your score: {self.score_int}', False, (255, 255, 255))

    def update(self, mouse, score):
        if self.score_int != score:
            self.score_int = score
            self.score_text = self.font_stile.render(
                f'Your score: {self.score_int}', False, (255, 255, 255))

        for button in self.buttons_list:
            if button.rect.collidepoint(mouse.get_pos()):
                if mouse.get_pressed()[0]:
                    button.run_function()
                else:
                    button.hover = True
            else:
                button.hover = False

    def draw(self, display, score):
        display.blit(self.blur_font, (0, 0))
        display.blit(self.menu_image, self.rect)

        for button in self.buttons_list:
            button.draw(display)

        display.blit(self.score_text, (self.rect.centerx*0.5,
                                       self.rect.top+self.font_size))
        display.blit(self.label, (self.rect.centerx -
                                  self.label.get_width()//2, self.rect.top+self.rect.height*0.2))


class PauseMenu(AbstractMenu):
    def __init__(self, menu_images, display_size, **func):
        super().__init__(menu_images, display_size)

        self.buttons_list = [
            Button(menu_images['buttons']['continue'],
                   (self.rect.centerx, self.rect.centery*.87), func['continue_']),

            Button(menu_images['buttons']['settings'],
                   (self.rect.centerx, self.rect.centery*1.12), func['settings_']),

            Button(menu_images['buttons']['restart'],
                   (self.rect.centerx, self.rect.centery*1.37), func['restart_']),

            Button(menu_images['buttons']['exit'],
                   (self.rect.centerx, self.rect.centery*1.62), func['exit_']),

        ]
        self.label = menu_images['labels']['menu']


class DiedMune(AbstractMenu):
    def __init__(self, menu_images, display_size, **func):
        super().__init__(menu_images, display_size)

        self.buttons_list = [
            Button(menu_images['buttons']['restart'],
                   self.rect.center, func['restart_']),
            Button(menu_images['buttons']['settings'], (self.rect.centerx,
                                                        self.rect.centery+self.rect.height//5.5), func['settings_']),
            Button(menu_images['buttons']['exit'], (self.rect.centerx,
                                                    self.rect.centery+self.rect.height//3), func['exit_'])
        ]
        self.label = menu_images['labels']['died']


class Inventary(AbstractMenu):
    pass


class Button(pygame.sprite.Sprite):
    def __init__(self, image, center, function):
        self.function = function
        self.hover = False
        self.default_image = image
        self.rect = self.default_image.get_rect(center=center)
        self.crop_image = Scale()._image(self.default_image, 1.2)
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
            image = image['icon']
            size = (image.get_width(), image.get_height())
            change_index = self.tb_rect.height * 0.6//size[1]
            image = Scale()._image(image, change_index)
            self.shells_image.update({name: image})

        self.position_list = [(i+2, self.tb_rect.y-2) for i in range((self.tb_rect.width//7)
                                                                     * 2+self.tb_rect.x, self.tb_rect.x+self.tb_rect.width, self.tb_rect.width//7)]

        self.number_list = {i+49: i for i in range(0, len(self.tb_images))}

        self.objects = {0: [LiteShell, self.shells_image['lite']],
                        1: [Bullet, self.shells_image['lastlite']],
                        2: [Orange, self.shells_image['orange']]
                        }
        self.iteral = 0

    def scroll(self, command):  # переключение элементов тулбара
        if command == 5:
            if self.iteral + 1 <= len(self.objects)-1:  # прокрутка вправо
                self.iteral += 1
            else:
                self.iteral = 0
        elif command == 4:  # прокрутка влево
            if self.iteral - 1 >= 0:
                self.iteral -= 1
            else:
                self.iteral = len(self.objects)-1

        elif command in self.number_list:  # переключение по цифрам
            if self.number_list[command] > len(self.objects)-1:
                pass
            else:
                self.iteral = self.number_list[command]

    def draw(self, display):
        display.blit(self.tb_images[self.iteral], self.tb_rect)

        for num, list in self.objects.items():  # прорисовывает ТОЛЬКО объекты в списке элементов #NOT NONE!
            display.blit(list[1], (self.position_list[num][0]+self.tb_rect.width//7//2-list[1].get_width()//2,
                                   self.position_list[num][1]+self.tb_rect.height//4))


class Game(Download, FirstLevelCreator):
    def __init__(self, display_width=800, display_height=1000):
        pygame.init()
        self.display_size = self.display_width, self.display_height = (
            display_width, display_height)

        super().__init__(self.display_size)

        FirstLevelCreator.__init__(
            self, self.display_size, self.add_to_group, self.get_amount_objects)

        self.y_font = [0, self.font.get_height()*-1]
        self.display = pygame.display.set_mode(
            self.display_size)
        self.clock = pygame.time.Clock()
        self.__Run = True
        self.__show_menu_bool = False
        self.died_signal = False
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
        self.PauseMenu = PauseMenu(self.interface, self.display_size,
                                   exit_=self.exit_game, continue_=self.show_menu, settings_=self.settings, restart_=self.restart)
        self.DiedMenu = DiedMune(self.interface,  self.display_size,
                                 restart_=self.restart, settings_=self.settings, exit_=self.exit_game)

        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def restart(self):
        self.died_signal = False
        self.show_menu()

        self.clock = pygame.time.Clock()

        self.objectGroups = {
            'all': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'player': pygame.sprite.Group(),
            'items': pygame.sprite.Group()
        }

        FirstLevelCreator.__init__(
            self, self.display_size, self.add_to_group, self.get_amount_objects)

        self.last_sleep = 0
        self.elampsed_time = 0
        self.player = Player(self.display_width//2-50,
                             self.display_height//2-50, self.display_size)

        self.Score = Score(42)
# -----------------------------------ОТРИСОКВКА И ОБНОВЛЕНИЕ-------------------------------------------------------

    def draw_interface(self):
        #self.Score.draw(self.display, self.display_size)
        self.Toolbar.draw(self.display)

        for i in self.player.Health.heart_list:
            i.draw(self.display)

        self.player.Stamina.draw(self.display)

    def draw_font(self):
        self.display.blit(self.font, (0, self.y_font[0]))
        self.display.blit(self.font, (0, self.y_font[1]))

    def draw_objects(self):  # отрисовка элементов
        for i in self.get_all_objects:
            i.draw(self.display)

        self.player.draw(self.display)

    def update_game_element(self):
        now = self.get_game_time
        self.player.update(now)

        if self.player.XP <= 0:
            self.show_menu()
            self.died_signal = True

        for i in range(len(self.y_font)):
            if self.y_font[i] >= self.display_height:
                self.y_font[i] = -1400

        for i in range(len(self.y_font)):
            self.y_font[i] += 1

        for i in self.get_all_objects:
            if isinstance(i, AbstractItem):
                i.update(now, self.player.rect)
            else:
                i.update(now)

        for i in self.player.Health.heart_list:
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
            self.player.acting_images = self.player.images['left_move']

        if key[pygame.K_d] and self.player.rect.right < self.display_width:
            self.player.rect.x += int(self.player.speed['accel'])
            self.player.acting_images = self.player.images['right_move']

        if not key[pygame.K_d] and not key[pygame.K_a]:
            self.player.acting_images = self.player.images['default']

        if key[pygame.K_q]:
            self.player.changeSkinPack('red')


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
            for hitted_rect in element.hitted_rects:
                if isinstance(element, AbstractEnemy):  # если element враг
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
                            # коллизмя игрока с вражеским кораблем
                            if isinstance(element, FlyingEnemy):
                                self.player.rect.y += self.player.rect.height
                                self.player.hit(1)
                            else:
                                if not element.run_burst:  # колизия игрока с любым другим объктом
                                    self.player.hit(element.DAMAGE)

                                element.drop_items = element.kill
                                element.run_burst = True

                elif isinstance(element, AbstractItem):
                    for player_rect in self.player.hitted_rects:
                        if player_rect.colliderect(hitted_rect):
                            if isinstance(element, HeartItem):
                                self.player.heal(1)
                                element.kill()

                            elif isinstance(element, ManaPoint):
                                self.player.Stamina.toEnlarge(4)
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
                self.last_spawner_sleeped(
                    pygame.time.get_ticks())

                mouse_pos = pygame.mouse

                if self.died_signal:
                    self.DiedMenu.draw(
                        self.display, int(self.Score.score_count))
                    self.DiedMenu.update(
                        mouse_pos, int(self.Score.score_count))
                else:
                    self.PauseMenu.draw(
                        self.display, int(self.Score.score_count))
                    self.PauseMenu.update(
                        mouse_pos, int(self.Score.score_count))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

# -------------------------------------------ТЕХНИЧЕСКИЕ ФУНКЦИИ-----------------------------------------------


if __name__ == "__main__":
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    game = Game(int(screensize[1]*.75), int(screensize[1]*.9))
    game.run_game()
