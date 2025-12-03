import sys
import pygame
#to run the code, use cd C:\Users\osabr\OneDrive\Documents\GitHub\cheeseTD3
#.\.venv\Scripts\Activate.ps1
#python main.py
print(f'Running with {sys.executable}')

# Initialize Pygame
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CheeseTD3")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()