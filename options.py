"""Модуль с переменными и настройками"""
import pygame
from maze import *
from os import path as ospath
from sys import exit as sysexit

# GAME SETTINGS
if ospath.isfile('settings.txt'):
    with open("settings.txt", 'r') as f:
        file = f.readlines()
        SENSITIVITY = float(file[0].strip('\n').split('=')[1])
        BTN_F = eval(f"pygame.K_{file[1][:-1].split('=')[1]}")
        BTN_L = eval(f"pygame.K_{file[2][:-1].split('=')[1]}")
        BTN_R = eval(f"pygame.K_{file[3][:-1].split('=')[1]}")
        BTN_B = eval(f"pygame.K_{file[4][:-1].split('=')[1]}")
        BTN_INTERACT = eval(f"pygame.K_{file[5][:-1].split('=')[1]}")
        WIDTH = int(file[6].strip('\n').split('=')[1])
        HEIGHT = int(file[7].strip('\n').split('=')[1])
        seed = file[8].strip('\n').split('=')[1]
        SEED = randint(0, 999999) if seed == 'random' else seed
else:
    SENSITIVITY = 0.04
    BTN_F = pygame.K_w
    BTN_L = pygame.K_a
    BTN_R = pygame.K_d
    BTN_B = pygame.K_s
    BTN_INTERACT = pygame.K_e
    WIDTH, HEIGHT = 1280, 720
    SEED = randint(0, 999999)
    with open("settings.txt", 'w') as f:
        f.write('SENSITIVITY=0.04\n')
        f.write('BTN_F=w\n')
        f.write('BTN_L=a\n')
        f.write('BTN_R=d\n')
        f.write('BTN_B=s\n')
        f.write('BTN_INTERACT=e\n')
        f.write('WIDTH=1280\n')
        f.write('HEIGHT=720\n')
        f.write('SEED=random')
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
RECT_GAME_WINDOW = pygame.Rect(0, 0, round(WIDTH / 3 * 2), HEIGHT)
####################
all_groups = pygame.sprite.Group()
walls_groups = pygame.sprite.Group()
doors_groups = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sg_group = pygame.sprite.Group()
####################
PATHTIME = pygame.USEREVENT + 1
HEARTBEAT = pygame.USEREVENT + 0
pygame.time.set_timer(PATHTIME, 100)
pygame.time.set_timer(HEARTBEAT, 100)
####################
pause_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 7.2), True)
btn_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 14.4), True)
debug_font = pygame.font.SysFont("Console", round(HEIGHT / 36))


def load_image(name, colorkey=None):
    fullname = ospath.join('data', 'sprites', name)
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


def load_sound(name):
    fullname = ospath.join('data', 'sounds', name)
    if not ospath.isfile(fullname):
        print(f"Звук с изображением '{fullname}' не найден")
        sysexit()
    return pygame.mixer.Sound(fullname)


BTN_SOUND = load_sound('btn_click.wav')
HEART_S = load_sound('heart_s.wav')
GAME_BG = load_image('game_bg.png')
MENU_BG = load_image('menu_bg.png')
BLANK = load_image('btn_blank.png')
NOIMAGE = load_image('noimage.png')
###################################


def update_fps():
    fps = 'FPS ' + str(int(clock.get_fps()))
    fps_text = debug_font.render(fps, True, pygame.Color("White"))
    screen.blit(fps_text, (WIDTH - fps_text.get_width(), 0))


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
    screen.blit(pygame.transform.scale(MENU_BG, (RECT_MENU.w, RECT_MENU.h)), (RECT_MENU.x, RECT_MENU.y))
    screen.blit(pygame.transform.scale(BLANK, (RECT_PLAY.w, RECT_PLAY.h)), (RECT_PLAY.x, RECT_PLAY.y))
    screen.blit(pygame.transform.scale(BLANK, (RECT_SETTINGS.w, RECT_SETTINGS.h)), (RECT_SETTINGS.x, RECT_SETTINGS.y))
    screen.blit(pygame.transform.scale(BLANK, (RECT_EXIT.w, RECT_EXIT.h)), (RECT_EXIT.x, RECT_EXIT.y))

    text = ['', '', '']
    rects = [RECT_PLAY, RECT_SETTINGS, RECT_EXIT]
    if from_where == 'menu':
        text = ['PLAY', 'SETTINGS', 'EXIT GAME']
    elif from_where == 'choose_session':
        text = ['FREE RUN', 'TUTORIAL', 'MENU']
    elif from_where == 'game':
        text = ['RETURN', 'SETTINGS', 'EXIT']
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
                    BTN_SOUND.play()
                    return True, True, False
                elif RECT_SETTINGS.collidepoint(event.pos):
                    BTN_SOUND.play()
                elif RECT_EXIT.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return True, False, False

        pygame.display.flip()
