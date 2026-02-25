import sys
import os
import pygame
import json
from mapspace import MapSpace
from myce import Myce
import enemies
import variables as var

# Ensure project root on sys.path for relative asset imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f'Running with {sys.executable}')

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((var.SCREEN_WIDTH + var.sidebar, var.SCREEN_HEIGHT))
pygame.display.set_caption("CheeseTD3")

# safe asset loads
#map
try:
    map_image = pygame.image.load('assets/images/maps/teetrex.png').convert_alpha()
except Exception:
    map_image = pygame.Surface((var.SCREEN_WIDTH, var.SCREEN_HEIGHT))
    map_image.fill((0, 100, 0))
#boss
try:
    foe_image = pygame.image.load(os.path.join('assets/images/enemies/yarn_boss.gif')).convert_alpha()
except Exception:
    foe_image = pygame.Surface((var.TileSize, var.TileSize), pygame.SRCALPHA)
    pygame.draw.rect(foe_image, (255, 0, 0), foe_image.get_rect())
#myce
try:
    cursor_myce = pygame.image.load('assets/images/myce/myce1.png').convert_alpha()
except Exception:
    cursor_myce = pygame.Surface((var.TileSize, var.TileSize), pygame.SRCALPHA)
    pygame.draw.circle(cursor_myce, (255, 255, 0), (var.TileSize//2, var.TileSize//2), var.TileSize//2)
cursor_myce = pygame.transform.scale(cursor_myce, (var.TileSize, var.TileSize))
#buttons

# load map data
try:
    with open('tilesheets/teetrex..tmj') as f:
        mapspace_data = json.load(f)
except Exception:
    mapspace_data = {'width': 10, 'height': 10, 'layers': []}

# create mapspace
mapspace = MapSpace(mapspace_data, map_image, var.SCREEN_WIDTH, var.SCREEN_HEIGHT)
mapspace.objprocess()

# create foe
try:
    foe = enemies.Foe(mapspace.wayp, foe_image)
except Exception:
    foe = None

# groups
foe_group = pygame.sprite.Group()
if foe:
    foe_group.add(foe)
myce_group = pygame.sprite.Group()

def spawnmyce():
    mouse_pos = pygame.mouse.get_pos()
    mouse_tile_x = mouse_pos[0] // var.TileSize
    mouse_tile_y = mouse_pos[1] // var.TileSize
    #
    if 0 <= mouse_pos[0] < var.SCREEN_WIDTH and 0 <= mouse_pos[1] < var.SCREEN_HEIGHT:
        m = Myce(mouse_tile_x, mouse_tile_y, cursor_myce)
        myce_group.add(m)
        +

# Game loop
running = True
while running:
    clock.tick(var.FPS)

    # clear
    screen.fill(var.BACKGROUND_COLOR)

    # draw map
    mapspace.draw(screen)

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            spawnmyce()

    # update
    foe_group.update()
    myce_group.update()

    # draw (after map so visible)
    foe_group.draw(screen)
    myce_group.draw(screen)

    pygame.display.flip()

pygame.quit()
print('Game closed.')
