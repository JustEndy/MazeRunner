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
###################
# Должно быть чётным, иначе генератор падает
MAZE_S = 14
FPS = 60
CENTER = WIDTH // 2, HEIGHT // 2
CELL_W = round(HEIGHT / (MAZE_S * 2 + 1))
SPEED = HEIGHT / 360
SCORE = 0
pygame.init()
pygame.display.set_caption('Maze Runner | Work in Progress')
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
maze = Maze(MAZE_S, MAZE_S).get_maze()
####################
menu_x, width_x = round(WIDTH / 3 * 2), WIDTH - round(WIDTH / 3 * 2)
RECT_MENU = pygame.Rect(menu_x, 0, width_x, HEIGHT)
menu_x, menu_y = round(menu_x + menu_x * 0.075), round(HEIGHT / 3 + HEIGHT / 3 * 0.25)
width_x, width_y = round(width_x - width_x * 0.3), round(HEIGHT / 3 * 0.3)
RECT_PLAY = pygame.Rect(menu_x, menu_y, width_x, width_y)
RECT_SETTINGS = pygame.Rect(menu_x, menu_y + round(HEIGHT / 3 * 0.5), width_x, width_y)
RECT_EXIT = pygame.Rect(menu_x, menu_y + round(HEIGHT / 3), width_x, width_y)
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
pause_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 7.2), True)
btn_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 14.4), True)
debug_font = pygame.font.SysFont("Console", round(HEIGHT / 36))


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


NOIMAGE = load_image('noimage.png')
###################################


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


def work_with_menu(from_where=''):
    """Отрисовка кнопок меню"""
    pygame.draw.rect(screen, (155, 155, 155), RECT_MENU)
    pygame.draw.rect(screen, (55, 155, 55), RECT_PLAY)
    pygame.draw.rect(screen, (55, 55, 155), RECT_SETTINGS)
    pygame.draw.rect(screen, (155, 55, 55), RECT_EXIT)

    text = ['', '', '']
    rects = [RECT_PLAY, RECT_SETTINGS, RECT_EXIT]
    if from_where == 'menu':
        text = ['PLAY', 'SETTINGS', 'EXIT GAME']
    elif from_where == 'choose_session':
        text = ['FREE RUN', 'TUTORIAL', 'MENU']
    elif from_where == 'game':
        text = ['RETURN', 'SETTINGS', 'MENU']
    for btn in range(3):
        btnB_1 = btn_font.render(text[btn], True, pygame.Color("Black"))
        btnW_1 = btn_font.render(text[btn], True, pygame.Color("White"))
        screen.blit(btnB_1, (rects[btn][0] + rects[btn][2] // 2 - btnB_1.get_width() // 2,
                             rects[btn][1] + rects[btn][3] // 2 - btnB_1.get_height() // 2 + btnB_1.get_height() * 0.1))
        screen.blit(btnW_1, (rects[btn][0] + rects[btn][2] // 2 - btnW_1.get_width() // 2,
                             rects[btn][1] + rects[btn][3] // 2 - btnW_1.get_height() // 2))

    # Подсветка кнопок в меню
    m_pos = pygame.mouse.get_pos()
    if RECT_PLAY.collidepoint(m_pos):
        pygame.draw.rect(screen, (255, 255, 153), RECT_PLAY, round(HEIGHT / 240))
    elif RECT_SETTINGS.collidepoint(m_pos):
        pygame.draw.rect(screen, (255, 255, 153), RECT_SETTINGS, round(HEIGHT / 240))
    elif RECT_EXIT.collidepoint(m_pos):
        pygame.draw.rect(screen, (255, 255, 153), RECT_EXIT, round(HEIGHT / 240))


def choose_session():
    """Выбор режима игры"""
    menu = True
    while menu:
        screen.fill((0, 0, 0))

        # Картинка с лого
        screen.blit(pygame.transform.scale(NOIMAGE, (round(WIDTH / 3 * 2),
                                                     HEIGHT)), (0, 0))
        work_with_menu('choose_session')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False, False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    return True, True, False
                elif RECT_EXIT.collidepoint(event.pos):
                    return True, False, False

        pygame.display.flip()

