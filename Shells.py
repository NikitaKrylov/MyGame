import pygame
from animation import Animator


class Shell(pygame.sprite.Sprite, Animator):  # общий класс для пуль всех типов
    def __init__(self, images, rect, name, speed):
        super().__init__()
        self.burstAnimator = Animator()
        self.flowAnimator = Animator()
        self.image = images[name]['default']
        self.burst_list = images[name]['burst']
        self.speed = speed
        self.spawn = False

        x, y = rect.centerx, int(rect.top+self.image.get_height()//2)
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
        self.hitted_rects[0] = self.rect

        if self.run_burst:
            self.burstAnimator.updateAnimation(
                now, len(self.burst_list), 40, self.kill)
            self.speed = 0
        else:
            self.burstAnimator.change_time(now)


class Bullet(Shell):
    def __init__(self, images, rect, groups):
        self.speed = 12
        self.DAMAGE = 21
        super().__init__(images, rect, 'default', self.speed)


class LiteShell(Shell):
    cooldawn = 200
    stm = 2

    def __init__(self, images, rect):
        self.speed = 21
        self.DAMAGE = 15
        super().__init__(images, rect, 'lite', self.speed)


class Rocket(Shell):
    cooldawn = 1000

    def __init__(self, images, rect, groups):
        self.speed = 11
        super().__init__(images, rect, 'racket', self.speed)
