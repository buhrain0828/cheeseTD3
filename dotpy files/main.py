import sys
import os
import pygame
import json
from mapspace import MapSpace
from myce import Myce
import enemies
import variables as var
from buttons import Button
from allmycedata import MYCE_DATA

#make sure project root is on sys.path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def resource_path(relative_path):
    #use bundled temp dir when running from pyinstaller
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = PROJECT_ROOT
    return os.path.join(base_path, relative_path)

print(f'Running with {sys.executable}')

#selection variables
selected_myce = None
selected_myce_type = None
last_spawn_time = pygame.time.get_ticks()
show_myce_menu = False

#game state
started = False
fast_forward = False
game_over = False
game_win = 0  #-1 = loss, 1 = win


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((var.SCREEN_WIDTH + var.sidebar, var.SCREEN_HEIGHT))
pygame.display.set_caption("CheeseTD3")

#map
map_image = pygame.image.load(resource_path('assets/images/maps/teetrex.png')).convert_alpha()

#foe images
foe_images = {}
for foe_name, foe_path in {
    "easy": 'assets/images/enemies/black_cat_enemy.png',
    "medium": 'assets/images/enemies/brown_cat_enemy.png',
    "hard": 'assets/images/enemies/beige_cat_enemy.png',
    "harder": 'assets/images/enemies/blue_cat_enemy.png',
    "insane": 'assets/images/enemies/pink_cat_enemy.png',
    "demon": 'assets/images/enemies/white_cat_enemy.png',
}.items():
    foe_surface = pygame.image.load(resource_path(foe_path)).convert_alpha()
    foe_images[foe_name] = pygame.transform.scale(foe_surface, (64, 64))

#myce assets
myce_icon_size = (56, 56)
fastforward_size = (56, 56)

myce_assets = {}
for myce_type, myce_data in MYCE_DATA.items():
    #keep sheet and icon together for tower selection
    sheet = pygame.image.load(resource_path(myce_data["sheet_path"])).convert_alpha()
    icon = pygame.image.load(resource_path(myce_data["icon_path"])).convert_alpha()
    icon = pygame.transform.scale(icon, myce_icon_size)
    myce_assets[myce_type] = {
        "sheet": sheet,
        "icon": icon,
    }

cursor_myce = pygame.transform.scale(myce_assets["basic"]["icon"].copy(), (var.TileSize, var.TileSize))

#button images
place_myce_image = pygame.image.load(resource_path('assets/images/buttons/place_myce.png')).convert_alpha()
stop_sign_image = pygame.image.load(resource_path('assets/images/buttons/stop_sign.png')).convert_alpha()
startgameimg = pygame.image.load(resource_path('assets/images/buttons/startgame.png')).convert_alpha()
fastforwardimg = pygame.image.load(resource_path('assets/images/buttons/ff.png')).convert_alpha()
restartimg = pygame.image.load(resource_path('assets/images/buttons/restart.png')).convert_alpha()
button_size = (var.sidebar - 40, var.TileSize * 2)
place_myce_image = pygame.transform.scale(place_myce_image, button_size)
stop_sign_image = pygame.transform.scale(stop_sign_image, button_size)
startgameimg = pygame.transform.scale(startgameimg, button_size)
fastforwardimg = pygame.transform.scale(fastforwardimg, fastforward_size)
restartimg = pygame.transform.scale(restartimg, button_size)

#hud images
health_image = pygame.image.load(resource_path('assets/misc/heart.png')).convert_alpha()
health_image = pygame.transform.scale(health_image, (24, 24))
quesos_image = pygame.image.load(resource_path('assets/misc/quesos.png')).convert_alpha()
quesos_image = pygame.transform.scale(quesos_image, (24, 24))
text_font = pygame.font.SysFont("Consolas", 36, bold=True)
tooltip_font = pygame.font.SysFont("Consolas", 18, bold=True)

#print text to screen
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


def wrap_tooltip_text(text, font, max_width):
    #split tooltip text into lines that fit the box
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_tooltip(title, text, x, y):
    #wrap longer text so the tooltip stays compact
    body_lines = wrap_tooltip_text(text, tooltip_font, 180)
    lines = [title] + body_lines
    rendered_lines = [tooltip_font.render(line, True, "grey100") for line in lines]
    width = max(line.get_width() for line in rendered_lines) + 16
    height = sum(line.get_height() for line in rendered_lines) + 16

    #keep tooltip inside the game window
    max_x = screen.get_width() - width - 8
    max_y = screen.get_height() - height - 8
    x = min(max(8, x), max_x)
    y = min(max(8, y), max_y)

    tooltip_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (25, 25, 25), tooltip_rect, border_radius=8)
    pygame.draw.rect(screen, (180, 180, 180), tooltip_rect, 2, border_radius=8)

    text_y = y + 8
    for rendered_line in rendered_lines:
        screen.blit(rendered_line, (x + 8, text_y))
        text_y += rendered_line.get_height()


#load map data
try:
    with open(resource_path('tilesheets/teetrex..tmj')) as f:
        mapspace_data = json.load(f)
except Exception:
    mapspace_data = {'width': 10, 'height': 10, 'layers': []}


#create mapspace
mapspace = MapSpace(mapspace_data, map_image, var.SCREEN_WIDTH, var.SCREEN_HEIGHT)
mapspace.objprocess()
mapspace.process_spawn()

#groups
foe_group = pygame.sprite.Group()
myce_group = pygame.sprite.Group()

#center buttons horizontally inside the sidebar using their actual widths
sidebar_x = var.SCREEN_WIDTH
myce_x = sidebar_x + (var.sidebar - place_myce_image.get_width()) // 2
stop_x = sidebar_x + (var.sidebar - stop_sign_image.get_width()) // 2

#myce menu config (2x2 grid)
myce_menu_start_x = sidebar_x + 24
myce_menu_start_y = 180 + stop_sign_image.get_height() + 20
myce_menu_gap = 16
myce_menu_col_2_x = myce_menu_start_x + myce_icon_size[0] + myce_menu_gap
myce_menu_row_2_y = myce_menu_start_y + myce_icon_size[1] + myce_menu_gap

fast_forward_x = sidebar_x + var.sidebar - fastforwardimg.get_width() - 12
fast_forward_y = 12
start_button_y = 500
restart_button_y = 500


#initialise buttons
myce_button = Button(myce_x, 120, place_myce_image, True)
stop_button = Button(stop_x, 180, stop_sign_image, True)
start_button = Button(sidebar_x + (var.sidebar - startgameimg.get_width()) // 2, start_button_y, startgameimg, True)
fastforward_button = Button(fast_forward_x, fast_forward_y, fastforwardimg, False)
restart_button = Button(sidebar_x + (var.sidebar - restartimg.get_width()) // 2, restart_button_y, restartimg, True)

myce_menu_positions = {
    "basic": (myce_menu_start_x, myce_menu_start_y),
    "lumber": (myce_menu_col_2_x, myce_menu_start_y),
    "money": (myce_menu_start_x, myce_menu_row_2_y),
    "pumpkin": (myce_menu_col_2_x, myce_menu_row_2_y),
}

myce_menu_buttons = {}
for myce_type in MYCE_DATA:
    button_x, button_y = myce_menu_positions[myce_type]
    myce_menu_buttons[myce_type] = Button(button_x, button_y, myce_assets[myce_type]["icon"], True)


def spawnmyce():
    if selected_myce_type not in MYCE_DATA:
        return

    selected_stats = MYCE_DATA[selected_myce_type]
    selected_assets = myce_assets[selected_myce_type]
    mouse_x, mouse_y = pygame.mouse.get_pos()

    #ignore clicks outside playable map area
    if not (0 <= mouse_x < var.SCREEN_WIDTH and 0 <= mouse_y < var.SCREEN_HEIGHT):
        return

    #can't place anything until tile data exists
    if not mapspace.tilemap:
        return

    #convert mouse position into tile coords
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
    if mapspace.quesos < selected_stats["cost"]:
        return

    #center tower on clicked tile
    screen_x = tile_x * tile_width + tile_width / 2
    screen_y = tile_y * tile_height + tile_height / 2

    new_myce = Myce(
        tile_x,
        tile_y,
        selected_assets["sheet"],
        screen_x=screen_x,
        screen_y=screen_y,
        spacing=selected_stats["spacing"],
        target_width=60,
        damage=selected_stats["damage"],
        cooldown=selected_stats["cooldown"],
        aoe_radius=selected_stats["aoe_radius"],
    )

    mapspace.quesos -= selected_stats["cost"]
    myce_group.add(new_myce)


def check_selection(mouse_pos):
    #return the myce the player clicked on
    for myce in myce_group:
        if myce.rect.collidepoint(mouse_pos):
            return myce
    return None


def set_selected_myce(clicked_myce):
    global selected_myce

    #only one myce should show its range at a time
    selected_myce = clicked_myce
    for myce in myce_group:
        myce.select = myce is clicked_myce

#game loop
running = True

#track whether selected tower should follow cursor
drop_myce = False
while running:
    current_fps = var.FPS * 2 if fast_forward else var.FPS
    clock.tick(current_fps)

    #clear
    screen.fill(var.BACKGROUND_COLOR)

    #draw map
    mapspace.draw(screen)

    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if drop_myce:
                spawnmyce()
            elif event.pos[0] < var.SCREEN_WIDTH:
                #click a myce to show range, click empty map space to clear
                set_selected_myce(check_selection(event.pos))
    if not game_over:
        #check loss/win before next frame draws
        if mapspace.health <= 0:
            game_over = True
            game_win = -1 #lose
        elif mapspace.round > var.allrounds:
            game_over = True
            game_win = 1 #win

        #update
        myce_group.update(foe_group)
        foe_group.update(mapspace)

        #draw after map so everything stays visible
        foe_group.draw(screen)
        for myce in myce_group:
            myce.draw_range(screen)

    draw_words(str(mapspace.health), text_font, "grey100", 650, 5, health_image)
    draw_words(str(mapspace.quesos), text_font, "grey100", 650, 40, quesos_image)
    draw_words(f"Round:{mapspace.round}", text_font, "grey100", 650, 75, None)
    if not game_over:
        #check if game started
        if not started:
            if start_button.draw(screen):
                started = True
        else:
            if fastforward_button.draw(screen):
                fast_forward = not fast_forward

            spawn_delay = var.time_between_spawn // 2 if fast_forward else var.time_between_spawn

            #spawn foes
            if pygame.time.get_ticks() - last_spawn_time > spawn_delay:
                if mapspace.foes_spawned < len(mapspace.foe_list):
                    foe_type = mapspace.foe_list[mapspace.foes_spawned]
                    foe = enemies.Foe(foe_type, mapspace.wayp, foe_images)
                    foe_group.add(foe)
                    mapspace.foes_spawned += 1
                    last_spawn_time = pygame.time.get_ticks()
        #advance only after every foe is gone
        if mapspace.round_end_check():
            mapspace.quesos += var.quesoper_roundend
            mapspace.round += 1
            started = False
            last_spawn_time = pygame.time.get_ticks()
            mapspace.reset_round()
            mapspace.process_spawn()
        #draw ui buttons
        if myce_button.draw(screen):
            show_myce_menu = not show_myce_menu
            drop_myce = False

        if show_myce_menu:
            hovered_myce_type = None
            for myce_type, myce_button_option in myce_menu_buttons.items():
                if myce_button_option.draw(screen):
                    selected_myce_type = myce_type
                    cursor_myce = pygame.transform.scale(myce_assets[myce_type]["icon"].copy(), (var.TileSize, var.TileSize))
                    drop_myce = True
                    show_myce_menu = False
                    break

            mouse_pos = pygame.mouse.get_pos()
            for myce_type, myce_button_option in myce_menu_buttons.items():
                if myce_button_option.rect.collidepoint(mouse_pos):
                    hovered_myce_type = myce_type
                    break

            if hovered_myce_type is not None:
                tooltip_x = sidebar_x + 16
                tooltip_y = myce_menu_row_2_y + myce_icon_size[1] + 20
                draw_tooltip(
                    MYCE_DATA[hovered_myce_type]["label"],
                    MYCE_DATA[hovered_myce_type]["tooltip"],
                    tooltip_x,
                    tooltip_y,
                )
        #only show cancel button while myce placement is active
        if drop_myce:
            #current myce being placed follows cursor
            cursor_rect = cursor_myce.get_rect()
            cursor_pos = pygame.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= var.SCREEN_WIDTH:
                screen.blit(cursor_myce, cursor_rect)

            if stop_button.draw(screen):
                drop_myce = False
                show_myce_menu = False
                selected_myce_type = None
    #restart game if loss
    else:
        pygame.draw.rect(screen, "black",(200,200,400,200), border_radius = 30)
        if game_win == -1:
            draw_words("YOU LOST! :(", text_font, "grey100",310,230, None)
        elif game_win == 1:
            draw_words("YOU WON!", text_font, "grey100",315,230, None)
        if restart_button.draw(screen):
            game_over = False
            game_win = 0
            started = False
            fast_forward = False
            drop_myce = False
            selected_myce = None
            show_myce_menu = False
            selected_myce_type = None
            cursor_myce = pygame.transform.scale(myce_assets["basic"]["icon"].copy(), (var.TileSize, var.TileSize))
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

