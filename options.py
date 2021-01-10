"""Модуль с переменными и настройками"""
import pygame
from maze import *

SENSITIVITY = 0.02
FPS = 60
SIZE = WIDTH, HEIGHT = 1280, 820
CENTER = WIDTH // 2, HEIGHT // 2
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
font = pygame.font.SysFont("Console", 20)
PATHTIME = pygame.USEREVENT + 1
pygame.time.set_timer(PATHTIME, 100)


def update_fps():
    fps = 'FPS ' + str(int(clock.get_fps()))
    fps_text = font.render(fps, True, pygame.Color("White"))
    return fps_text

