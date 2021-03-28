import pygame
from animation import Animator
from math import sqrt


class AbstractItem(pygame.sprite.Sprite, Animator):
    def __init__(self, pos: list, images):
        super().__init__()
        Animator.__init__(self)

        self.images = images
        self.default_speed = 1600
        self.speed = self.default_speed

        if isinstance(self.images, list):
            self.rect = self.images[0].get_rect(center=pos)
        else:
            self.rect = self.images.get_rect(center=pos)
            self.hitted_rects = [self.rect.copy()]

    def draw(self, display):
        display.blit(self.images, self.rect)

    def update(self, now, _player):
        dx, dy = _player.centerx - self.rect.centerx, _player.centery - self.rect.centery
        distanse = sqrt(dx**2+dy**2)

        if distanse > _player.height*3:
            self.rect.y += 1
        else:
            try:
                self.speed = round(self.default_speed / distanse)
            except ZeroDivisionError:
                self.speed = self.default_speed

            dx, dy = dx/distanse*self.speed, dy/distanse*self.speed
            self.rect.centerx += dx
            self.rect.centery += dy
            self.hitted_rects[0] = self.rect.copy()

    def use(self):
        self.function()


class HeartItem(AbstractItem):
    def __init__(self, pos, images):
        super().__init__(pos, images)


class ManaPoint(AbstractItem):
    def __init__(self, pos, images):
        super().__init__(pos, images)

