import pygame
from pygame.math import Vector2
class Foe(pygame.sprite.Sprite):
    def __init__(self, waypoint, image):
        pygame.sprite.Sprite.__init__(self)
        self.waypoint = waypoint
        self.pos = Vector2(self.waypoint[0])
        self.target_waypoint = 1
        self.image = image
        self.speed = 1
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    def update(self):
        self.move()
    def move(self):
        #target waypoint
        self.target = Vector2(self.waypoint[self.target_waypoint])
        self.movement = self.target - self.pos
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

    