import pygame
class MapSpace():
    def __init__(self, data, map_image, width, height):
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
        
    def draw(self, surface):
        surface.blit(self.image, (0, 0))
        
    def objprocess(self):
        #retrieve waypoints from json data
        for layer in self.mapspace_data['layers']:
            if layer["name"] == "waypoint":
                for object in layer["objects"]:
                    obj_x = object.get("x", 0)
                    obj_y = object.get("y", 0)
                    wayp_data = object.get("polyline", [])
                    self.wayp_process(wayp_data, obj_x, obj_y)
                    
    def wayp_process(self, data, obj_x, obj_y):
        #find x and y coords and apply object offset and scaling
        for point in data:
            prov_x = (point.get("x", 0) + obj_x) * self.scale_x
            prov_y = (point.get("y", 0) + obj_y) * self.scale_y
            self.wayp.append((prov_x, prov_y))

    