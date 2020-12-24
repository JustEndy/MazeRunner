from options import *
from collections import deque


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
        self.x, self.y = x + 2, y + 2
        self.rect.x, self.rect.y = x + 2, y + 2

    def update(self):
        btns = pygame.key.get_pressed()
        x, y = self.rect.x, self.rect.y
        if btns[pygame.K_LEFT]:
            self.x -= SPEED
        if btns[pygame.K_RIGHT]:
            self.x += SPEED
        self.rect.x = round(self.x)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.x = x
            self.x = x
        if btns[pygame.K_UP]:
            self.y -= SPEED
        if btns[pygame.K_DOWN]:
            self.y += SPEED
        self.rect.y = round(self.y)
        if pygame.sprite.spritecollideany(self, walls_groups):
            self.rect.y = y
            self.y = y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, player, w_map):
        x, y = pos
        super().__init__(all_groups, enemy_group)
        self.image = pygame.Surface((15, 15))
        pygame.draw.rect(self.image, (225, 175, 175), (0, 0, 15, 15))
        self.rect = self.image.get_rect()
        self.x, self.y = x + 2, y + 2
        self.rect.x, self.rect.y = x + 2, y + 2
        self.cell_x, self.cell_y = x // CELL_W, y // CELL_W
        self.player = player
        self.path = False
        self.w_map = w_map

    def update(self, path=False):
        if path:
            self.path = self.get_path(self.bfs())
        if self.path and len(self.path) > 1:
            x1, y1 = self.rect.x, self.rect.y
            x2, y2 = self.path[1]
            x2, y2 = x2 * CELL_W + 2, y2 * CELL_W + 2
            if x1 < x2:
                self.x += SPEED
            elif x1 > x2:
                self.x -= SPEED
            if y1 < y2:
                self.y += SPEED
            elif y1 > y2:
                self.y -= SPEED
        self.rect.x, self.rect.y = round(self.x), round(self.y)
        self.cell_x, self.cell_y = self.rect.x // CELL_W, self.rect.y // CELL_W

    def get_path(self, args):
        start, goal, visited = args
        if goal not in visited.keys():
            return False
        path = [goal]
        cell = visited[goal]
        while True:
            if cell is None:
                break
            path.append(cell)
            cell = visited[cell]
        return path[::-1]

    def bfs(self):
        """Алгоритм поиска пути в ширину"""
        start = self.cell_x, self.cell_y
        goal = self.player.rect.x // CELL_W, self.player.rect.y // CELL_W

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