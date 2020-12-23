import pygame
from maze import *

FPS = 60
SIZE = WIDTH, HEIGHT = 820, 820
CELL_W = 20
SPEED = 2
MAZE_S = 20
pygame.init()
pygame.display.set_caption('Лабиринт')
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
maze = Maze(MAZE_S, MAZE_S).get_maze()
####################
all_groups = pygame.sprite.Group()
walls_groups = pygame.sprite.Group()
doors_groups = pygame.sprite.Group()
player_group = pygame.sprite.Group()
