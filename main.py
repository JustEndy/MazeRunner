from maze import Maze
import pygame
import random


def list_from_maze(rows, cols):
    m = Maze(rows, cols)
    world_map = []
    for row in range(rows + 3):
        row_line = []
        for col in range(cols + 3):
            row_line.append(0) if m.maze[row, col] else row_line.append(1)
        world_map.append(row_line)
    return world_map if 0 in world_map[1] else False


def generate_level(world_map):
    potential_start, potential_end = [], []
    for x in range(len(world_map)):
        for y in range(len(world_map[x])):
            if world_map[x][y]:
                cell = Wall(x, y)
                if x == 0:
                    if not world_map[x + 1][y]:
                        potential_start.append(cell)
                elif x == len(world_map) - 1:
                    if not world_map[x - 1][y]:
                        potential_end.append(cell)
                elif y != 0 and y != len(world_map[x]) - 1:
                    if random.random() <= 0.1:
                        cell.kill()
    start, end = random.choice(potential_start), random.choice(potential_end)
    x, y = start.rect.x, start.rect.y
    start.kill(), end.kill()
    Wall(-1, y // CELL_W)
    return x, y


####### SETUP ######
FPS = 60
SIZE = WIDTH, HEIGHT = 820, 820
CELL_W = 20
SPEED = 2
MAZE_S = 38
pygame.init()
pygame.display.set_caption('Лабиринт')
screen = pygame.display.set_mode(SIZE)
running = True
clock = pygame.time.Clock()
maze = False
while not maze:
    maze = list_from_maze(MAZE_S, MAZE_S)
####################
all_groups = pygame.sprite.Group()
walls_groups = pygame.sprite.Group()
doors_groups = pygame.sprite.Group()
player_group = pygame.sprite.Group()
####################


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, is_open=False, start=False):
        super().__init__(all_groups, doors_groups)
        self.image = pygame.Surface((20, 20))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = CELL_W * x, CELL_W * y
        ###
        self.is_open = is_open
        self.start = start

    def update(self, *args):
        wall = pygame.sprite.spritecollide(self, walls_groups, False)
        if wall and self.is_open:
            wall[0].kill()
        elif not wall and not self.is_open:
            Wall(self.rect.x // CELL_W, self.rect.y // CELL_W)
            self.kill()
        if self.start:
            if pygame.sprite.spritecollideany(self, player_group) is None:
                self.is_open = False


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_groups, walls_groups)
        self.image = pygame.Surface((20, 20))
        pygame.draw.rect(self.image, (150, 150, 150), (0, 0, 20, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = CELL_W * x, CELL_W * y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        x, y = pos
        super().__init__(all_groups, player_group)
        self.image = pygame.Surface((15, 15))
        pygame.draw.rect(self.image, (200, 200, 200), (0, 0, 15, 15))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + 2, y + 2

    def update(self):
        btns = pygame.key.get_pressed()
        x, y = self.rect.x, self.rect.y
        if btns[pygame.K_LEFT]:
            self.rect.x -= SPEED
        if btns[pygame.K_RIGHT]:
            self.rect.x += SPEED
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.x = x
        if btns[pygame.K_UP]:
            self.rect.y -= SPEED
        if btns[pygame.K_DOWN]:
            self.rect.y += SPEED
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.y = y


pos = generate_level(maze)
player = Player(pos)
Door(pos[0] // CELL_W, pos[1] // CELL_W, is_open=True, start=True)
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if player.rect.x + player.rect.w > WIDTH:
        all_groups.empty()
        walls_groups.empty()
        doors_groups.empty()
        player_group.empty()
        maze = False
        while not maze:
            maze = list_from_maze(MAZE_S, MAZE_S)
        pos = generate_level(maze)
        player = Player(pos)
        Door(pos[0] // CELL_W, pos[1] // CELL_W, is_open=True, start=True)
    all_groups.update()
    all_groups.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
