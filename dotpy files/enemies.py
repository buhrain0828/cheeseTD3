import pygame
from pygame.math import Vector2
import math
class Foe(pygame.sprite.Sprite):
    def __init__(self, waypoint, image):
        pygame.sprite.Sprite.__init__(self)
        self.waypoint = waypoint
        self.pos = Vector2(self.waypoint[0])
        self.target_waypoint = 1
        self.orgimage = image
        # initial angle must be set before rotating the image
        self.angle = 0
        self.image = pygame.transform.rotate(self.orgimage, self.angle)
        self.speed = 1
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
    def update(self):
        self.move()

    def move(self):
        #target waypoint
        if self.target_waypoint < len(self.waypoint):
            self.target = Vector2(self.waypoint[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            # no more waypoints: remove the sprite and stop further processing
            self.kill()
            return
        #calculate distance to waypoint
        distance = self.movement.length()
        #check if remaining distance > speed
        if distance >= self.speed:
             self.pos += self.movement.normalize() * self.speed
        else:
            if distance !=0:
                self.pos += self.movement.normalize() * distance
            self.target_waypoint += 1
        self.rect.center = self.pos


    