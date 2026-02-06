import pygame
import variables as var
class Myce(pygame.sprite.Sprite):
    def __init__(self, tile_x,tile_y, image):
        pygame.sprite.Sprite.__init__(self)
        self.tile_x = tile_x
        self.tile_y = tile_y
        #centre of myce
        self.x = self.tile_x * var.TileSize + var.TileSize
        self.y = self.tile_y * var.TileSize + var.TileSize 
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)