import pygame
import os
from animation import Animator


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


class Player(pygame.sprite.Sprite,  HeartsGroup):
    def __init__(self, x, y, display_size):
        super().__init__()

        self.burstAnimator = Animator()
        self.flowAnimator = Animator()

        HeartsGroup.__init__(self, display_size)

        self.x, self.y = x, y
        self.display_size = display_size

        self.images = [pygame.image.load(
            os.getcwd()+r'\img\spaceship\space'+str(i)+'.png') for i in range(1, 3)]
        self.left_move = [pygame.image.load(
            os.getcwd()+r'\img\spaceship\left'+str(i)+'.png') for i in range(1, 3)]
        self.right_move = [pygame.image.load(
            os.getcwd()+r'\img\spaceship\right'+str(i)+'.png') for i in range(1, 3)]
        self.acting_images = self.images

        self.rect = pygame.Rect(
            self.x, self.y, self.images[0].get_width(), self.images[0].get_height())
        self.speed = {'accel': 1, 'finite': 8}
        self.DEFAULTXP = 10
        self.XP = self.DEFAULTXP

        self.hitted_rects = [pygame.Rect(self.rect.centerx - 10, self.rect.top+15, 20, self.rect.bottom - self.rect.top-25),
                             pygame.Rect(self.rect.left+10, self.rect.top +
                                         65, self.rect.right - self.rect.left-22, 45)
                             ]
        self.last_strike = 0

    def update(self, now, tick=80):
        self.hitted_rects = [pygame.Rect(self.rect.centerx - 10, self.rect.top+15, 20, self.rect.bottom - self.rect.top-25),
                             pygame.Rect(self.rect.left+10, self.rect.top +
                                         65, self.rect.right - self.rect.left-22, 45)
                             ]

        self.flowAnimator.updateAnimation(now, len(self.acting_images), tick, self.flowAnimator.IteralToNull)

    def draw(self, display):
        display.blit(self.acting_images[self.flowAnimator.getIteral],
                     (self.rect.x, self.rect.y))

    def Strike(self, now, object, image, func):
        if now - self.last_strike > object.cooldawn:
            func(object(image, self.rect), ('all', 'player'))
            self.last_strike = now

    def hit(self, damage):
        self.XP -= damage
        super().hit(self.XP, damage)

        return self.XP

    def heal(self, amount):
        if self.XP == self.DEFAULTXP:
            pass

        elif self.XP + amount <= self.DEFAULTXP:
            self.XP += amount
            super().heal(self.XP, amount)

        else:
            # аааааа дублирование кода
            amount = (self.XP + amount)-self.DEFAULTXP
            self.XP += amount
            super().heal(self.XP, amount)
