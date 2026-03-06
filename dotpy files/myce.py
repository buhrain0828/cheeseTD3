import pygame
import variables as var

class Myce(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, sprite_sheet, screen_x=None, screen_y=None,
                 frame_width=446, frame_height=827, spacing=323, num_frames=4, target_width=160):
        pygame.sprite.Sprite.__init__(self)
        self.cooldown = 1500
        self.last_shot_time = pygame.time.get_ticks()

        # tile coords
        self.tile_x = tile_x
        self.tile_y = tile_y

        # if the caller already knows the pixel location on screen (eg. after map scaling)
        # use that; otherwise fall back to the original unscaled tile size
        if screen_x is not None and screen_y is not None:
            self.x = screen_x
            self.y = screen_y
        else:
            self.x = self.tile_x * var.TileSize + var.TileSize // 2
            self.y = self.tile_y * var.TileSize + var.TileSize // 2

        self.sprite_sheet = sprite_sheet
        self.animatelist = self.imageload(frame_width, frame_height, spacing, num_frames, target_width)
        self.frame_indx = 0
        self.time_stamp = pygame.time.get_ticks()

        self.image = self.animatelist[self.frame_indx]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def imageload(self, frame_width, frame_height, spacing, num_frames, target_width):
        # extract each frame from the spritesheet, accounting for spacing between frames
        animatelist = []
        for i in range(num_frames):
            # each frame is at x = i * (frame_width + spacing)
            x = i * (frame_width + spacing)
            y = 0
            single_img = self.sprite_sheet.subsurface(x, y, frame_width, frame_height)
            # scale to target width, preserving aspect ratio
            scale_factor = target_width / frame_width
            new_width = int(frame_width * scale_factor)
            new_height = int(frame_height * scale_factor)
            scaled_img = pygame.transform.scale(single_img, (new_width, new_height))
            animatelist.append(scaled_img)
        return animatelist
    def update(self):
        #automatically clip to next target
        if pygame.time.get_ticks() - self.last_shot_time > self.cooldown:
            self.animate()

    def animate(self):
        #update img
        self.image = self.animatelist[self.frame_indx]
        #has enough time passed from update?
        if pygame.time.get_ticks() - self.time_stamp > var.time_delay:
            self.time_stamp = pygame.time.get_ticks()
            self.frame_indx += 1
            #check to reset frame
            if self.frame_indx >= len(self.animatelist):
                self.frame_indx = 0
            #completed animation, reset cooldown
            self.last_shot_time = pygame.time.get_ticks()
