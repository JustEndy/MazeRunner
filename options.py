"""Модуль с переменными и настройками"""
import pygame
from maze import *
from os import path as ospath
from sys import exit as sysexit
import math

# GAME SETTINGS
if ospath.isfile('settings.txt'):
    with open("settings.txt", 'r') as f:
        file = f.readlines()
        option_list = [file[element].strip('\n').split('=')[1] for element in range(8)]
        SENSITIVITY = int(option_list[0])
        BTN_F = eval(f"pygame.K_{option_list[1]}")
        BTN_L = eval(f"pygame.K_{option_list[2]}")
        BTN_R = eval(f"pygame.K_{option_list[3]}")
        BTN_B = eval(f"pygame.K_{option_list[4]}")
        BTN_INTERACT = eval(f"pygame.K_{option_list[5]}")
        INTERACT_UNICODE = option_list[5].upper()
        WIDTH = int(option_list[6])
        HEIGHT = int(option_list[7])
else:
    SENSITIVITY = 50
    BTN_F = pygame.K_w
    BTN_L = pygame.K_a
    BTN_R = pygame.K_d
    BTN_B = pygame.K_s
    BTN_INTERACT = pygame.K_e
    INTERACT_UNICODE = 'E'
    WIDTH, HEIGHT = 1280, 720
    with open("settings.txt", 'w') as f:
        f.write('SENSITIVITY=50\n')
        f.write('BTN_F=w\n')
        f.write('BTN_L=a\n')
        f.write('BTN_R=d\n')
        f.write('BTN_B=s\n')
        f.write('BTN_INTERACT=e\n')
        f.write('WIDTH=1280\n')
        f.write('HEIGHT=720\n')
SEED = randint(0, 999999)
###################
# Должно быть чётным, иначе генератор падает
MAZE_S = 14
FPS = 60
CENTER = WIDTH // 2, HEIGHT // 2
CELL_W = round(HEIGHT / (MAZE_S * 2 + 1))
SPEED = HEIGHT / 360 * 0.5
SCORE = 0
pygame.init()
pygame.display.set_caption('Maze: Runner')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
maze = Maze(MAZE_S, MAZE_S).get_maze()
####################
### RAY CAST ###
NUM_RAYS = 400
FAKE_RAYS = 100
FAKE_RAYS_RANGE = NUM_RAYS - 1 + 2 * FAKE_RAYS
DEPTH = 300
SCALE = round(WIDTH / 3 * 2 / NUM_RAYS)
GAME_WIN = SCALE * NUM_RAYS
RECT_MENU = pygame.Rect(GAME_WIN, 0, WIDTH - GAME_WIN, HEIGHT)
menu_x, menu_y = round(RECT_MENU.x + RECT_MENU.w * 0.15), round(HEIGHT / 3 + HEIGHT / 3 * 0.25)
width_x, width_y = round(RECT_MENU.w - RECT_MENU.w * 0.3), round(HEIGHT / 3 * 0.3)
RECT_PLAY = pygame.Rect(menu_x, menu_y, width_x, width_y)
RECT_SETTINGS = pygame.Rect(menu_x, menu_y + round(HEIGHT / 3 * 0.5), width_x, width_y)
RECT_EXIT = pygame.Rect(menu_x, menu_y + round(HEIGHT / 3), width_x, width_y)
RECT_GAME_WINDOW = pygame.Rect(0, 0, GAME_WIN, HEIGHT)
####################
all_groups = pygame.sprite.Group()
walls_groups = pygame.sprite.Group()
doors_groups = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sg_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
meat_group = pygame.sprite.Group()
####################
PATHTIME = pygame.USEREVENT + 1
HEARTBEAT = pygame.USEREVENT + 0
ITEMSPAWN = pygame.USEREVENT + 2
pygame.time.set_timer(ITEMSPAWN, 1000)
pygame.time.set_timer(PATHTIME, 100)
pygame.time.set_timer(HEARTBEAT, 100)
####################
pause_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 7.2), True)
btn_font = pygame.font.SysFont("Bahnschrift SemiBold", round(HEIGHT / 14.4), True)
debug_font = pygame.font.SysFont("Console", round(HEIGHT / 36))
seed_font = pygame.font.SysFont("NSimSun", round(HEIGHT / 26))
########
# DEBUG
DO2D = False


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


def load_sound(name, value=None):
    fullname = ospath.join('data', 'sounds', name)
    if not ospath.isfile(fullname):
        print(f"Звук с изображением '{fullname}' не найден")
        sysexit()
    sound = pygame.mixer.Sound(fullname)
    if value is not None:
        sound.set_volume(value)
    return sound


DOOR_SOUND = load_sound('door.wav')
SCORE_SOUND = load_sound('score.wav')
PICKUP = load_sound('pickup.wav')
STEP = load_sound('step.wav', value=0.2)
BTN_SOUND = load_sound('btn_click.wav')
CHOCK_SOUND = load_sound('chocolate.wav')
BELL_SOUND = load_sound('bell.wav')
HEART_S = load_sound('heart_s.wav')
MEAT_SOUND = load_sound('meat.wav')
GAME_BG = load_image('game_bg.png')
MENU_BG = load_image('menu_bg.png')
BLANK = load_image('btn_blank.png')
NOIMAGE = load_image('noimage.png')
SETTINGS_BG = load_image('settings_bg.png')
BLANK_BAR = load_image('bar_blank.png')
LOGO = load_image('logo.png')

pygame.display.set_icon(load_image('door.png'))
###
T_W = 128
T_H = 128
T_SCALE = T_W / CELL_W
WALLS = {0: load_image('wall.png'),
         2: load_image('door.png'),
         3: load_image('door1.png')}
###################################


class Sprite:
    def __init__(self, image, static, pos, shift, scale, angle=0):
        self.angle = angle
        self.image = image
        self.static = static
        self.pos = self.x, self.y = pos
        self.shift = shift
        self.scale = scale
        if not static:
            self.sprite_angles = [frozenset(range(i, i + 45)) for i in range(0, 360, 45)]
            self.sprite_positions = {angle: pos for angle, pos in zip(self.sprite_angles, self.image)}

    def locate(self, player, walls):
        d = NUM_RAYS / (2 * math.tan(player.fov / 2))
        dy, dx = self.x - player.x + player.rect.w / 2, self.y - player.y + player.rect.h / 2
        distance = math.sqrt(dx**2 + dy**2)

        theta = math.atan2(dx, dy)
        gamma = theta - player.angle
        if dy > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += math.pi * 2

        delta_rays = int(gamma / player.delta_a)
        cur_ray = (delta_rays + NUM_RAYS // 2)
        distance *= math.cos(player.fov // 2 * cur_ray * player.delta_a)

        fake_walls = [walls[0] for _ in range(100)] + walls + [walls[-1] for _ in range(100)]
        fake_ray = cur_ray + FAKE_RAYS
        if 0 <= fake_ray <= FAKE_RAYS_RANGE and distance > 10:
            h = min(int(1.5 * d * CELL_W / distance * self.scale), int(HEIGHT / 0.6))
            shift = h // 2 * self.shift

            if not self.static:
                if theta < 0:
                    theta += math.pi * 2
                theta = int(math.degrees(theta) + 22 - self.angle) % 360

                for angles in self.sprite_angles:
                    if theta in angles:
                        self.image = self.sprite_positions[angles]
                        break
                else:
                    self.image = self.sprite_positions[self.sprite_angles[0]]

            pos = (cur_ray * SCALE - h // 2, HEIGHT // 2 - h // 2 + shift)
            sprite = pygame.transform.scale(self.image, (h, h))
            return distance, sprite, pos
        return (False,)


class StaminaBar:
    def __init__(self):
        self.image = pygame.transform.scale(BLANK_BAR, (round(RECT_MENU.w / 5 * 4), round(WIDTH / 25.6)))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = RECT_MENU.x + RECT_MENU.w // 2 - self.rect.w // 2, HEIGHT // 5 - self.rect.h * 0.5
        self.stamina = FPS * 2

    def update(self, value):
        self.stamina += value
        if self.stamina > FPS * 2:
            self.stamina = FPS * 2
        elif self.stamina < 0:
            self.stamina = 0

    def draw(self):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (153, 153, 153), (self.rect.x, self.rect.y,
                                                   round(self.rect.w * self.stamina / FPS / 2), self.rect.h))
        screen.blit(self.image, (self.rect.x, self.rect.y))
        outline = seed_font.render('STAMINA', True, pygame.Color("Black"))
        btnW_1 = seed_font.render('STAMINA', True, pygame.Color("White"))
        out_v = round(HEIGHT / 240)
        offsets = [(ox, oy)
                   for ox in range(-out_v, 2 * out_v, out_v)
                   for oy in range(-out_v, 2 * out_v, out_v)
                   if ox != 0 or oy != 0]
        px, py = (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                  self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2)
        for ox, oy in offsets:
            screen.blit(outline, (px + ox, py + oy))
        screen.blit(btnW_1, (px, py))


class ScoreBar:
    def __init__(self):
        self.image = pygame.transform.scale(BLANK_BAR, (round(RECT_MENU.w / 5 * 4), round(WIDTH / 25.6)))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = RECT_MENU.x + RECT_MENU.w // 2 - self.rect.w // 2, HEIGHT // 5 - self.rect.h * 2
        self.score = 0

    def update(self, value):
        if value > 0:
            self.score += value if self.score + value <= 5 else 0
        else:
            self.score += value if self.score + value >= 0 else 0

    def draw(self):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (153, 153, 153), (self.rect.x, self.rect.y,
                                                   round(self.rect.w * self.score / 10 * 2), self.rect.h))
        screen.blit(self.image, (self.rect.x, self.rect.y))
        outline = seed_font.render('SCORE', True, pygame.Color("Black"))
        btnW_1 = seed_font.render('SCORE', True, pygame.Color("White"))
        out_v = round(HEIGHT / 240)
        offsets = [(ox, oy)
                   for ox in range(-out_v, 2 * out_v, out_v)
                   for oy in range(-out_v, 2 * out_v, out_v)
                   if ox != 0 or oy != 0]
        px, py = (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                  self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2)
        for ox, oy in offsets:
            screen.blit(outline, (px + ox, py + oy))
        screen.blit(btnW_1, (px, py))


class InputBar:
    def __init__(self, x, y, seed):
        self.image = pygame.transform.scale(BLANK_BAR, (round(RECT_MENU.w / 5 * 4), round(WIDTH / 25.6)))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - self.rect.w // 2, y
        self.activated = False
        self.seed = str(seed)

    def draw(self):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        screen.blit(self.image, (self.rect.x, self.rect.y))
        btnW_1 = seed_font.render(self.seed, True, pygame.Color("White"))
        screen.blit(btnW_1, (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                             self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2))
        if self.activated:
            pygame.draw.rect(screen, (153, 255, 153), self.rect, round(HEIGHT / 240))
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (255, 255, 153), self.rect, round(HEIGHT / 240))

    def change_seed(self, event):
        if event.key == pygame.K_BACKSPACE:
            if len(self.seed) > 0:
                self.seed = self.seed[:-1]
        elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
            self.activated = False
        else:
            if len(self.seed) < 6:
                self.seed += event.unicode


SEED_BAR = InputBar(RECT_MENU.x + RECT_MENU.w // 2, round(HEIGHT / 4), SEED)
##################


def game_over_message(player):
    if player is None:
        return
    if not (player.win or player.lost):
        return

    if player.win:
        text = pause_font.render('YOU WON', False, (153, 255, 153))
    elif player.lost:
        text = pause_font.render('YOU LOST', False, (145, 0, 0))

    bg = pygame.transform.scale(load_image('settings_bg_1.png'), (round(GAME_WIN / 1.05), round(HEIGHT / 1.5)))
    bg_rect = bg.get_rect()
    bg_rect.x, bg_rect.y = round(GAME_WIN / 2 - bg.get_width() / 2), round(HEIGHT / 2 - bg.get_height() / 2)
    menu = True
    while menu:
        screen.fill((0, 0, 0))

        # Картинка с лого
        screen.blit(pygame.transform.scale(LOGO, (RECT_GAME_WINDOW.w,
                                                  HEIGHT)), (0, 0))

        # Отрисовка элементов
        screen.blit(bg, bg_rect.topleft)
        screen.blit(text, (bg_rect.x + bg_rect.w // 2 - text.get_width() // 2,
                           bg_rect.y + bg_rect.h // 2 - text.get_height() // 2))

        work_with_menu('game_over')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    BTN_SOUND.play()
                    return None

        pygame.display.flip()


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

    text = ['', '', '']
    rects = [RECT_PLAY, RECT_SETTINGS, RECT_EXIT]
    if from_where == 'menu':
        text = ['PLAY', 'SETTINGS', 'EXIT GAME']
    elif from_where == 'choose_session':
        text = ['RUN', 'MENU']
    elif from_where == 'game':
        text = ['RETURN', 'SETTINGS', 'EXIT']
    elif from_where == 'settings':
        text = ['SAVE', 'BACK']
    elif from_where == 'game_over':
        text = ['OK']

    m_pos = pygame.mouse.get_pos()
    for btn in range(len(text)):
        screen.blit(pygame.transform.scale(BLANK, (rects[btn].w, rects[btn].h)), (rects[btn].x, rects[btn].y))
        btnB_1 = btn_font.render(text[btn], True, pygame.Color("Black"))
        btnW_1 = btn_font.render(text[btn], True, pygame.Color("White"))
        screen.blit(btnB_1, (rects[btn][0] + rects[btn][2] // 2 - btnB_1.get_width() // 2,
                             rects[btn][1] + rects[btn][3] // 2 - btnB_1.get_height() // 2 + btnB_1.get_height() * 0.1))
        screen.blit(btnW_1, (rects[btn][0] + rects[btn][2] // 2 - btnW_1.get_width() // 2,
                             rects[btn][1] + rects[btn][3] // 2 - btnW_1.get_height() // 2))

        # Подсветка кнопок в меню
        if rects[btn].collidepoint(m_pos):
            pygame.draw.rect(screen, (255, 255, 153), rects[btn], round(HEIGHT / 240))


def choose_session(seed):
    """Выбор режима игры"""
    seedBar = seed
    menu = True
    while menu:
        screen.fill((0, 0, 0))

        # Картинка с лого
        screen.blit(pygame.transform.scale(LOGO, (RECT_GAME_WINDOW.w,
                                                  HEIGHT)), (0, 0))
        work_with_menu('choose_session')
        seedBar.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False, False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return True, True, seedBar.seed
                elif RECT_SETTINGS.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return True, False, False
                elif seedBar.rect.collidepoint(event.pos):
                    BTN_SOUND.play()
                    seedBar.activated = True
                else:
                    seedBar.activated = False
            elif event.type == pygame.KEYDOWN:
                if seedBar.activated:
                    seedBar.change_seed(event)

        pygame.display.flip()


def settings():
    class BtnSize:
        def __init__(self, x, y, title):
            self.image = pygame.transform.scale(load_image('cell_inv.png'), (round(WIDTH / 12.8), round(WIDTH / 12.8)))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
            self.dict = {'1080': '1920',
                         '480': '854',
                         '576': '1024',
                         '640': '1136',
                         '720': '1280'}
            self.title = title if title in self.dict.keys() else list(self.dict.keys())[0]

        def save(self):
            return self.title, self.dict[self.title]

        def draw(self):
            screen.blit(self.image, (self.rect.x, self.rect.y))
            btnW_1 = btn_font.render(self.title, True, pygame.Color("White"))
            screen.blit(btnW_1, (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                                 self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2))

            if self.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 255, 153), self.rect, round(HEIGHT / 240))

        def change_size(self):
            keys = list(self.dict.keys())
            index = keys.index(self.title)
            index = index + 1 if index + 1 <= len(keys) - 1 else 0
            self.title = keys[index]

    class Bar:
        def __init__(self, x, y, percent):
            self.image = pygame.transform.scale(BLANK_BAR, (round(RECT_MENU.w / 5 * 4), round(WIDTH / 25.6)))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
            self.percent = int(percent)

        def save(self):
            return str(self.percent)

        def draw(self):
            pygame.draw.rect(screen, (40, 40, 40), self.rect)
            pygame.draw.rect(screen, (153, 153, 153), (self.rect.x, self.rect.y,
                                                       round(self.rect.w * self.percent / 100), self.rect.h))
            screen.blit(self.image, (self.rect.x, self.rect.y))
            btnW_1 = btn_font.render(str(self.percent), True, pygame.Color("White"))
            screen.blit(btnW_1, (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                                 self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2))

            if self.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 255, 153), self.rect, round(HEIGHT / 240))

        def change_percent(self, pos):
            x, y = pos
            self.percent = round((x - self.rect.x) * 100 / self.rect.w)

    class Button:
        def __init__(self, x, y, title, key):
            self.image = pygame.transform.scale(load_image('cell_inv.png'), (round(WIDTH / 12.8), round(WIDTH / 12.8)))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
            self.title = title
            self.key = key.upper()
            self.choosed = False
            self.parent = None

        def save(self):
            return self.key.lower()

        def choose(self):
            self.choosed = not self.choosed

        def draw(self):
            screen.blit(self.image, (self.rect.x, self.rect.y))
            btnW_1 = btn_font.render(self.key, True, pygame.Color("White"))
            screen.blit(btnW_1, (self.rect[0] + self.rect[2] // 2 - btnW_1.get_width() // 2,
                                 self.rect[1] + self.rect[3] // 2 - btnW_1.get_height() // 2))
            if self.choosed:
                pygame.draw.rect(screen, (153, 255, 153), self.rect, round(HEIGHT / 240))
            elif self.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (255, 255, 153), self.rect, round(HEIGHT / 240))

        def change_btn(self, event):
            if event.key == pygame.K_LEFT:
                for i in self.parent:
                    if i.key == 'left':
                        i.key = ''
                self.key = 'left'
            elif event.key == pygame.K_RIGHT:
                for i in self.parent:
                    if i.key == 'right':
                        i.key = ''
                self.key = 'right'
            elif event.key == pygame.K_UP:
                for i in self.parent:
                    if i.key == 'up':
                        i.key = ''
                self.key = 'up'
            elif event.key == pygame.K_DOWN:
                for i in self.parent:
                    if i.key == 'down':
                        i.key = ''
                self.key = 'down'
            elif event.unicode.lower() in 'qwertyuiopasdfghjklzxcvbnm' and event.unicode != '':
                print(event.unicode)
                for i in self.parent:
                    if i.key == event.unicode.upper():
                        i.key = ''
                self.key = event.unicode.upper()

        def set_parent(self, parent):
            self.parent = parent

    bg = pygame.transform.scale(SETTINGS_BG, (round(GAME_WIN / 1.05), round(HEIGHT / 1.5)))
    bg_rect = bg.get_rect()
    #####
    # Buttons
    btnF = Button(bg_rect.x + WIDTH // 4.7, bg_rect.y + HEIGHT // 4, 'BTN_F', option_list[1])
    btnL = Button(bg_rect.x + WIDTH // 8, bg_rect.y + HEIGHT // 2.5, 'BTN_L', option_list[2])
    btnR = Button(bg_rect.x + WIDTH // 3.3, bg_rect.y + HEIGHT // 2.5, 'BTN_R', option_list[3])
    btnB = Button(bg_rect.x + WIDTH // 4.7, bg_rect.y + HEIGHT // 2.4, 'BTN_B', option_list[4])
    btnI = Button(bg_rect.x + GAME_WIN * 0.75, bg_rect.y + HEIGHT // 3.4, 'BTN_INTERACT', option_list[5])
    all_btns = [btnF, btnL, btnR, btnB, btnI]
    [i.set_parent(all_btns) for i in all_btns]
    # Sens Bar
    sensBar = Bar(bg_rect.x + GAME_WIN * 0.47, bg_rect.y + HEIGHT // 1.4, option_list[0])
    # Window Size
    btnWin = BtnSize(bg_rect.x + GAME_WIN * 0.16, bg_rect.y + HEIGHT // 1.5, option_list[7])
    #####
    all_obj = [sensBar]
    all_obj.extend(all_btns)
    all_obj.append(btnWin)
    menu = True
    choosed_btn = None
    while menu:
        screen.fill((0, 0, 0))

        # Картинка с лого
        screen.blit(pygame.transform.scale(LOGO, (RECT_GAME_WINDOW.w,
                                                  HEIGHT)), (0, 0))

        # Отрисовка элементов
        screen.blit(bg, (round(GAME_WIN / 2 - bg.get_width() / 2),
                         round(HEIGHT / 2 - bg.get_height() / 2)))
        [btn.draw() for btn in all_btns]
        sensBar.draw()
        btnWin.draw()

        work_with_menu('settings')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if RECT_PLAY.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return [obj.save() for obj in all_obj]
                elif RECT_SETTINGS.collidepoint(event.pos):
                    BTN_SOUND.play()
                    return [None]
                elif sensBar.rect.collidepoint(event.pos):
                    BTN_SOUND.play()
                    sensBar.change_percent(event.pos)
                elif btnWin.rect.collidepoint(event.pos):
                    BTN_SOUND.play()
                    btnWin.change_size()
                else:
                    choosed_btn = None
                    for btn in all_btns:
                        btn.choosed = False
                        if btn.rect.collidepoint(event.pos):
                            BTN_SOUND.play()
                            btn.choose()
                            choosed_btn = btn
            elif event.type == pygame.KEYDOWN:
                if choosed_btn is not None:
                    choosed_btn.change_btn(event)

        pygame.display.flip()
