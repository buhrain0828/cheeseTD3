import pygame
class MapSpace():
    def __init__(self, map_image):
        self.image = map_image

    def draw(self, surface):
        surface.blit(self.image, (0,0))
