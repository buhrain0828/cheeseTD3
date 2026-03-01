import pygame 

class Button():
    def __init__(self, xpos, ypos, image, one_click):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (xpos, ypos)
        self.click = False
        self.one_click = one_click

    def draw(self, surface):
        #draw button and handle click
        #action on click
        active = False

        # mouse position
        pos = pygame.mouse.get_pos()

        # click condition (placeholder for future behavior)
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                active = True
                self.click = True
            #if button is one click
            if self.one_click:
                self.click = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.click = False

        # draw button image
        surface.blit(self.image, self.rect)
        return active