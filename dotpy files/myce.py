import pygame
import variables as var
import math


class Myce(pygame.sprite.Sprite):
    def __init__(
        self,
        tile_x,
        tile_y,
        sprite_sheet,
        screen_x=None,
        screen_y=None,
        frame_width=446,
        frame_height=826,
        spacing=323,
        num_frames=4,
        target_width=160,
        damage=None,
        cooldown=None,
        aoe_radius=0,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.cooldown = cooldown if cooldown is not None else var.cooldown
        self.damage = damage if damage is not None else 5
        self.aoe_radius = aoe_radius
        self.last_shot_time = pygame.time.get_ticks() - self.cooldown
        self.range = 100
        self.select = False
        self.active_target = None

        #tile coords
        self.tile_x = tile_x
        self.tile_y = tile_y

        #if caller already knows screen position use it
        #otherwise fall back to original tile size
        if screen_x is not None and screen_y is not None:
            self.x = screen_x
            self.y = screen_y
        else:
            self.x = self.tile_x * var.TileSize + var.TileSize // 2
            self.y = self.tile_y * var.TileSize + var.TileSize // 2

        #each tower sheet has its own spacing so pass it in at spawn
        self.sprite_sheet = sprite_sheet
        self.animatelist = self.imageload(frame_width, frame_height, spacing, num_frames, target_width)
        self.frame_indx = 0
        self.time_stamp = pygame.time.get_ticks()

        #image
        self.angle = 90
        self.orgimage = self.animatelist[self.frame_indx]
        self.image = pygame.transform.rotate(self.orgimage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #range circle
        self.range_image = pygame.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0,))
        self.range_image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(75)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = (self.x, self.y)

    def imageload(self, frame_width, frame_height, spacing, num_frames, target_width):
        #extract each frame from the spritesheet using its own spacing
        animatelist = []
        for i in range(num_frames):
            #each frame is at x = i * (frame_width + spacing)
            x = i * (frame_width + spacing)
            y = 0
            single_img = self.sprite_sheet.subsurface(x, y, frame_width, frame_height)
            #scale to target width while keeping the same ratio
            scale_factor = target_width / frame_width
            new_width = int(frame_width * scale_factor)
            new_height = int(frame_height * scale_factor)
            scaled_img = pygame.transform.scale(single_img, (new_width, new_height))
            animatelist.append(scaled_img)
        return animatelist

    def update(self, foe_group, mapspace=None):
        #only animate while target is locked otherwise look for a new shot
        if self.active_target:
            self.animate()
        else:
            if pygame.time.get_ticks() - self.last_shot_time >= self.cooldown:
                self.turn_to_target(foe_group)

    
    def turn_to_target(self, foe_group, mapspace=None):
        #seek first target in range and optionally splash nearby foes
        for foe in foe_group:
            if foe.health > 0:
                dist_x = foe.pos[0] - self.x
                dist_y = foe.pos[1] - self.y
                dist_e = math.sqrt(dist_x ** 2 + dist_y ** 2)
                if dist_e < self.range:
                    self.active_target = foe
                    self.angle = math.degrees(math.atan2(-dist_y, dist_x))

                    if self.aoe_radius > 0:
                        for splash_foe in foe_group:
                            if splash_foe.health > 0:
                                splash_x = splash_foe.pos[0] - foe.pos[0]
                                splash_y = splash_foe.pos[1] - foe.pos[1]
                                splash_distance = math.sqrt(splash_x ** 2 + splash_y ** 2)
                                if splash_distance <= self.aoe_radius:
                                    splash_foe.health -= self.damage
                    else:
                        self.active_target.health -= self.damage
                    break

    def animate(self):
        #step through firing animation and reset cooldown at the end
        self.orgimage = self.animatelist[self.frame_indx]
        if pygame.time.get_ticks() - self.time_stamp > var.time_delay:
            self.time_stamp = pygame.time.get_ticks()
            self.frame_indx += 1
            if self.frame_indx >= len(self.animatelist):
                self.frame_indx = 0
                self.last_shot_time = pygame.time.get_ticks()
                self.active_target = None

    def draw_range(self, surface):
        self.image = pygame.transform.rotate(self.orgimage, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.select:
            surface.blit(self.range_image, self.range_rect)
