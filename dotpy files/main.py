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

# selection variables
# currently selected myce, if any
selected_myce = None
last_spawn_time = pygame.time.get_ticks()
#game state
started = False
fast_forward = False
game_over = False
game_win = 0 #-1 = loss, 1 = win


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((var.SCREEN_WIDTH + var.sidebar, var.SCREEN_HEIGHT))
pygame.display.set_caption("CheeseTD3")

# map
map_image = pygame.image.load('assets/images/maps/teetrex.png').convert_alpha()

# foe images
foe_images = {}
for foe_name, foe_path in {
    "easy": 'assets/images/enemies/black_cat_enemy.png',
    "normal": 'assets/images/enemies/brown_cat_enemy.png',
    "hard": 'assets/images/enemies/beige_cat_enemy.png',
    "harder": 'assets/images/enemies/blue_cat_enemy.png',
    "insane": 'assets/images/enemies/pink_cat_enemy.png',
    "demon": 'assets/images/enemies/white_cat_enemy.png',
}.items():
    foe_surface = pygame.image.load(os.path.join(foe_path)).convert_alpha()
    foe_images[foe_name] = pygame.transform.scale(foe_surface, (64, 64))

# myce sprites
myce1sheet = pygame.image.load('assets/images/myce/sheets/myce1_shooting_spritesheet.png').convert_alpha()
lumbermyce = pygame.image.load('assets/images/myce/sheets/lumbermyce_shooting.png').convert_alpha()
moneymyce = pygame.image.load('assets/images/myce/sheets/money_mice_shooting.png').convert_alpha()
pumpkyce = pygame.image.load('assets/images/myce/sheets/pumpkyce_shooting.png').convert_alpha()
cursor_myce = pygame.image.load('assets/images/myce/sprites/myce1.png').convert_alpha()
cursor_myce = pygame.transform.scale(cursor_myce, (var.TileSize, var.TileSize))

# button images
place_myce_image = pygame.image.load('assets/images/buttons/place_myce.png').convert_alpha()
stop_sign_image = pygame.image.load('assets/images/buttons/stop_sign.png').convert_alpha()
startgameimg = pygame.image.load('assets/images/buttons/startgame.png').convert_alpha()
fastforwardimg = pygame.image.load('assets/images/buttons/ff.png').convert_alpha()
restartimg = pygame.image.load('assets/images/buttons/restart.png').convert_alpha()
button_size = (var.sidebar - 40, var.TileSize * 2)
place_myce_image = pygame.transform.scale(place_myce_image, button_size)
stop_sign_image = pygame.transform.scale(stop_sign_image, button_size)
startgameimg = pygame.transform.scale(startgameimg, button_size)
fastforwardimg = pygame.transform.scale(fastforwardimg, button_size)
restartimg = pygame.transform.scale(restartimg, button_size)

# HUD images
health_image = pygame.image.load('assets/misc/heart.png').convert_alpha()
health_image = pygame.transform.scale(health_image, (24, 24))
quesos_image = pygame.image.load('assets/misc/quesos.png').convert_alpha()
quesos_image = pygame.transform.scale(quesos_image, (24, 24))
text_font = pygame.font.SysFont("Consolas", 36, bold=True)

# print text to screen
def draw_words(text, font, colour, x, y, icon=None, space=1):
    if icon is not None:
        icon_rect = icon.get_rect()
        icon_rect.topleft = (x, y)
        screen.blit(icon, icon_rect)

        img = font.render(text, True, colour)
        text_y = y + (icon_rect.height - img.get_height()) // 2
        screen.blit(img, (x + icon_rect.width + space, text_y))
    else:
        img = font.render(text, True, colour)
        screen.blit(img, (x, y))


# load map data
try:
    with open('tilesheets/teetrex..tmj') as f:
        mapspace_data = json.load(f)
except Exception:
    mapspace_data = {'width': 10, 'height': 10, 'layers': []}


# create mapspace
mapspace = MapSpace(mapspace_data, map_image, var.SCREEN_WIDTH, var.SCREEN_HEIGHT)
mapspace.objprocess()
mapspace.process_spawn()

# groups
foe_group = pygame.sprite.Group()
myce_group = pygame.sprite.Group()

# center buttons horizontally inside the sidebar using their actual widths
sidebar_x = var.SCREEN_WIDTH
myce_x = sidebar_x + (var.sidebar - place_myce_image.get_width()) // 2
stop_x = sidebar_x + (var.sidebar - stop_sign_image.get_width()) // 2

# initialise buttons
myce_button = Button(myce_x, 120, place_myce_image, True)
stop_button = Button(stop_x, 180, stop_sign_image, True)
start_button = Button(sidebar_x + (var.sidebar - startgameimg.get_width()) // 2, 240, startgameimg, True)
fastforward_button = Button(sidebar_x + (var.sidebar - fastforwardimg.get_width()) // 2, 300, fastforwardimg, True)
restart_button = Button(270,300,restartimg,True)

def spawnmyce():
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Ignore clicks outside the playable map area.
    if not (0 <= mouse_x < var.SCREEN_WIDTH and 0 <= mouse_y < var.SCREEN_HEIGHT):
        return

    # A placement is not possible until tile data exists.
    if not mapspace.tilemap:
        return

    # Convert the mouse position into map tile coordinates.
    map_columns = mapspace.orig_width or var.Column
    map_rows = mapspace.orig_height or var.Row
    tile_width = mapspace.width / mapspace.orig_width if mapspace.orig_width else var.TileSize
    tile_height = mapspace.height / mapspace.orig_height if mapspace.orig_height else var.TileSize
    tile_x = int(mouse_x // tile_width)
    tile_y = int(mouse_y // tile_height)

    #reject tiles outside map bounds
    if not (0 <= tile_x < map_columns and 0 <= tile_y < map_rows):
        return

    tile_index = tile_y * map_columns + tile_x

    #reject invalid or non-buildable tiles
    if tile_index >= len(mapspace.tilemap):
        return
    if mapspace.tilemap[tile_index] != 142:
        return

    #prevent placing myce on same tile
    for existing_myce in myce_group:
        if existing_myce.tile_x == tile_x and existing_myce.tile_y == tile_y:
            return

    #affordability check
    if mapspace.quesos < var.cost_buy:
        return

    #center myce spawn placement
    screen_x = tile_x * tile_width + tile_width / 2
    screen_y = tile_y * tile_height + tile_height / 2

    new_myce = Myce(
        tile_x,
        tile_y,
        myce1sheet,
        screen_x=screen_x,
        screen_y=screen_y,
        target_width=60,
    )
    mapspace.quesos -= var.cost_buy
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
    if game_over == False:
        #check for loss
        if mapspace.health <= 0:
            game_over = True
            game_win = -1 #lose
        #check if win
        elif mapspace.round > var.allrounds:
            game_over = True
            game_win = 1 #win

        # update
        foe_group.update(mapspace)
        myce_group.update(foe_group)

        # draw (after map so visible)
        foe_group.draw(screen)
        for myce in myce_group:
            myce.draw_range(screen)

    draw_words(str(mapspace.health), text_font, "grey100", 650, 5, health_image)
    draw_words(str(mapspace.quesos), text_font, "grey100", 650, 40, quesos_image)
    draw_words(str("Round:" + str(mapspace.round)), text_font, "grey100", 650, 75, None)
    if not game_over:
        # check if game started
        if not started:
            if start_button.draw(screen):
                started = True
        else:
            # spawn foes
            if pygame.time.get_ticks() - last_spawn_time > var.time_between_spawn:
                if mapspace.foes_spawned < len(mapspace.foe_list):
                    foe_type = mapspace.foe_list[mapspace.foes_spawned]
                    foe = enemies.Foe(foe_type, mapspace.wayp, foe_images)
                    foe_group.add(foe)
                    mapspace.foes_spawned += 1
                    last_spawn_time = pygame.time.get_ticks()
        #check if wave ended
        if mapspace.round_end_check() == True:
            mapspace.quesos += var.quesoper_roundend
            mapspace.round += 1
            started = False
            last_spawn_time = pygame.time.get_ticks()
            mapspace.reset_round()
            mapspace.process_spawn()
        # draw UI buttons
        if myce_button.draw(screen):
            drop_myce = True

        # only show cancel button while myce placement is active
        if drop_myce:
            # current myce being placed follows cursor
            cursor_rect = cursor_myce.get_rect()
            cursor_pos = pygame.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= var.SCREEN_WIDTH:
                screen.blit(cursor_myce, cursor_rect)

            if stop_button.draw(screen):
                drop_myce = False
    #restart game if loss
    else:
        pygame.draw.rect(screen, "black",(200,200,400,200), border_radius = 30)
        if game_win == -1:
            draw_words("YOU LOST! :(", text_font, "grey100",310,230, None)
            #restart
        elif game_win == 1:
            draw_words("YOU WON!", text_font, "grey100",315,230, None)
        if restart_button.draw(screen):
            game_over = False
            game_win = 0
            started = False
            drop_myce = False
            selected_myce = None
            last_spawn_time = pygame.time.get_ticks()
            mapspace = MapSpace(mapspace_data, map_image, var.SCREEN_WIDTH, var.SCREEN_HEIGHT)
            mapspace.objprocess()
            mapspace.process_spawn()
            #empty groups
            foe_group.empty()
            myce_group.empty()

    pygame.display.flip()

pygame.quit()
print('Game closed.')

