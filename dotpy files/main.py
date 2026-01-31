import sys
import os
import pygame
from mapspace import MapSpace
import json
from myce import Myce

# Ensure the project root is on sys.path so absolute imports like `assets` resolve
# when running this script from the `main/` subfolder.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import variables as var
import  enemies as enemies
#to run the code, use cd C:\Users\osabr\OneDrive\Documents\GitHub\cheeseTD3
#.\.venv\Scripts\Activate.ps1
#python main.py
print(f'Running with {sys.executable}')


#set up clock
clock = pygame.time.Clock()


# Initialize Pygame and the game window
pygame.init()
screen = pygame.display.set_mode((var.SCREEN_WIDTH, var.SCREEN_HEIGHT))
pygame.display.set_caption("CheeseTD3")

#images
#map
map_image = pygame.image.load('assets/images/maps/teetrex.png').convert_alpha()
#enemy
foe_image = pygame.image.load('assets/images/enemies/foe1.png').convert_alpha()
#myce

#load json level stuff
with(open('tilesheets/teetrex..tmj')) as file:
    mapspace_data = json.load(file)

#create map space (map menu pnding)
mapspace = MapSpace(mapspace_data,map_image, var.SCREEN_WIDTH, var.SCREEN_HEIGHT)
mapspace.objprocess()





foe = enemies.Foe(mapspace.wayp, foe_image)
print(foe)

#create groups
foe_group = pygame.sprite.Group()
foe_group.add(foe)
myce_group = pygame.sprite.Group()


#Player rectangle
player = pygame.Rect(300, 250, 50, 50)


# Game loop
running = True
while running:
    clock.tick(var.FPS)
    #fill screen
    screen.fill(var.BACKGROUND_COLOR)

    #draw map
    mapspace.draw(screen)
    

    #update groups
    foe_group.update()
    #draw groups
    foe_group.draw(screen)

   

    #Exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #click
        if event.type == pygame.MOUSEBUTTONDOWN and even.button == 1:
            mouse_pos = pygame.mouse.get
            if mouse_pos [0] > var.SCREEN_WIDTH or mouse_pos[1] > var.SCREEN_HEIGHT:
                myce = Myce()
                myce_group.add(myce)

    # Update the display
    pygame.display.flip()

pygame.quit()
print("Game closed.")