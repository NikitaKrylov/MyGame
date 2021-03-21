import pygame

class Scale:
    def _image(self, im: object, index):
        return pygame.transform.scale(im, (round(im.get_width()*index), round(im.get_height()*index)))

    def _list(self, list: list, index):
        for i in range(len(list)):
            list[i] = pygame.transform.scale(
                list[i], (round(list[i].get_width()*index), round(list[i].get_height()*index)))
        return list