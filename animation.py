import pygame


class Animator:
    def __init__(self):
        self.updating = {
            'iteral': 0,
            'rotation': 0,
            'time': 0
        }
        self.rot = 0

    def Rotate(self, now, rot_speed, rect, image, image_copy, cooldawn):
        if now - self.updating['rotation'] > cooldawn:
            self.updating['rotation'] = now
            self.rot = (self.rot + rot_speed) % 360
            new_image = pygame.transform.rotate(image, self.rot)
            old_center = rect.center
            image_copy = new_image
            rect = image_copy.get_rect()
            rect.center = old_center
            return rect, image_copy

        else:
            return rect, image_copy

    def updateAnimation(self, now, list_len, cooldawn, finite_function=None):
        if now - self.updating['time'] > cooldawn:
            self.updating['time'] = now

            if self.updating['iteral']+1 <= list_len-1:
                self.updating['iteral'] += 1
            else:
                if finite_function:
                    finite_function()

    def IteralToNull(self):
        self.updating['iteral'] = 0

    @property
    def getIteral(self):
        return self.updating['iteral']

    def change_time(self, value):
        self.updating['time'] = value
