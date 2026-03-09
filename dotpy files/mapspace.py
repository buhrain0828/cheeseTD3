import pygame
from allfoedata import FOE_SPAWN_DATA
import variables as var
class MapSpace():
    def __init__(self, data, map_image, width, height):
        self.tilemap = []
        self.wayp = []
        self.width = width
        self.height = height
        self.image = pygame.transform.scale(map_image, (width, height))
        self.mapspace_data = data
        # Get original map dimensions from the data
        self.orig_width = data.get('width', 1)
        self.orig_height = data.get('height', 1)
        # Calculate scale factor
        self.scale_x = width / (self.orig_width * data.get('tilewidth', 1))
        self.scale_y = height / (self.orig_height * data.get('tileheight', 1))
        self.round = 1
        self.foe_list = []
        self.health = var.health
        self.quesos = var.quesos
        self.foes_killed = 0
        self.foes_spawned = 0
        self.foes_missed = 0
        
    def draw(self, surface):
        surface.blit(self.image, (0, 0))

    def process_spawn(self):
        foes = FOE_SPAWN_DATA[self.round - 1]
        for foe_type in foes:
            foes_to_spawn = foes[foe_type]
            for foe in range(foes_to_spawn):
                self.foe_list.append(foe_type)

    def round_end_check(self):
        if (self.foes_killed + self.foes_missed) >= len(self.foe_list):
            return True

    def reset_round(self):
        #reset variables
        self.foe_list = []
        self.foes_killed = 0
        self.foes_missed = 0
        self.foes_spawned = 0

    def objprocess(self):
        # retrieve waypoints and tile data from json layers
        for layer in self.mapspace_data.get('layers', []):
            lname = layer.get('name', '')
            ltype = layer.get('type', '')
            # if it's a tile layer, grab its data regardless of the name
            if ltype == 'tilelayer':
                self.tilemap = layer.get('data', [])
            elif lname == 'waypoint' or ltype == 'objectgroup':
                for obj in layer.get('objects', []):
                    obj_x = obj.get('x', 0)
                    obj_y = obj.get('y', 0)
                    wayp_data = obj.get('polyline', [])
                    self.wayp_process(wayp_data, obj_x, obj_y)

    def wayp_process(self, data, obj_x, obj_y):
        #find x and y coords and apply object offset and scaling
        for point in data:
            prov_x = (point.get("x", 0) + obj_x) * self.scale_x
            prov_y = (point.get("y", 0) + obj_y) * self.scale_y
            self.wayp.append((prov_x, prov_y))

    