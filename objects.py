"""Модуль с физ. объектами, все сущности и блоки"""
from options import *
from collections import deque
import math
import random


class Meat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_groups, meat_group)
        self.health = FPS * 3
        size = math.ceil(CELL_W * 0.4)
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (150, 35, 35), (0, 0, size, size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self, value=None):
        if self.health <= 0:
            self.kill()
        if value is not None:
            self.health += value


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, is_open=False, start=False):
        super().__init__(all_groups, doors_groups)
        self.color = (0, 0, 0) if start else (150, 75, 0)
        # Физический объект
        self.image = pygame.Surface((CELL_W, CELL_W))
        pygame.draw.rect(self.image, self.color, (0, 0, CELL_W, CELL_W))
        self.rect = self.image.get_rect()
        # Система координат
        self.rect.x, self.rect.y = CELL_W * x, CELL_W * y
        # Логика
        self.is_open = is_open
        self.start = start

    def update(self):
        """Логика двери, закрытие/открытие"""
        wall = pygame.sprite.spritecollide(self, walls_groups, False)
        if wall and self.is_open:
            wall[0].kill()
            pygame.draw.rect(self.image, (0, 0, 0), (0, 0, CELL_W, CELL_W))
        elif not wall and not self.is_open:
            Wall(self.rect.x // CELL_W, self.rect.y // CELL_W)
            if self.start:
                self.image.set_colorkey(self.color)
            else:
                pygame.draw.rect(self.image, self.color, (0, 0, CELL_W, CELL_W))
        if self.start:
            if not self.is_open:
                self.color = (150, 150, 150)
            if pygame.sprite.spritecollideany(self, player_group) is None:
                self.is_open = False


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
            x, y = self.player.x, self.player.y
            angle = self.player.angle
            d_x, d_y = ((x + self.player.rect.width // 2 + 0.5 * math.sin(angle)) // CELL_W,
                        (y + self.player.rect.width // 2 + 0.5 * math.cos(angle)) // CELL_W)
            v_x, v_y = self.args[0][0]
            v_x, v_y = v_x // CELL_W, v_y // CELL_W
            if (v_x, v_y) == (int(d_x), int(d_y)):
                self.player.score_bar.update(1)
                self.player.monster.change_speed()
                self.slot.object = None
        elif self.id == 'chock':
            CHOCK_SOUND.play()
            self.player.stamina.stamina = FPS * 3
            self.slot.object = None
        elif self.id == 'bell':
            BELL_SOUND.play()
            x, y = self.player.x, self.player.y
            self.player.monster.set_custom_goal((x, y))
            self.slot.object = None
        elif self.id == 'pack':
            MEAT_SOUND.play()
            x, y = self.player.x, self.player.y
            Meat(x, y)
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
        # В зависимости от объекта - своя текстура
        if id[:-2] == 'stat':
            self.args = args
            self.image = pygame.Surface((size, size))
            pygame.draw.rect(self.image, (150, 150, 255), (0, 0, size, size))
        elif id == 'chock':
            self.args = args
            self.image = pygame.Surface((size, size))
            pygame.draw.rect(self.image, (150, 35, 150), (0, 0, size, size))
        elif id == 'bell':
            self.args = args
            self.image = pygame.Surface((size, size))
            pygame.draw.rect(self.image, (150, 150, 35), (0, 0, size, size))
        elif id == 'pack':
            self.args = args
            self.image = pygame.Surface((size, size))
            pygame.draw.rect(self.image, (150, 35, 35), (0, 0, size, size))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.contain = ItemUse(obj, id, args)

    def go_to_inventory(self):
        if self.id[:-2] != 'stat':
            self.args[0].amount -= 1
        return self.contain


class ItemSpawner:
    """Генератор предметов"""
    def __init__(self, w_map):
        self.w_map = w_map
        self.amount = 0
        self.sprites = {'chock': load_image('chock.png'),
                        'bell': load_image('bell.png'),
                        'pack': load_image('pack.png')}

    def spawn(self):
        if self.amount < 3:
            if random.random() <= 0.1:
                c_x, c_y = 0, 0
                size = math.ceil(CELL_W * 0.4)
                while not self.w_map[c_x][c_y]:
                    c_x = random.randint(1, len(self.w_map) - 1)
                    c_y = random.randint(1, len(self.w_map[c_x]) - 1)
                x = c_x * CELL_W + random.randint(0, CELL_W - size)
                y = c_y * CELL_W + random.randint(0, CELL_W - size)
                id = random.choice(list(self.sprites.keys()))
                Item((x, y), self.sprites[id], id, self)
                self.amount += 1


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
    def __init__(self, pos, end_door):
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
        self.end_door = end_door

    def add_handler(self, obj):
        """Добавление ссылки на обработчик"""
        self.handler = obj

    def activated(self):
        """Вызывается при активации игроком"""
        self.handler.monster.set_custom_goal((self.rect.x, self.rect.y))
        self.handler.update_sg()
        obj, id = self.handler.statue()
        Item((self.rect.x, self.rect.y), obj, id, self.end_door)
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
    def __init__(self, pos, w_map):
        x, y = pos
        size = math.ceil(CELL_W * 0.25)
        super().__init__(all_groups, player_group)
        # Физический объект
        self.image = pygame.Surface((size, size))
        pygame.draw.rect(self.image, (155, 255, 155), (0, 0, size, size))
        self.rect = self.image.get_rect()

        self.stamina = StaminaBar()
        # Система координат
        self.w_map = w_map
        self.angle = math.radians(0)
        self.x, self.y = x + 2, y + 2
        self.rect.x, self.rect.y = x + 2, y + 2
        self.fov = math.pi / 3
        self.delta_a = self.fov / NUM_RAYS
        # Логика
        self.lost = False
        self.is_interacting = False
        self.inventory = InventoryManager(self)
        self.item_spawner = ItemSpawner(w_map)
        self.score_bar = ScoreBar()
        self.monster = None
        self.sg_handler = None

    def ray_casting(self):

        def mapping(a, b):
            return a // CELL_W * CELL_W, b // CELL_W * CELL_W

        d = NUM_RAYS / (2 * math.tan(self.fov / 2))
        cur_angle = self.angle - self.fov / 2
        p_x, p_y = self.pos
        cp_x, cp_y = mapping(p_x, p_y)
        for ray in range(NUM_RAYS):
            sin_a = math.sin(cur_angle)
            cos_a = math.cos(cur_angle)

            # Вертикали
            x, dx = (cp_x + CELL_W, 1) if cos_a >= 0 else (cp_x, -1)
            for i in range(len(self.w_map)):
                delta_v = (x - p_x) / cos_a
                y = p_y + delta_v * sin_a
                m = 1 if x < p_x else 0
                if not self.w_map[int(x // CELL_W - m) % (MAZE_S * 2 + 1), int(y // CELL_W) % (MAZE_S * 2 + 1)]:
                    break
                x += dx * CELL_W
            # Вертикали
            y, dy = (cp_y + CELL_W, 1) if sin_a >= 0 else (cp_y, -1)
            for i in range(len(self.w_map[cp_x // CELL_W])):
                delta_h = (y - p_y) / sin_a
                x = p_x + delta_h * cos_a
                m = 1 if y < p_y else 0
                if not self.w_map[int(x // CELL_W) % (MAZE_S * 2 + 1), int(y // CELL_W - m) % (MAZE_S * 2 + 1)]:
                    break
                y += dy * CELL_W

            # Проекция
            delta = delta_v if delta_v < delta_h else delta_h
            h = d * CELL_W * 2 / delta / math.cos(self.angle - cur_angle)
            c = 255 / (1 + delta ** 2 * 0.0002)
            pygame.draw.rect(screen, (c, c // 2, c // 3), (ray * SCALE, HEIGHT // 2 - h // 2, SCALE, h))
            cur_angle += self.delta_a

    @property
    def pos(self):
        return self.rect.center

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
                self.y += cos * SPEED
                self.x += sin * SPEED
                self.stamina.update(-1)
            else:
                self.y += cos * SPEED * 0.6
                self.x += sin * SPEED * 0.6
        if btns[pygame.K_DOWN] or btns[BTN_B]:
            self.y -= cos * SPEED * 0.5
            self.x -= sin * SPEED * 0.5
        if btns[pygame.K_LEFT] or btns[BTN_L]:
            self.y -= sin * SPEED * 0.6
            self.x += cos * SPEED * 0.6
        if btns[pygame.K_RIGHT] or btns[BTN_R]:
            self.y += sin * SPEED * 0.6
            self.x -= cos * SPEED * 0.6
        self.rect.y = math.ceil(self.y)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.y = y
            self.y = y
        self.rect.x = math.ceil(self.x)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.x = x
            self.x = x
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
        # Физический объект
        size = math.ceil(CELL_W * 0.75)
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
        # Скорость
        self.speed_coef = coef
        self.speed = SPEED * self.speed_coef

    def change_speed(self):
        """Изменение скорости монстра в зависимости от переменной Score"""
        self.speed_coef = 0.4 + self.player.score_bar.score * 0.1
        if self.aggressive:
            self.speed = SPEED * self.speed_coef * 2
        else:
            self.speed = SPEED * self.speed_coef

    def change_behave(self):
        """Изменение поведения Агрессивное/Пассивное, влияет на цель монстра"""
        self.aggressive = not self.aggressive
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