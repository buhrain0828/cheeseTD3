import pygame
import variables as var
class Myce(pygame.sprite.Sprite):
    def __init__(self,tile_x,tile_y, sprite_sheet):
        pygame.sprite.Sprite.__init__(self)

    #pos variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        #centre of myce
        self.x = self.tile_x * var.TileSize + var.TileSize
        self.y = self.tile_y * var.TileSize + var.TileSize 
    #"animation"
        self.sprite_sheet = sprite_sheet
        self.animatelist = []

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
    def imageload(self):
        #extract images
        size = self.sprite_sheet.get_height()
        animatelist = []
        for i in range (4)
        single_img = self.sprite_sheet.subsurface(x * size, 0, size, size)
        animatelist.append(single_img)