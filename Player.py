import pygame
import os
from scaler import Scale
from animation import Animator
import numpy as np
from time import sleep
import asyncio


class Mana:
    def __init__(self, display_size):
        self.display_size = display_size
        self.image = pygame.image.load(
            os.getcwd()+f'\img\interface\Stamina3.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(display_size[0]//2, 15))
        self.padding = round(self.rect.width*0.05)
        self.circleValues = np.arange(
            self.rect.left+self.padding, self.rect.right-self.padding, dtype=np.int)
        self.DEFAULTAMOUNT = 150
        self.AMOUNT = self.DEFAULTAMOUNT
        self.step = self.circleValues.size / self.AMOUNT
        print(self.circleValues.size)

    def draw(self, display):
        display.blit(self.image, self.rect)

        for i in self.circleValues[:int(self.AMOUNT*self.step)]:
            pygame.draw.circle(
                display, (71, 204, 221), (i, self.rect.centery), self.rect.height//2-self.padding//3)

    def toSpend(self, value):
        if self.AMOUNT - value >= 0:
            self.AMOUNT -= value
            return True
        else:
            return False

    def toEnlarge(self, value):
        if self.AMOUNT + value <= self.DEFAULTAMOUNT:
            self.AMOUNT += value
        elif self.AMOUNT + value > self.DEFAULTAMOUNT:
            self.AMOUNT = self.DEFAULTAMOUNT


class Heart(pygame.sprite.Sprite):
    def __init__(self, images, x, y):
        super().__init__()
        self.images = images
        self.rect = self.images[0].get_rect(center=(x, y))
        self.x, self.y = self.rect.centerx, self.rect.top
        self.start_hited_animation = False
        self.start_heal_animation = False
        self.last_update = {'time': 0, 'iteral': 0}

    def draw(self, display, tick=95):
        display.blit(
            self.images[self.last_update['iteral']], (self.rect.x, self.rect.y))

    def update(self, now):
        if self.start_hited_animation:
            self.heart(now)

        elif self.start_heal_animation:
            self.heal(now)

    def heal(self, now, tick=95):
        self.last_update['iteral'] = 0
        self.start_heal_animation = False

    def heart(self, now, tick=95):
        if now - self.last_update['time'] > tick:
            self.last_update['time'] = now

            if self.last_update['iteral'] + 1 <= len(self.images)-1:
                self.last_update['iteral'] += 1

                if self.last_update['iteral'] == 1:
                    self.rect.y -= 10
                else:
                    self.rect.y = self.y
            else:
                self.start_hited_animation = False


class HeartsGroup:
    def __init__(self, display_size):
        self.display_size = display_size
        self.heart_list = []
        self.heart_images = [pygame.image.load(os.getcwd()+r'\img\interface\heart2.png').convert_alpha(),
                             pygame.image.load(
            os.getcwd()+r'\img\interface\whiteheart.png').convert_alpha(),
            pygame.image.load(os.getcwd()+r'\img\interface\deathheart.png').convert_alpha()]

        self.heart_images = Scale()._list(self.heart_images, 1)

        for i in range(1, 11):
            self.heart_list.append(
                Heart(self.heart_images, i*45, self.heart_images[0].get_height()))

    def hit(self, XP, damage):
        if XP > 0:
            for i in range(XP, XP+damage):
                self.heart_list[i].start_hited_animation = True

    def heal(self, XP, amount):
        for i in range(XP-amount, XP):
            self.heart_list[i].start_heal_animation = True


class Player(pygame.sprite.Sprite,  HeartsGroup, Mana):
    def __init__(self, x, y, display_size):
        super().__init__()

        self.burstAnimator = Animator()
        self.flowAnimator = Animator()

        self.Health = HeartsGroup(display_size)
        self.Stamina = Mana(display_size)

        self.x, self.y = x, y
        self.display_size = display_size

        path = os.getcwd()
        self.skins = {
            'purple': {
                'left_move': [pygame.image.load(path+r'\img\spaceship\purpleship\left'+str(i)+'.png') for i in range(1, 3)],
                'right_move': [pygame.image.load(path+r'\img\spaceship\purpleship\right'+str(i)+'.png') for i in range(1, 3)],
                'default': [pygame.image.load(path+r'\img\spaceship\purpleship\space'+str(i)+'.png') for i in range(1, 3)],
                'color': 'purple'
            },
            'red': {
                'left_move': [pygame.image.load(path+r'\img\spaceship\redship\left'+str(i)+'.png') for i in range(1, 3)],
                'right_move': [pygame.image.load(path+r'\img\spaceship\redship\right'+str(i)+'.png') for i in range(1, 3)],
                'default': [pygame.image.load(path+r'\img\spaceship\redship\space'+str(i)+'.png') for i in range(1, 3)],
                'color': 'red'
            }
        }

        self.images = self.skins['purple']
        self.acting_images = self.images['default']

        self.rect = pygame.Rect(
            self.x, self.y, self.images['default'][0].get_width(), self.images['default'][0].get_height())
        self.speed = {'accel': 1, 'finite': 8}
        self.DEFAULTXP = 10
        self.XP = self.DEFAULTXP

        self.hitted_rects = [pygame.Rect(self.rect.centerx - 10, self.rect.top+15, 20, self.rect.bottom - self.rect.top-25),
                             pygame.Rect(self.rect.left+10, self.rect.top +
                                         65, self.rect.right - self.rect.left-22, 45)
                             ]
        self.last_strike = 0
        self.last_skinChanging = 0

    def update(self, now, tick=80):
        self.hitted_rects = [pygame.Rect(self.rect.centerx - self.rect.width*.2//2, self.rect.top, self.rect.width*0.2, self.rect.bottom - self.rect.top-self.rect.height*0.1),
                             pygame.Rect(self.rect.left, self.rect.top+self.rect.height*0.36,
                                         self.rect.right - self.rect.left, self.rect.height*0.25)
                             ]

        self.flowAnimator.updateAnimation(
            now, len(self.acting_images), tick, self.flowAnimator.IteralToNull)

    def draw(self, display):
        display.blit(self.acting_images[self.flowAnimator.getIteral],
                     (self.rect.x, self.rect.y))

    def Strike(self, now, object, image, func):
        if object:
            if now - self.last_strike > object.cooldawn:
                if self.Stamina.toSpend(object.stm):
                    func(object(image, self.rect), ('all', 'player'))
                    self.last_strike = now

    def hit(self, damage):
        self.XP -= damage
        self.Health.hit(self.XP, damage)

        return self.XP

    def heal(self, amount):
        if self.XP == self.DEFAULTXP:
            pass

        elif self.XP + amount <= self.DEFAULTXP:
            self.XP += amount
            self.Health.heal(self.XP, amount)

        else:
            # аааааа дублирование кода
            amount = (self.XP + amount)-self.DEFAULTXP
            self.XP += amount
            super().heal(self.XP, amount)

    def changeSkinPack(self, now):
        if now - self.last_skinChanging > 250:
            a = list(self.skins.keys())
            index = a.index(self.images['color'])

            if index + 1 < len(a):
                pack_name = a[index+1]
            else:
                pack_name = a[0]

            self.images = self.skins[pack_name]
            self.rect = pygame.Rect(self.rect.x, self.rect.y, self.images['default'][0].get_width(
            ), self.images['default'][0].get_height())

            self.last_skinChanging = now
            

