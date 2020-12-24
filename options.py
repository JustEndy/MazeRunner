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
enemy_group = pygame.sprite.Group()
####################
font = pygame.font.SysFont("Console", 18)
PATHTIME = pygame.USEREVENT + 1
pygame.time.set_timer(PATHTIME, 100)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, True, pygame.Color("Red"))
    return fps_text
