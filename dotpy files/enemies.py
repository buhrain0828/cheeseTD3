import pygame
from pygame.math import Vector2
import math
import variables as var
from allfoedata import FOE_DATA
class Foe(pygame.sprite.Sprite):
    def __init__(self, foe_type,waypoint, images):
        pygame.sprite.Sprite.__init__(self)
        self.waypoint = waypoint
        self.pos = Vector2(self.waypoint[0])
        self.target_waypoint = 1
        self.orgimage = images.get(foe_type)
        # initial angle must be set before rotating the image
        self.angle = 0
        self.image = pygame.transform.rotate(self.orgimage, self.angle)
        self.health = FOE_DATA.get(foe_type)["health"]
        self.speed = FOE_DATA.get(foe_type)["speed"]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
    def update(self, mapspace):
        self.move(mapspace)
        self.check_death(mapspace)

    def move(self, mapspace):
        #target waypoint
        if self.target_waypoint < len(self.waypoint):
            self.target = Vector2(self.waypoint[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            # no more waypoints: remove the sprite and stop further processing
            self.kill()
            mapspace.health -= 1
            mapspace.foes_missed += 1
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


    def check_death(self, mapspace):
        if self.health <= 0:
            mapspace.foes_killed += 1
            mapspace.quesos += var.quesoperkill
            self.kill()