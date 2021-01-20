"""Модуль с физ. объектами, все сущности и блоки"""
from options import *
from collections import deque
import math
import random


class Meat(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__(all_groups, meat_group)
        self.player = player
        self.health = FPS * 3
        size = math.ceil(CELL_W * 0.6)
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (150, 35, 35), (0, 0, size, size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self, value=None):
        if self.health <= 0:
            self.player.meat.remove(self)
            self.kill()
        if value is not None:
            self.health += value


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, is_open=False):
        super().__init__(all_groups, doors_groups)
        self.color = (150, 75, 0)
        # Физический объект
        self.image = pygame.Surface((CELL_W, CELL_W))
        pygame.draw.rect(self.image, self.color, (0, 0, CELL_W, CELL_W))
        self.rect = self.image.get_rect()
        # Система координат
        self.rect.x, self.rect.y = CELL_W * x, CELL_W * y
        # Логика
        self.is_open = is_open

    @property
    def pos(self):
        return self.rect.x // CELL_W, self.rect.y // CELL_W


class ItemUse:
    """Логический объект, представитель предмета в инвенторе игрока"""
    def __init__(self, obj, id, *args):
        size = WIDTH // 10
        self.image = pygame.transform.scale(load_image(id + '.png'), (size, size))
        self.rect = self.image.get_rect()
        self.obj = obj
        self.id = id
        self.player = None
        self.args = args
        self.slot = None

    def use(self):
        # Статуэтки
        if self.id[:-2] == 'stat':
            p_x, p_y = self.player.pos
            cur_angle = self.player.angle

            v1_x, v1_y = self.args[0][0][0]
            v2_x, v2_y = self.args[0][0][1]
            v1_x, v1_y = v1_x // CELL_W, v1_y // CELL_W
            v2_x, v2_y = v2_x // CELL_W, v2_y // CELL_W

            sin_a = math.sin(cur_angle)
            cos_a = math.cos(cur_angle)

            for delta in range(CELL_W):
                x = p_x + delta * cos_a
                y = p_y + delta * sin_a
                if (v1_x, v1_y) == (int(x // CELL_W), int(y // CELL_W)) or \
                        (v2_x, v2_y) == (int(x // CELL_W), int(y // CELL_W)):
                    self.player.score_bar.update(1)
                    self.player.monster.change_speed()
                    self.slot.object = None
                    break
        elif self.id == 'chock':
            CHOCK_SOUND.play()
            self.player.stamina.stamina = FPS * 2
            self.slot.object = None
        elif self.id == 'bell':
            BELL_SOUND.play()
            x, y = self.player.x, self.player.y
            self.player.monster.set_custom_goal((x, y))
            self.slot.object = None
        elif self.id == 'pack':
            MEAT_SOUND.play()
            x, y = self.player.x, self.player.y
            self.player.meat.append(Meat(x, y, self.player))
            self.slot.object = None

    def set_player(self, player):
        self.player = player

    def set_cell(self, slot):
        self.slot = slot


class Item(pygame.sprite.Sprite):
    """Физ. объект, представитель предмета в физическом мире"""
    def __init__(self, pos, obj, id, *args):
        super().__init__(all_groups, item_group)
        x, y = pos
        size = math.ceil(CELL_W * 0.4)
        self.id = id
        self.args = args
        self.image = pygame.Surface((size, size))
        self.sprite_im = obj
        # В зависимости от объекта - своя текстура
        if id[:-2] == 'stat':
            pygame.draw.rect(self.image, (150, 150, 255), (0, 0, size, size))
        elif id == 'chock':
            pygame.draw.rect(self.image, (150, 35, 150), (0, 0, size, size))
        elif id == 'bell':
            pygame.draw.rect(self.image, (150, 150, 35), (0, 0, size, size))
        elif id == 'pack':
            pygame.draw.rect(self.image, (150, 35, 35), (0, 0, size, size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.contain = ItemUse(obj, id, args)

    def go_to_inventory(self):
        if self.id[:-2] != 'stat':
            self.args[0].amount.remove(self)
        return self.contain

    @property
    def pos(self):
        return self.rect.x, self.rect.y


class ItemSpawner:
    """Генератор предметов"""
    def __init__(self, w_map):
        self.w_map = w_map
        self.amount = list()
        self.sprites = {'chock': load_image('chock.png'),
                        'bell': load_image('bell.png'),
                        'pack': load_image('pack.png')}

    def spawn(self):
        if len(self.amount) < 3:
            if random.random() <= 0.1:
                c_x, c_y = 0, 0
                size = math.ceil(CELL_W * 0.4)
                while not self.w_map[c_x][c_y]:
                    c_x = random.randint(1, len(self.w_map) - 1)
                    c_y = random.randint(1, len(self.w_map[c_x]) - 1)
                x = c_x * CELL_W + random.randint(0, CELL_W - size)
                y = c_y * CELL_W + random.randint(0, CELL_W - size)
                id = random.choice(list(self.sprites.keys()))
                self.amount.append(Item((x, y), self.sprites[id], id, self))


class InventoryCell:
    def __init__(self, point, manager):
        self.image = pygame.transform.scale(load_image('cell_inv.png'), (WIDTH // 10, WIDTH // 10))
        self.rect = self.image.get_rect()
        self.object = None
        self.manager = manager
        self.is_current = False

        x, y = RECT_MENU.x + RECT_MENU.w // 2 - self.rect.w // 2, HEIGHT // 2
        if point == 1:
            self.rect.x, self.rect.y = x - self.rect.w // 1.5, y
        elif point == 2:
            self.rect.x, self.rect.y = x + self.rect.w // 1.5, y
        elif point == 3:
            self.rect.x, self.rect.y = x, y + self.rect.h * 1.25

    def use(self):
        if self.object is not None:
            self.object.use()

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        if self.object is not None:
            screen.blit(self.object.image, (self.rect.x + self.rect.w // 2 - self.object.rect.w // 2,
                                            self.rect.y + self.rect.h // 2 - self.object.rect.h // 2))
        if self.is_current:
            pygame.draw.rect(screen, (255, 255, 153), self.rect, round(HEIGHT / 240))


class InventoryManager:
    def __init__(self, parent):
        self.parent = parent
        self.slot_1 = InventoryCell(1, self)
        self.slot_2 = InventoryCell(2, self)
        self.slot_3 = InventoryCell(3, self)
        self.current = self.slot_1
        self.list = [self.slot_1, self.slot_2, self.slot_3]

    def use(self):
        self.current.use()

    def pickup(self, item):
        for slot in self.list:
            if slot.object is None:
                slot.object = item.go_to_inventory()
                slot.object.set_player(self.parent)
                slot.object.set_cell(slot)
                item.kill()
                break

    def draw(self):
        for slot in self.list:
            slot.draw()

    def update(self, value=None):
        if self.current is None:
            return
        self.current.is_current = False
        if value is None:
            btns = pygame.key.get_pressed()
            if btns[pygame.K_1]:
                self.current = self.list[0]
            elif btns[pygame.K_2]:
                self.current = self.list[1]
            elif btns[pygame.K_3]:
                self.current = self.list[2]
        else:
            index = self.list.index(self.current)
            index += value
            if index < 0:
                index = 2
            elif index > 2:
                index = 0
            self.current = self.list[index]
        self.current.is_current = True


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_groups, walls_groups)
        self.image = pygame.Surface((CELL_W, CELL_W))
        pygame.draw.rect(self.image, (150, 150, 150), (0, 0, CELL_W, CELL_W))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = CELL_W * x, CELL_W * y
        # Это просто стена, что вы от неё ожидаете :)


class SG(pygame.sprite.Sprite):
    """Объект мини-игры"""
    def __init__(self, pos, end_doors):
        x, y = pos
        size = math.ceil(CELL_W * 0.4)
        super().__init__()
        # Физ объект
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (255, 255, 153), (0, 0, size, size))
        self.rect = self.image.get_rect()
        # Координаты
        self.rect.x = x * CELL_W + randint(0, CELL_W - size)
        self.rect.y = y * CELL_W + randint(0, CELL_W - size)
        # Логика
        self.is_visible = False
        self.end_doors = end_doors

    def add_handler(self, obj):
        """Добавление ссылки на обработчик"""
        self.handler = obj
        self.sprite_im, self.id = self.handler.statue()

    def activated(self):
        """Вызывается при активации игроком"""
        self.handler.monster.set_custom_goal((self.rect.x, self.rect.y))
        self.handler.update_sg()
        Item((self.rect.x, self.rect.y), self.sprite_im, self.id, self.end_doors)
        self.kill()

    def update(self, activated=False):
        """Перенаправляем сигнал"""
        if activated:
            self.activated()


class SGHandler:
    """Объект для обработки всех мини-игр"""
    def __init__(self, sgs):
        self.list = sgs
        self.current_sg = random.choice(self.list)
        self.current_sg.add(all_groups, sg_group)
        self.current_sg.is_visible = True
        self.stat_sprites = {}
        for i in range(5):
            self.stat_sprites[f'stat_{i}'] = load_image(f'stat_{i}.png')
        for sg in self.list:
            sg.add_handler(self)

    def statue(self):
        id = random.choice(list(self.stat_sprites.keys()))
        return self.stat_sprites.pop(id), id

    def set_monster(self, m):
        self.monster = m

    def update_sg(self):
        """Меняем нынешнюю активную игру"""
        self.list.remove(self.current_sg)
        if self.list:
            self.current_sg = random.choice(self.list)
            self.current_sg.is_visible = True
            self.current_sg.add(all_groups, sg_group)


class Player(pygame.sprite.Sprite):
    """Объект игрока"""
    def __init__(self, pos, w_map, end_doors):
        x, y = pos
        size = math.ceil(CELL_W * 0.4)
        super().__init__(all_groups, player_group)
        # Физический объект
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (155, 255, 155), (0, 0, size, size))
        self.rect = self.image.get_rect()

        self.stamina = StaminaBar()
        # Система координат
        self.w_map = w_map
        self.angle = math.radians(0)
        self.x, self.y = x + 2 + CELL_W, y + 2
        self.rect.x, self.rect.y = x + 2 + CELL_W, y + 2
        self.fov = math.pi / 3
        self.delta_a = self.fov / NUM_RAYS
        # Логика
        self.end_doors = end_doors
        self.lost = False
        self.win = False
        self.is_interacting = False
        self.inventory = InventoryManager(self)
        self.item_spawner = ItemSpawner(w_map)
        self.score_bar = ScoreBar()
        self.monster = None
        self.sg_handler = None
        self.meat = []

    def draw_world(self):
        sg = self.sg_handler.current_sg
        entities = [Sprite(sg.sprite_im, True, sg.rect.topleft, 1.6, 0.4)]
        entities.extend([Sprite(item.sprite_im, True, item.pos, 2.8, 0.3) for item in self.item_spawner.amount])
        entities.append(Sprite(self.monster.sprites, False, (self.monster.x, self.monster.y), 0, 0.6,
                               self.monster.angle))
        if self.meat:
            for meat in self.meat:
                entities.append(Sprite(load_image('meat.png'), True, (meat.rect.x, meat.rect.y), 0.8, 0.4))

        world = list()
        walls = self.ray_casting()
        world.extend(walls)
        world.extend([sprite.locate(self, walls) for sprite in entities])

        for obj in sorted(world, key=lambda x: x[0], reverse=True):
            if obj[0]:
                dist, image, pos = obj
                screen.blit(image, pos)

        if self.monster.aggressive:
            text = pause_font.render('RUN', True, pygame.Color("Red"))
            screen.blit(text, (GAME_WIN // 2 - text.get_width() // 2, 0))

    def ray_casting(self):

        def mapping(a, b):
            return int(a // CELL_W * CELL_W), int(b // CELL_W * CELL_W)

        d = NUM_RAYS / (2 * math.tan(self.fov / 2))
        cur_angle = self.angle - self.fov / 2
        p_x, p_y = self.pos
        cp_x, cp_y = mapping(p_x, p_y)
        walls = []
        for ray in range(NUM_RAYS):
            sin_a = math.sin(cur_angle)
            cos_a = math.cos(cur_angle)

            # Вертикали
            x, dx = (cp_x + CELL_W, 1) if cos_a >= 0 else (cp_x, -1)
            for i in range(len(self.w_map)):
                delta_v = (x - p_x) / cos_a
                yv = p_y + delta_v * sin_a
                m = 1 if x < p_x else 0
                if self.w_map[int(x // CELL_W - m) % (MAZE_S * 2 + 1), int(yv // CELL_W) % (MAZE_S * 2 + 1)] != 1:
                    obj_v = self.w_map[int(x // CELL_W - m) % (MAZE_S * 2 + 1), int(yv // CELL_W) % (MAZE_S * 2 + 1)]
                    break
                x += dx * CELL_W
            # Горизонтали
            y, dy = (cp_y + CELL_W, 1) if sin_a >= 0 else (cp_y, -1)
            for i in range(len(self.w_map[cp_x // CELL_W])):
                delta_h = (y - p_y) / sin_a
                xh = p_x + delta_h * cos_a
                m = 1 if y < p_y else 0
                if self.w_map[int(xh // CELL_W) % (MAZE_S * 2 + 1), int(y // CELL_W - m) % (MAZE_S * 2 + 1)] != 1:
                    obj_h = self.w_map[int(xh // CELL_W) % (MAZE_S * 2 + 1), int(y // CELL_W - m) % (MAZE_S * 2 + 1)]
                    break
                y += dy * CELL_W

            # Проекция
            delta, offset, obj = (delta_v, yv, obj_v) if delta_v < delta_h else (delta_h, xh, obj_h)
            delta *= math.cos(cur_angle - self.angle)
            offset = offset / CELL_W - int(offset / CELL_W)
            h = min(int(1.5 * d * CELL_W / delta), HEIGHT * 3)
            wall_column = WALLS[obj].subsurface(offset * T_W, 0, 1, T_H)
            wall_column = pygame.transform.scale(wall_column, (SCALE, h))
            walls.append((delta, wall_column, (ray * SCALE, HEIGHT // 2 - h // 2)))

            cur_angle += self.delta_a

        # Блок зрения монстра
        m_x, m_y = self.monster.rect.center
        dy, dx = m_x - p_x, m_y - p_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        theta = math.atan2(dx, dy)
        gamma = theta - math.radians(self.monster.angle)
        if dy > 0 and 180 <= self.monster.angle <= 360 or dx < 0 and dy < 0:
            gamma += math.pi * 2
        delta_a = math.pi / 6 / NUM_RAYS
        delta_rays = int(gamma / delta_a)
        cur_ray = (delta_rays + NUM_RAYS // 2)
        distance *= math.cos(math.pi / 3 // 2 * cur_ray * delta_a)
        if 0 <= cur_ray <= NUM_RAYS - 1 and distance < walls[cur_ray][0]:
            self.monster.see_player()

        return walls

    @property
    def pos(self):
        return self.x + self.rect.w / 2, self.y + self.rect.w / 2

    def set_monster(self, m):
        self.monster = m

    def set_sg_handler(self, h):
        self.sg_handler = h

    def heartbeat(self, pos):
        """Проигрывает звук сердца, если рядом монстр"""
        x, y = pos
        x1, y1 = self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2
        length = math.sqrt((x1 - x)**2 + (y1 - y)**2) / MAZE_S * (HEIGHT / 720)
        if 5 < length <= 10:
            HEART_S.set_volume(1 - length / 10)
            HEART_S.play()
            pygame.time.set_timer(HEARTBEAT, round(HEART_S.get_length() * 100) * 10)
        elif length <= 5:
            HEART_S.set_volume(1 - length / 10)
            HEART_S.play()
            pygame.time.set_timer(HEARTBEAT, round(HEART_S.get_length() * 100) * 5)
        else:
            pygame.time.set_timer(HEARTBEAT, 100)

    def draw_inventory(self):
        """Отрисовывает все данные и инвентарь игрока"""
        # Фон
        screen.blit(pygame.transform.scale(GAME_BG, (RECT_MENU.w, RECT_MENU.h)), (RECT_MENU.x, RECT_MENU.y))

        # Ячейки инвентаря
        self.inventory.draw()

        # Текст (Заменить потом на нормальный)
        self.score_bar.draw()
        self.stamina.draw()

    def change_angle(self, mouse_pos):
        """Меняем угол направления взгляда"""
        delta_mouse_pos = mouse_pos[0] - CENTER[0]
        self.angle += (0.0008 * SENSITIVITY / 100) * delta_mouse_pos
        self.angle = (2 * math.pi + self.angle) % (2 * math.pi) if self.angle >= 0 else self.angle % (2 * math.pi)

    def update(self):
        """Передвижение"""
        btns = pygame.key.get_pressed()
        x, y = self.rect.x, self.rect.y
        cos, sin = math.sin(self.angle), \
                   math.cos(self.angle)

        if not any(btns):
            self.stamina.update(0.5)
        else:
            if pygame.key.get_mods() != 4097:
                self.stamina.update(0.25)

        if btns[pygame.K_UP] or btns[BTN_F]:
            if pygame.key.get_mods() == 4097 and self.stamina.stamina > 0:
                self.y += cos * SPEED * 1.2
                self.x += sin * SPEED * 1.2
                self.stamina.update(-1)
            else:
                self.y += cos * SPEED * 0.6
                self.x += sin * SPEED * 0.6
        if btns[pygame.K_DOWN] or btns[BTN_B]:
            if pygame.key.get_mods() == 4097 and self.stamina.stamina > 0:
                self.y -= cos * SPEED
                self.x -= sin * SPEED
                self.stamina.update(-1)
            else:
                self.y -= cos * SPEED * 0.6
                self.x -= sin * SPEED * 0.6
        if btns[pygame.K_LEFT] or btns[BTN_L]:
            self.y -= sin * SPEED * 0.6
            self.x += cos * SPEED * 0.6
        if btns[pygame.K_RIGHT] or btns[BTN_R]:
            self.y += sin * SPEED * 0.6
            self.x -= cos * SPEED * 0.6
        self.rect.y = round(self.y)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.y = y
            self.y = y
        if pygame.sprite.spritecollideany(self, doors_groups):
            if not self.end_doors[0].is_open:
                self.rect.y = y
                self.y = y
            else:
                self.win = True
        self.rect.x = round(self.x)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.x = x
            self.x = x
        if pygame.sprite.spritecollideany(self, doors_groups):
            if not self.end_doors[0].is_open:
                self.rect.x = x
                self.x = x
            else:
                self.win = True
        # Взаимодействие
        sg = pygame.sprite.spritecollide(self, sg_group, False)
        if sg:
            self.is_interacting = True
            if btns[BTN_INTERACT]:
                sg[0].update(activated=True)
        else:
            self.is_interacting = False

        item = pygame.sprite.spritecollide(self, item_group, False)
        if item:
            self.inventory.pickup(item[0])

    def interact_text(self):
        final = pygame.Surface((WIDTH, HEIGHT))
        final.fill((0, 0, 0))
        final.set_colorkey((0, 0, 0))
        text = btn_font.render(f'Press {INTERACT_UNICODE} to use.', False, (1, 1, 1))
        delta = text.get_height() * 2
        pygame.draw.rect(final, (255, 255, 255), (HEIGHT // 2 - text.get_width() // 2 - 5,
                                                  HEIGHT // 2 - text.get_height() // 2 - 5 + delta,
                                                  text.get_width() + 10, text.get_height() + 10))
        final.blit(text, (HEIGHT // 2 - text.get_width() // 2,
                          HEIGHT // 2 - text.get_height() // 2 + delta))
        return final


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, player, coef=0.4):
        x, y = pos
        super().__init__(all_groups, enemy_group)
        # Визуал
        self.sprites = []
        self.cut_sheet(load_image('demon.png'), 8, 1)
        self.angle = 0
        # Физический объект
        size = math.ceil(CELL_W * 0.5)
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (225, 175, 175), (0, 0, size, size))
        self.rect = self.image.get_rect()
        # Всё, что связано с передвижением и системой координат
        self.x, self.y = x + 2 - CELL_W, y + 2
        self.rect.x, self.rect.y = x + 2 - CELL_W, y + 2
        self.cell_x, self.cell_y = x // CELL_W, y // CELL_W
        self.player = player
        self.path = []
        self.w_map = player.w_map
        # Сосотояние монстра, Агрессия/Пассивность
        self.aggressive = False
        self.agro_timer = 0
        # Скорость
        self.speed_coef = coef
        self.speed = SPEED * self.speed_coef

    def cut_sheet(self, sheet, columns, rows):
        rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                           sheet.get_height() // rows)

        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                self.sprites.append(sheet.subsurface(pygame.Rect(
                    frame_location, rect.size)))

    def see_player(self):
        """Увидеть игрока"""
        self.agro_timer = 5 * FPS

    def change_speed(self):
        """Изменение скорости монстра в зависимости от переменной Score"""
        self.speed_coef = 0.4 + self.player.score_bar.score * 0.1
        if self.aggressive:
            self.speed = SPEED * self.speed_coef
        else:
            self.speed = SPEED * self.speed_coef * 0.8

    def change_behave(self, agro_timer=None):
        """Изменение поведения Агрессивное/Пассивное, влияет на цель монстра"""
        if agro_timer is None:
            self.aggressive = not self.aggressive
        elif agro_timer:
            self.aggressive = True
        else:
            self.aggressive = False
        self.path = []

    def random_passive(self):
        """Возвращает рандомную точку внутри лабиринта"""
        while True:
            x, y = randint(1, len(self.w_map) - 1), randint(1, len(self.w_map[0]) - 1)
            if self.w_map[x][y]:
                return x, y

    def set_custom_goal(self, pos):
        """Ручная установка цели монстра"""
        goal = pos[0] // CELL_W, pos[1] // CELL_W
        self.path = self.get_path(self.bfs(goal))
        self.speed = SPEED * self.speed_coef * 1.75

    def update_goal(self):
        """Обновляем цель монстра Игрок/Точка в лабиринте"""
        if self.aggressive:
            goal = self.player.rect.x // CELL_W, self.player.rect.y // CELL_W
            self.path = self.get_path(self.bfs(goal))
            self.speed = SPEED * self.speed_coef * 2
        else:
            if len(self.path) <= 1:
                self.speed = SPEED * self.speed_coef
                goal = self.random_passive()
                self.path = self.get_path(self.bfs(goal))

    def update(self):
        """Передвижение"""
        if self.agro_timer == 5 * FPS:
            self.change_behave(True)
        elif self.agro_timer == 0:
            self.change_behave(False)
        self.agro_timer -= 1 if self.agro_timer - 1 >= -1 else 0

        if pygame.sprite.spritecollideany(self, player_group):
            self.player.lost = True
            return
        if len(self.path) <= 1:
            x, y = self.rect.x, self.rect.y
            if self.player.x > x:
                self.x += self.speed
            elif self.player.x < x:
                self.x -= self.speed
            self.rect.x = int(self.x)
            if pygame.sprite.spritecollideany(self, walls_groups):
                self.rect.x = x
                self.x = x
            if self.player.y > y:
                self.y += self.speed
            elif self.player.y < y:
                self.y -= self.speed
            self.rect.y = int(self.y)
            if pygame.sprite.spritecollideany(self, walls_groups):
                self.rect.y = y
                self.y = y
            return
        x, y = self.rect.x, self.rect.y
        x1, y1 = self.rect.x + self.rect.w // 2, self.rect.y + self.rect.w // 2
        x2, y2 = self.path[1]

        if x1 // CELL_W < x2:
            self.angle = 180
        elif x2 < x1 // CELL_W:
            self.angle = 0
        elif y1 // CELL_W < y2:
            self.angle = 270
        elif y2 < y1 // CELL_W:
            self.angle = 90
        if (self.cell_x, self.cell_y) == (x2, y2):
            self.path.pop(0)
            return

        x2, y2 = x2 * CELL_W + 2 + self.rect.w // 2, y2 * CELL_W + 2 + self.rect.w // 2
        if x1 < x2:
            self.x += self.speed
        elif x1 >= x2:
            self.x -= self.speed
        self.rect.x = int(self.x)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.x = x
            self.x = x
        meat = pygame.sprite.spritecollide(self, meat_group, False)
        if meat:
            meat[0].update(-1)
            self.rect.x = x
            self.x = x
        if y1 < y2:
            self.y += self.speed
        elif y1 > y2:
            self.y -= self.speed
        self.rect.y = int(self.y)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.y = y
            self.y = y
        if meat:
            meat[0].update(-1)
            self.rect.y = y
            self.y = y
        self.cell_x, self.cell_y = self.rect.x // CELL_W, self.rect.y // CELL_W

    def get_path(self, args):
        """Возвращает список координат, путь монстра"""
        start, goal, visited = args
        if goal not in visited.keys():
            return []
        path = [goal]
        cell = visited[goal]
        while True:
            if cell is None:
                break
            path.append(cell)
            cell = visited[cell]
        return path[::-1]

    def bfs(self, goal):
        """Алгоритм поиска пути в ширину"""
        start = self.cell_x, self.cell_y

        def get_next_nodes(self, x, y):
            maze = self.w_map
            ways = [-1, 0], [0, -1], [1, 0], [0, 1]
            ans = []
            for dy, dx in ways:
                if 0 < y + dy < len(maze) - 1 and 0 < x + dx < len(maze[0]) - 1 and maze[dx + x][dy + y] == 1:
                    ans.append((x + dx, y + dy))
            return ans

        graph = {}
        for y in range(1, len(maze) - 1):
            for x in range(1, len(maze[y]) - 1):
                if self.w_map[x][y]:
                    graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(self, x, y)
        x, y = self.cell_x, self.cell_y
        graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(self, x, y)
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = graph[cur_node]
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return start, goal, visited