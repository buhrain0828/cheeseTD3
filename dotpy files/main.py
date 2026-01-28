import sys
import os
import pygame
from mapspace import MapSpace

# Ensure the project root is on sys.path so absolute imports like `assets` resolve
# when running this script from the `main/` subfolder.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import variables as var
import enemies as enemies
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
map_image = pygame.image.load('assets/images/maps/dustbox.png').convert_alpha()
#enemy
foe_image = pygame.image.load('assets/images/enemies/foe1.png').convert_alpha()

#create map space (map menu pnding)
mapspace = MapSpace(map_image)

waypoint = [
    (100,100),
    (400,200),
    (400,100), 
    (200,300)
]

foe = enemies.Foe(waypoint, foe_image)
print(foe)

#create groups
foe_group = pygame.sprite.Group()
foe_group.add(foe)


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
    #draw path (use color from variables)
    pygame.draw.lines(screen, var.GREY0, False, waypoint, 3)

    #update groups
    foe_group.update()
    #draw groups
    foe_group.draw(screen)

   

    #Exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the display
    pygame.display.flip()

pygame.quit()
print("Game closed.")