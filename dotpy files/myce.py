import pygame
import variables as var

class Myce(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, sprite_sheet):
        pygame.sprite.Sprite.__init__(self)

        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = self.tile_x * var.TileSize + var.TileSize // 2
        self.y = self.tile_y * var.TileSize + var.TileSize // 2

        self.sprite_sheet = sprite_sheet
        self.animatelist = self.imageload()
        self.frame_indx = 0

        self.image = self.animatelist[self.frame_indx]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def imageload(self):
        # Use full sheet height to capture complete sprite
        frame_width = 446
        frame_height = self.sprite_sheet.get_height()  # Use full sheet height (827px)
        animatelist = []
        for i in range(4):
            x = i * frame_width
            y = 0
            # Ensure we don't go out of bounds
            actual_height = min(frame_height, self.sprite_sheet.get_height() - y)
            single_img = self.sprite_sheet.subsurface(x, y, frame_width, actual_height)
            # scale down preserving aspect ratio to fit within 96x96
            target_size = 96
            scale_factor = min(target_size / frame_width, target_size / actual_height)
            new_width = int(frame_width * scale_factor)
            new_height = int(actual_height * scale_factor)
            scaled_img = pygame.transform.scale(single_img, (new_width, new_height))
            animatelist.append(scaled_img)
        return animatelist