import sys
import os
import pygame
import json
from mapspace import MapSpace
from myce import Myce
import enemies
import variables as var
from buttons import Button

# Ensure project root on sys.path for relative asset imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f'Running with {sys.executable}')
#selection variables
# currently selected myce, if any
selected_myce = None

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
    foe_types = {
        "easy": pygame.image.load(os.path.join('assets/images/enemies/black_cat_enemy.png')).convert_alpha(),
        "normal": pygame.image.load(os.path.join('assets/images/enemies/brown_cat_enemy.png')).convert_alpha(),
        "hard": pygame.image.load(os.path.join('assets/images/enemies/beige_cat_enemy.png')).convert_alpha(),
        "harder": pygame.image.load(os.path.join('assets/images/enemies/blue_cat_enemy.png')).convert_alpha(),
        "insane": pygame.image.load(os.path.join('assets/images/enemies/pink_cat_enemy.png')).convert_alpha(),
        "demon": pygame.image.load(os.path.join('assets/images/enemies/white_cat_enemy.png')).convert_alpha()
    }
    foe_image = pygame.transform.scale(foe_image,(64,64))
except Exception:
    foe_image = pygame.Surface((var.TileSize, var.TileSize), pygame.SRCALPHA)
    pygame.draw.rect(foe_image, (255, 0, 0), foe_image.get_rect())
#myce spritesheet
myce1sheet = pygame.image.load('assets/images/myce/sheets/myce1_shooting_spritesheet.png').convert_alpha()
#myce cursor image
try:
    cursor_myce = pygame.image.load('assets/images/myce/sprites/myce1.png').convert_alpha()
except Exception:
    cursor_myce = pygame.Surface((var.TileSize, var.TileSize), pygame.SRCALPHA)
    pygame.draw.circle(cursor_myce, (255, 255, 0), (var.TileSize//2, var.TileSize//2), var.TileSize//2)
cursor_myce = pygame.transform.scale(cursor_myce, (var.TileSize, var.TileSize))
#buttons
# load button images
place_myce_image = pygame.image.load('assets/images/buttons/place_myce.png').convert_alpha()
stop_sign_image = pygame.image.load('assets/images/buttons/stop_sign.png').convert_alpha()

# scale buttons while preserving aspect ratio so they don't look squished
# target the button height to 2 tiles and allow width to adjust accordingly
def _scale_preserve_to_height(img, target_h, max_w):
    w, h = img.get_size()
    if h == 0 or w == 0:
        return img
    scale = target_h / h
    new_w = int(w * scale)
    if new_w > max_w:
        scale = max_w / w
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return pygame.transform.smoothscale(img, new_size)

max_button_height = var.TileSize * 2
max_button_width = var.sidebar - 20
place_myce_image = _scale_preserve_to_height(place_myce_image, max_button_height, max_button_width)
stop_sign_image = _scale_preserve_to_height(stop_sign_image, max_button_height, max_button_width)


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
# center buttons horizontally inside the sidebar using their actual widths
sidebar_x = var.SCREEN_WIDTH
myce_x = sidebar_x + (var.sidebar - place_myce_image.get_width()) // 2
stop_x = sidebar_x + (var.sidebar - stop_sign_image.get_width()) // 2

#initialise buttons
myce_button = Button(myce_x, 120, place_myce_image, True)  # one_click=True for toggle behavior
stop_button = Button(stop_x, 180, stop_sign_image, True)



def spawnmyce():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # only handle clicks inside the map area
    if not (0 <= mouse_x < var.SCREEN_WIDTH and 0 <= mouse_y < var.SCREEN_HEIGHT):
        return

    # compute tile coordinates using scaled map dimensions
    tile_width = mapspace.width / mapspace.orig_width if mapspace.orig_width else var.TileSize
    tile_height = mapspace.height / mapspace.orig_height if mapspace.orig_height else var.TileSize
    clicked_tile = (int(mouse_x // tile_width), int(mouse_y // tile_height))
    clicked_tile_x, clicked_tile_y = clicked_tile

    map_columns = mapspace.orig_width or var.Column
    map_rows = mapspace.orig_height or var.Row
    # quick bounds check
    if clicked_tile_x < 0 or clicked_tile_x >= map_columns or clicked_tile_y < 0 or clicked_tile_y >= map_rows:
        return

    if not mapspace.tilemap:
        return
    tile_index = clicked_tile_y * map_columns + clicked_tile_x
    if tile_index >= len(mapspace.tilemap):
        return

    # only allow placement on grass
    if mapspace.tilemap[tile_index] != 142:
        return

    # avoid spawning too near an existing myce (by tile)
    for existing_myce in myce_group:
        existing_tile = (getattr(existing_myce, 'tile_x', None), getattr(existing_myce, 'tile_y', None))
        if existing_tile == clicked_tile:
            return

    new_myce = Myce(clicked_tile_x, clicked_tile_y, myce1sheet, screen_x=mouse_x, screen_y=mouse_y, target_width=60)
    #sprite doesn't overlap the sidebar area
    if new_myce.rect.right > var.SCREEN_WIDTH:
        new_myce.rect.right = var.SCREEN_WIDTH
        new_myce.x = new_myce.rect.centerx
    #similarly guard left edge (shouldn't trigger normally)
    if new_myce.rect.left < 0:
        new_myce.rect.left = 0
        new_myce.x = new_myce.rect.centerx
    myce_group.add(new_myce)

def check_selection(mouse_pos):
    # return the myce the player clicked on
    for myce in myce_group:
        if myce.rect.collidepoint(mouse_pos):
            return myce
    return None


def set_selected_myce(clicked_myce):
    global selected_myce

    # only one myce should show its range at a time
    selected_myce = clicked_myce
    for myce in myce_group:
        myce.select = myce is clicked_myce

# Game loop
running = True
# track whether we are in placement mode
drop_myce = False
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
            if drop_myce:
                spawnmyce()
            elif event.pos[0] < var.SCREEN_WIDTH:
                # click a myce to show range, click empty map space to clear
                set_selected_myce(check_selection(event.pos))

    # update
    foe_group.update()
    myce_group.update(foe_group)

    # draw (after map so visible)
    foe_group.draw(screen)
    for myce in myce_group:
        myce.draw_range(screen)

    # draw UI buttons
    if myce_button.draw(screen):
        drop_myce = True
    #only show cancel button while myce placement is active
    if drop_myce == True:
        #current myce being placed follows cursor
        cursor_rect = cursor_myce.get_rect()
        cursor_pos = pygame.mouse.get_pos()
        cursor_rect.center = cursor_pos
        if cursor_pos[0] <= var.SCREEN_WIDTH:
           screen.blit(cursor_myce, cursor_rect)
        
        if stop_button.draw(screen):
            drop_myce = False


    pygame.display.flip()

pygame.quit()
print('Game closed.')

