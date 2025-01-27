import pygame

# conf tamanho da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Controle com Arduino")

# Cores
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# spedd
PLAYER_SPEED = 5
BULLET_SPEED = 7
OBSTACLE_SPEED = 3


#  relógio
clock = pygame.time.Clock()
