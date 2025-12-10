import sys
import pygame
import assets.variables as var
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


#Player rectangle
player = pygame.Rect((300, 250, 50, 50))


# Game loop
running = True
while running:
    clock.tick(var.FPS)

   

    #Exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()