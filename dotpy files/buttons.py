import pygame 

class Button():
    def __init__(self, xpos, ypos, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (xpos, ypos)

    def draw(self, surface):
        """Draw the button to the given surface and handle hover/click logic."""
        # mouse position
        pos = pygame.mouse.get_pos()

        # click condition (placeholder for future behavior)
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                pass

        # draw button image
        surface.blit(self.image, self.rect)