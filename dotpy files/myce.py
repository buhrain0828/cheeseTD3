import pygame

class Myce(pygame.sprite.Sprite):
    def __init__(self, position, image):
    pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position