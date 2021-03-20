import pygame
from animation import Animator


class AbstractItem(pygame.sprite.Sprite, Animator):
    def __init__(self, pos: list, images):
        super().__init__()
        Animator.__init__(self)

        self.images = images

        if isinstance(self.images, list):
            self.rect = self.images[0].get_rect(center=pos)
        else:
            self.rect = self.images.get_rect(center=pos)

    def draw(self, display):
        display.blit(self.images, self.rect)

    def update(self, now):
        self.rect.y += 1

    def use(self):
        self.function()


class HeartItem(AbstractItem):
    def __init__(self, pos, images):
        super().__init__(pos, images)

