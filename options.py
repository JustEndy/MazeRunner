"""Модуль с переменными и настройками"""
import pygame
from maze import *
from os import path as ospath
from sys import exit as sysexit

# GAME SETTINGS
SENSITIVITY = 0.04
BTN_F = pygame.K_w
BTN_L = pygame.K_a
BTN_R = pygame.K_d
BTN_B = pygame.K_s
BTN_INTERACT = pygame.K_e
SIZE = WIDTH, HEIGHT = 1280, 720
SEED = randint(0, 999999)
SEED = 2
###################
# Должно быть чётным, иначе генератор падает
MAZE_S = 14
FPS = 60
CENTER = WIDTH // 2, HEIGHT // 2
CELL_W = round(HEIGHT / (MAZE_S * 2 + 1))
SPEED = 2
SCORE = 0
pygame.init()
pygame.display.set_caption('Maze Runner | Work in Progress')
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
maze = Maze(MAZE_S, MAZE_S).get_maze()
####################
all_groups = pygame.sprite.Group()
walls_groups = pygame.sprite.Group()
doors_groups = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sg_group = pygame.sprite.Group()
####################
PATHTIME = pygame.USEREVENT + 1
pygame.time.set_timer(PATHTIME, 100)
####################
pause_font = pygame.font.SysFont("Bahnschrift SemiBold", 100, True)
debug_font = pygame.font.SysFont("Console", 20)
interact_font = pygame.font.SysFont("Bahnschrift SemiBold", 50, True)


def update_fps():
    fps = 'FPS ' + str(int(clock.get_fps()))
    fps_text = debug_font.render(fps, True, pygame.Color("White"))
    return fps_text


def pause_banners():
    banner = pygame.Surface((WIDTH, HEIGHT))
    final = pygame.Surface((WIDTH, HEIGHT))
    final.fill((0, 0, 0))
    final.set_colorkey((0, 0, 0))
    banner.fill((0, 0, 0))
    banner.set_alpha(125)
    text = pause_font.render('PAUSED', False, (0, 0, 0))
    pygame.draw.rect(final, (255, 255, 255), (HEIGHT // 2 - text.get_width() // 2 - 20,
                                              HEIGHT // 2 - text.get_height() // 2 - 20,
                                              text.get_width() + 40, text.get_height() + 40))
    final.blit(text, (HEIGHT // 2 - text.get_width() // 2,
                       HEIGHT // 2 - text.get_height() // 2))
    return banner, final


def load_image(name, colorkey=None):
    fullname = ospath.join('data', name)
    # если файл не существует, то выходим
    if not ospath.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sysexit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

