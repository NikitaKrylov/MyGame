import pygame
import random
from animation import Animator
from math import sin, cos
from Shells import Shell
from items import HeartItem, ManaPoint
import os
from Player import Player


class AbstractEnemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.burstAnimator = Animator()
        self.flowAnimator = Animator()
        self.spawn = True
        self.run_burst = False
        self.hitted_rects = []


class FlyingEnemy(AbstractEnemy):
    def __init__(self, images, add_function):
        self.add_function = add_function
        self.add_function = add_function
        self.default_images = images['default']
        self.burst_images = images['burst']
        self.redshell = images
        self.drop = images['drop']
        super().__init__()
    
    def drop_items(self):
        for i in range(random.randint(2, 6)):
            self.add_function(ManaPoint(
                (random.randint(self.rect.left, self.rect.right), random.randint(self.rect.top, self.rect.bottom)), self.drop['manapoint']), ('all', 'items'))
        self.kill()



class StaticEnemy(AbstractEnemy):
    def __init__(self, add_function):
        self.add_function = add_function
        super().__init__()

    def drop_items(self):
        if random.randint(1, 4) == 1:
            self.add_function(HeartItem(self.rect.center, self.drop['health']), ('all', 'items'))

        for i in range(random.randint(1, 4)):
            self.add_function(ManaPoint(
                (random.randint(self.rect.left, self.rect.right), random.randint(self.rect.top, self.rect.bottom)), self.drop['manapoint']), ('all', 'items'))
        
        self.kill()


    


class ShellsEnemy(AbstractEnemy, Shell):
    def __init__(self, images, rect, speed):
        super().__init__()
        Shell.__init__(self, images, rect, 'shell', speed)
        self.spawn = False


class RedShell(ShellsEnemy):
    cooldawn = 1000

    def __init__(self, images, rect):
        super().__init__(images, rect, -10)
        x, y = rect.centerx, int(rect.bottom)
        self.rect = self.image.get_rect(center=(x, y))
        self.hitted_rects = [self.rect.copy()]
        self.DAMAGE = 1


class FirstEnemy(FlyingEnemy):
    def __init__(self, images: list,  display_size: list, add_function):
        super().__init__(images, add_function)
        self.display_size = display_size
        self.iteral_index = 1
        self.list_iteral = 0

        self.rect = self.default_images[0].get_rect(
            center=((self.default_images[0].get_width()*-2, self.display_size[1]*0.6)))
        self.hitted_rects = [pygame.Rect(
            self.rect.x, self.rect.y, self.rect.width//2, self.rect.height//3)]
        self.y_speed = int(self.rect.height//2 +
                           self.rect.height//random.randint(1, 4))

        speed = random.randint(2, 4)
        e = random.uniform(0.006, 0.01)
        self.cord_list = [[x, int(sin(x*e)*60)+self.display_size[1]*0.1+self.default_images[0].get_height()]
                          for x in range(self.rect.width*-2, self.display_size[0]+self.rect.width*2, speed)]

        self.XP = 120
        self.DEFAULTXP = self.XP
        self.DAMAGE = 1
        self.EXP = 110
        self.last_strike = 0


    def change_y_position(self):
        if self.rect.bottom > self.display_size[1]*0.4 and self.y_speed > 0:
            self.y_speed *= -1

        elif self.rect.top < self.display_size[1]*0.1-self.y_speed and self.y_speed < 0:
            self.y_speed *= -1

        for i in range(len(self.cord_list)-1):
            self.cord_list[i][1] += self.y_speed

    def update(self, now):
        if self.run_burst:
            self.burstAnimator.updateAnimation(
                now, len(self.burst_images), 90, self.drop_items)
        else:
            self.burstAnimator.change_time(now)
            self.flowAnimator.updateAnimation(
                now, len(self.default_images), 80, self.flowAnimator.IteralToNull)

            if self.list_iteral + self.iteral_index >= len(self.cord_list) or self.list_iteral + self.iteral_index < 0:
                self.iteral_index *= -1
                self.change_y_position()

            self.list_iteral += self.iteral_index
            self.rect.center = self.cord_list[self.list_iteral]

            self.hitted_rects = [pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height//1.8),
                                 pygame.Rect(
                self.rect.x+self.rect.width//3.5, self.rect.y, self.rect.width//2.5, self.rect.height)
            ]

        if now - self.last_strike > 2500:
            self.Strike(now)
            self.last_strike = now

    def draw(self, display):
        if self.run_burst:
            display.blit(
                self.burst_images[self.burstAnimator.getIteral], self.rect)
        else:
            display.blit(
                self.default_images[self.flowAnimator.getIteral], self.rect)
            pygame.draw.rect(display, (48, 50, 51), (self.rect.left,
                                                     self.rect.top-self.display_size[1] % 10, self.rect.width, int(self.rect.height*0.07)))
            p = 0 if self.XP/self.DEFAULTXP*100 < 0 else self.XP/self.DEFAULTXP*100

            pygame.draw.rect(display, (200, 0, 0), (self.rect.left, self.rect.top -
                                                    self.display_size[1] % 10, int(self.rect.width/100*p), int(self.rect.height*0.07)))

    def Strike(self, now):
        if not self.run_burst:
            self.add_function(
                RedShell(self.redshell, self.rect), ('all', 'enemy'))

    def hit(self, damage):
        self.XP -= damage

    def __str__(self):
        return 'FirstEnemy'


class Asteroid(StaticEnemy):
    def __init__(self, add_function, image, x):
        super().__init__(add_function)

        self.scale_index = random.uniform(0.8, 2.0)
        random_image = random.choice(image['default'])
        self.drop = image['drop']

        self.burst_images = [pygame.transform.scale(im, (int(random_image.get_width(
        )*self.scale_index), int(random_image.get_height()*self.scale_index))) for im in image['burst']]

        self.image = pygame.transform.scale(random_image, (int(random_image.get_width(
        )*self.scale_index), int(random_image.get_height()*self.scale_index)))
        self.image_copy = self.image.copy()

        self.rect = self.image.get_rect(
            center=(x, (self.image.get_width()+20)*-1))
        self.hitted_rects = [self.rect.copy()]

        self.xspeed = random.randrange(-4,
                                       2) if x >= 500 else random.randrange(-2, 4)
        self.yspeed = random.randrange(1, 13)

        self.rot = 0
        self.rot_speed = random.uniform(-2.0, 2.0)
        self.XP = int(self.scale_index * 1.5 * 26)
        self.DAMAGE = 2 if self.scale_index >= 1.7 else 1
        self.EXP = 25 if self.scale_index >= 1.8 else 18


    def draw(self, display):
        if self.run_burst:
            display.blit(
                self.burst_images[self.burstAnimator.getIteral], self.rect)
        else:
            display.blit(self.image_copy, self.rect)

    def update(self, now):
        if self.run_burst:
            self.burstAnimator.updateAnimation(
                now, len(self.burst_images), 130, self.drop_items)
            # if self.burstAnimator.getIteral == len(self.burst_images)//2:
            #     self.drop_items()
        else:
            self.burstAnimator.change_time(now)

            # перемещение
            for rect in [self.rect, self.hitted_rects[0]]:
                rect.x += self.xspeed
                rect.y += self.yspeed

            # вращение
            self.rect, self.image_copy = self.flowAnimator.Rotate(
                now, self.rot_speed, self.rect, self.image, self.image_copy, 15)

   

    def __str__(self):
        return 'Asteroid'
