import pygame
from animation import Animator


class Shell(pygame.sprite.Sprite, Animator):  # общий класс для пуль всех типов
    def __init__(self, images, rect, name, speed):
        super().__init__()
        self.burstAnimator = Animator()
        self.flowAnimator = Animator()
        self.image = images[name]['default']
        self.burst_list = images[name]['burst']
        self.icon = images[name]['icon']
        self.speed = speed
        self.spawn = False

        x, y = rect.centerx, int(rect.top+self.icon.get_height()//2)
        # хитбокс создается на основе картинки без эффектов
        self.icon_rect = self.icon.get_rect(center=(x, y))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitted_rects = [self.rect.copy()]

        self.run_burst = False

    def draw(self, display):
        if self.run_burst:
            display.blit(
                self.burst_list[self.burstAnimator.getIteral], self.rect)
        else:
            display.blit(self.image, self.rect)
            
    def update(self, now):
        self.rect.y -= self.speed

        if self.run_burst:
            self.burstAnimator.updateAnimation(
                now, len(self.burst_list), 40, self.kill)  # 40
            self.speed = 0
            self.rect = self.burst_list[self.burstAnimator.getIteral].get_rect(
                center=(self.rect.center))
        else:
            self.burstAnimator.change_time(now)

        self.icon_rect.center = self.rect.center
        self.hitted_rects[0] = self.icon_rect


class Bullet(Shell):
    cooldawn = 200
    stm = 2

    def __init__(self, images, rect):
        self.speed = 20
        self.DAMAGE = 15
        super().__init__(images, rect, 'lastlite', self.speed)


class LiteShell(Shell):
    cooldawn = 200
    stm = 2

    def __init__(self, images, rect):
        self.speed = 20
        self.DAMAGE = 15
        super().__init__(images, rect, 'lite', self.speed)


class Orange(Shell):
    cooldawn = 350
    stm = 3

    def __init__(self, images, rect):
        self.speed = 18
        self.DAMAGE = 23
        super().__init__(images, rect, 'orange', self.speed)


class Rocket(Shell):
    cooldawn = 1000

    def __init__(self, images, rect):
        self.speed = 11
        super().__init__(images, rect, 'racket', self.speed)
